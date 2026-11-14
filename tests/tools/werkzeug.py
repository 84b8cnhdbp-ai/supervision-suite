"""Gemeinsame Hilfen für die Testwerkzeuge (nur Python-Standardbibliothek + Google Chrome).

- Server: lokaler HTTP-Server für einen Ordner (ohne HTTP-Cache), plus eigene Routen.
- Browser: Headless Chrome mit eigener, leerer Profil-Ablage, gesteuert über das
  Chrome DevTools Protocol (CDP) – Fenstergrösse, Dark Mode, Druck, JavaScript, Bilder.
- git_stand(): einen Commit/Branch (z. B. main) in einen temporären Ordner auspacken.
"""
import base64
import http.server
import json
import os
import shutil
import socket
import struct
import subprocess
import tempfile
import threading
import time
import urllib.request

HIER = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HIER, '..', '..'))
FIXTURES = os.path.join(REPO, 'tests', 'fixtures')
ERGEBNISSE = os.path.join(HIER, 'ergebnisse')   # steht in .gitignore
CHROME = os.environ.get('CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')


# ---------------------------------------------------------------- Server

def server(wurzel, routen=None):
    """Startet einen Server für den Ordner `wurzel`. `routen`: {pfad: (content_type, bytes)}.
    /tests/fixtures/ kommt immer aus dem aktuellen Repo (gleiche Testdaten für alle Stände)."""
    routen = routen or {}

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(s, *a, **k):
            super().__init__(*a, directory=wurzel, **k)

        def translate_path(s, path):
            p = path.split('?')[0]
            if p.startswith('/tests/fixtures/'):
                return os.path.join(FIXTURES, p[len('/tests/fixtures/'):])
            return super().translate_path(path)

        def do_GET(s):
            p = s.path.split('?')[0]
            if p in routen:
                ct, data = routen[p]
                s.send_response(200)
                s.send_header('Content-Type', ct)
                s.send_header('Content-Length', str(len(data)))
                s.end_headers()
                s.wfile.write(data)
                return
            super().do_GET()

        def end_headers(s):
            s.send_header('Cache-Control', 'no-store')
            super().end_headers()

        def log_message(s, *a):
            pass

    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    srv.basis = f'http://127.0.0.1:{srv.server_address[1]}'
    return srv


def git_stand(ref):
    """Packt den Stand `ref` (Branch, Tag, Commit) in einen temporären Ordner aus."""
    ziel = tempfile.mkdtemp(prefix='stand-')
    arch = subprocess.run(['git', '-C', REPO, 'archive', ref], check=True, capture_output=True).stdout
    subprocess.run(['tar', '-x', '-C', ziel], input=arch, check=True)
    return ziel


# ---------------------------------------------------------------- Browser (CDP)

class _WebSocket:
    """Minimaler WebSocket-Client (nur Text, ausreichend für CDP)."""

    def __init__(self, url):
        rest = url.split('://', 1)[1]
        hostport, pfad = rest.split('/', 1)
        host, port = hostport.split(':')
        self.sock = socket.create_connection((host, int(port)), timeout=120)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f'GET /{pfad} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\n'
                           f'Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
        antwort = b''
        while b'\r\n\r\n' not in antwort:
            antwort += self.sock.recv(4096)
        if b' 101 ' not in antwort.split(b'\r\n')[0]:
            raise RuntimeError('WebSocket abgelehnt: ' + antwort.split(b'\r\n')[0].decode())
        self.puffer = antwort.split(b'\r\n\r\n', 1)[1]

    def _lies(self, n):
        while len(self.puffer) < n:
            teil = self.sock.recv(1 << 16)
            if not teil:
                raise ConnectionError('WebSocket geschlossen')
            self.puffer += teil
        d, self.puffer = self.puffer[:n], self.puffer[n:]
        return d

    def senden(self, text):
        daten = text.encode()
        kopf = bytearray([0x81])
        n = len(daten)
        if n < 126:
            kopf.append(0x80 | n)
        elif n < 65536:
            kopf += bytes([0x80 | 126]) + struct.pack('>H', n)
        else:
            kopf += bytes([0x80 | 127]) + struct.pack('>Q', n)
        maske = os.urandom(4)
        self.sock.sendall(bytes(kopf) + maske + bytes(b ^ maske[i % 4] for i, b in enumerate(daten)))

    def empfangen(self):
        teile = []
        while True:
            b1, b2 = self._lies(2)
            n = b2 & 0x7F
            if n == 126:
                n = struct.unpack('>H', self._lies(2))[0]
            elif n == 127:
                n = struct.unpack('>Q', self._lies(8))[0]
            nutz = self._lies(n)
            op = b1 & 0x0F
            if op == 0x9:            # Ping -> ignorieren
                continue
            teile.append(nutz)
            if b1 & 0x80:
                return b''.join(teile).decode()


