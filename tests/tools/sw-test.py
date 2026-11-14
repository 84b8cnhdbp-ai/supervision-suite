"""Service-Worker-Test: startet die App in Headless Chrome und spielt Netz-Szenarien durch.

Der Testserver markiert jede ausgelieferte Seite, CSS- und JS-Datei mit der simulierten Version
("alt" = Stand im Ordner, "neu" = simuliertes nächstes Release mit ?v= + 1). So fällt sofort auf,
wenn eine Seite gemischte Versionen bekommt.

Aufruf:  python3 tests/tools/sw-test.py                  (alle Szenarien)
         python3 tests/tools/sw-test.py langsam-alles     (einzelne Szenarien)
         python3 tests/tools/sw-test.py --uebergang-von 67b77e9   (zusätzlich: Wechsel von einem alten Stand)
Abbruchcode 1 bei Fehlern.
"""
import http.server, json, os, re, shutil, subprocess, sys, tempfile, threading, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from werkzeug import CHROME, git_stand  # noqa: E402
ARGS = sys.argv[1:]
ALT = None
if '--uebergang-von' in ARGS:
    i = ARGS.index('--uebergang-von'); ALT = git_stand(ARGS[i + 1]); del ARGS[i:i + 2]
ALL = ['online-update', 'offline', 'langsam-alles', 'langsam-css-js', 'langsam-gleich', 'ohne-erhoehung']
M = {}
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s, *a, **k): super().__init__(*a, directory=M.get('dir', REPO), **k)
    def do_POST(s):
        body = s.rfile.read(int(s.headers['Content-Length'])).decode()
        if s.path == '/__mode':
            m = json.loads(body)
            if m.pop('neu', False): M['dir'] = REPO
            M.update(m)
        else: M['result'] = json.loads(body); M['done'].set()
        s.send_response(200); s.end_headers()
    def do_GET(s):
        p = s.path.split('?')[0]
        if p == '/__sw-test':
            return s.send_bytes(open(os.path.join(HERE, 'sw-test.html'), 'rb').read(), 'text/html')
        if not M.get('online', True): s.close_connection = True; return
        is_asset = p.endswith('.css') or (p.endswith('.js') and p != '/sw.js')
        is_page = p in ('/', '/index.html')
        delay = M.get('delayAll', 0) + (M.get('delayAssets', 0) if is_asset else 0)
        if delay and p != '/sw.js': time.sleep(delay)
        if not (is_asset or is_page): return super().do_GET()
        fp = os.path.join(M.get('dir', REPO), 'index.html' if p == '/' else p.lstrip('/'))
        data = open(fp, 'rb').read(); lab = M.get('label', 'alt')
        if p.endswith('.css'): data += f'\n:root{{--sw-test:{lab}}}\n'.encode(); ct = 'text/css'
        elif p.endswith('.js'): data += f'\n;(window.__swv=window.__swv||[]).push("{lab}:{p}");\n'.encode(); ct = 'text/javascript'
        else:
            data = data.replace(b'</head>', f'<meta name="sw-test" content="{lab}"></head>'.encode()); ct = 'text/html'
            if M.get('bump'): data = re.sub(rb'\?v=(\d+)"', lambda m: b'?v=%d"' % (int(m.group(1)) + 1), data)
        s.send_bytes(data, ct)
    def send_bytes(s, data, ct):
        s.send_response(200); s.send_header('Content-Type', ct); s.send_header('Content-Length', str(len(data))); s.end_headers(); s.wfile.write(data)
    def end_headers(s):
        if os.environ.get('HTTPCACHE') != '1': s.send_header('Cache-Control', 'no-store')
        super().end_headers()
    def log_message(s, *a): pass
    def handle(s):
        try: super().handle()
        except (BrokenPipeError, ConnectionResetError): pass
fehler = 0
for sc in (ARGS or (ALL + (['uebergang-v6'] if ALT else []))):
    M.clear(); M['done'] = threading.Event()
    if sc == 'uebergang-v6': M['dir'] = ALT
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H); port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    prof = tempfile.mkdtemp()
    p = subprocess.Popen([CHROME, '--headless=new', f'--user-data-dir={prof}', '--window-size=1300,1000', '--no-first-run',
        f'http://127.0.0.1:{port}/__sw-test?s={sc}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ok = M['done'].wait(150); p.kill(); p.wait(); srv.shutdown(); shutil.rmtree(prof, ignore_errors=True)
    print(f'\n== {sc} ' + ('' if ok else 'TIMEOUT'))
    for e in M.get('result', []):
        if 'error' in e: print('  FEHLER', e['error']); fehler += 1; continue
        probleme = []
        if not (e['einheitlich'] and e['vollstaendig']): probleme.append('Version')
        if e.get('sw') is False: probleme.append('nicht vom Service Worker geliefert')
        if '+5 s' in e['label'] and e['ms'] > 4500: probleme.append('zu langsam')
        flag = 'XX ' if probleme else 'ok '
        if flag == 'XX ': fehler += 1
        print(f"  {flag}{e['label']:<38} {e['ms']:>5} ms | HTML {e['html']} CSS {e['css']} JS {e['js']} | {'einheitlich' if e['einheitlich'] else 'GEMISCHT'}, {'vollständig' if e['vollstaendig'] else 'UNVOLLSTÄNDIG'} | Badge: {e['badge']}" + (f"  <-- {', '.join(probleme)}" if probleme else ''))
print(f'\n{fehler} Fehler'); sys.exit(1 if fehler else 0)