class Browser:
    """Headless Chrome mit leerem Profil. Mit `with Browser() as b:` verwenden."""

    def __enter__(self):
        self.fehler = []
        self.profil = tempfile.mkdtemp(prefix='chrome-')
        s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
        self.proc = subprocess.Popen([CHROME, '--headless=new', f'--user-data-dir={self.profil}',
                                      f'--remote-debugging-port={port}', '--no-first-run', '--no-default-browser-check',
                                      '--hide-scrollbars', '--force-device-scale-factor=1', 'about:blank'],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ziel = None
        for _ in range(100):
            try:
                liste = json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json/list', timeout=1))
                ziel = next((t for t in liste if t.get('type') == 'page'), None)
                if ziel:
                    break
            except OSError:
                pass
            time.sleep(0.1)
        if not ziel:
            raise RuntimeError('Chrome startet nicht (Pfad: %s)' % CHROME)
        self.ws = _WebSocket(ziel['webSocketDebuggerUrl'])
        self.nr = 0
        self.befehl('Page.enable')
        self.befehl('Runtime.enable')
        return self

    def __exit__(self, *a):
        self.proc.kill(); self.proc.wait()
        shutil.rmtree(self.profil, ignore_errors=True)

    def befehl(self, methode, **params):
        self.nr += 1
        nr = self.nr
        self.ws.senden(json.dumps({'id': nr, 'method': methode, 'params': params}))
        while True:
            m = json.loads(self.ws.empfangen())
            if m.get('id') == nr:
                if 'error' in m:
                    raise RuntimeError(f"{methode}: {m['error']}")
                return m.get('result', {})
            if m.get('method') == 'Runtime.exceptionThrown':
                d = m['params']['exceptionDetails']
                self.fehler.append(d.get('exception', {}).get('description') or d.get('text'))
            if m.get('method') == 'Runtime.consoleAPICalled' and m['params']['type'] in ('error', 'warning'):
                self.fehler.append(' '.join(str(a.get('value', a.get('description', ''))) for a in m['params']['args']))

    def fenster(self, breite, hoehe, farbschema='light', druck=False):
        self.befehl('Emulation.setDeviceMetricsOverride', width=breite, height=hoehe, deviceScaleFactor=1, mobile=False)
        self.befehl('Emulation.setEmulatedMedia', media='print' if druck else '',
                    features=[{'name': 'prefers-color-scheme', 'value': farbschema},
                              {'name': 'prefers-reduced-motion', 'value': 'reduce'}])

    def oeffnen(self, url, warten=0.6):
        self.befehl('Page.navigate', url=url)
        for _ in range(200):
            if self.js('document.readyState') == 'complete':
                break
            time.sleep(0.05)
        time.sleep(warten)

    def js(self, ausdruck):
        """Wertet JavaScript aus (Promises werden abgewartet) und gibt den Wert als Python-Objekt zurück."""
        r = self.befehl('Runtime.evaluate', expression=ausdruck, awaitPromise=True, returnByValue=True)
        if 'exceptionDetails' in r:
            raise RuntimeError('JS-Fehler: ' + r['exceptionDetails'].get('exception', {}).get('description', str(r['exceptionDetails'])))
        return r['result'].get('value')

    def bild(self, datei, ganze_seite=True):
        clip = None
        if ganze_seite:
            m = self.befehl('Page.getLayoutMetrics')['cssContentSize']
            clip = {'x': 0, 'y': 0, 'width': m['width'], 'height': m['height'], 'scale': 1}
        r = self.befehl('Page.captureScreenshot', format='png', captureBeyondViewport=ganze_seite, **({'clip': clip} if clip else {}))
        with open(datei, 'wb') as f:
            f.write(base64.b64decode(r['data']))

    def pdf(self, datei):
        r = self.befehl('Page.printToPDF', printBackground=True, preferCSSPageSize=True)
        with open(datei, 'wb') as f:
            f.write(base64.b64decode(r['data']))


# Leere Seite auf dem gleichen Ursprung, um localStorage vor dem App-Start zu setzen.
LEER = ('text/html', b'<!doctype html><meta charset="utf-8"><title>leer</title>')


def daten_setzen(b, basis, spiel=True, theme=None, sprache=None):
    """Setzt Kader und (optional) das Beispielspiel im localStorage, bevor die App lädt."""
    b.oeffnen(basis + '/__leer', warten=0)
    b.js("""(async () => {
      localStorage.clear();
      const kader = await (await fetch('/tests/fixtures/beispiel-kader.json')).json();
      localStorage.setItem('referee_kader', JSON.stringify(kader.schiedsrichter));
      %s
      %s
      %s
    })()""" % (
        "localStorage.setItem('referee_multi_supervision_data', JSON.stringify(await (await fetch('/tests/fixtures/beispiel-spiel.json')).json()));" if spiel else '',
        f"localStorage.setItem('referee_theme_preference', {json.dumps(theme)});" if theme else '',
        f"localStorage.setItem('referee_lang_preference', {json.dumps(sprache)});" if sprache else ''))
