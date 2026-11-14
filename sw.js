// Service Worker – Referee Supervision Suite
//
// Release-Regel: Bei jeder Änderung an css/ oder js/ die Nummer ?v= in index.html erhöhen
// (alle Links gleich). Der pre-commit-Hook in .githooks/ prüft das.
// CACHE_NAME nur ändern, wenn sich der Aufbau des Caches in dieser Datei ändert.
//
// Grundsatz: index.html und die CSS-/JS-Dateien, die sie einbindet, sind ein Paket.
// Ein neues Paket wird nur vollständig übernommen, darum bekommt eine Seite nie
// CSS/JS einer anderen Version.
const CACHE_NAME = 'referee-supervision-sw1';
const NETWORK_TIMEOUT_MS = 3000;

const SCOPE = self.registration.scope;
const PAGE = new URL('index.html', SCOPE).href;
const STATUS_KEY = new URL('__sw-status', SCOPE).href;

// Dateien ohne Versionsnummer: aus dem Cache, im Hintergrund aktualisiert.
const STATIC_ASSETS = [
  'manifest.json',
  'logo-evz.svg',
  'icons/icon.svg',
  'icons/icon-192.png',
  'icons/icon-512.png',
  'icons/icon-maskable-512.png',
  'icons/apple-touch-icon.png'
].map((p) => new URL(p, SCOPE).href);

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const isVersionedAsset = (url) => /\.(css|js)$/.test(new URL(url).pathname) && new URL(url).pathname !== new URL('sw.js', SCOPE).pathname;
const shortName = (url) => url.replace(SCOPE, '');

// Lokale CSS-/JS-Dateien, die eine Seite per <link href> oder <script src> einbindet.
function assetsOf(html) {
  const urls = new Set();
  const re = /<(?:link|script)\b[^>]*?\b(?:href|src)="([^"]+\.(?:css|js)(?:\?[^"]*)?)"/gi;
  for (const m of html.matchAll(re)) {
    const u = new URL(m[1], PAGE);
    if (u.origin === self.location.origin) urls.add(u.href);
  }
  return [...urls];
}

async function fetchOk(url) {
  // 'no-cache': der Browser fragt immer beim Server nach (bei unveränderter Datei nur kurz, 304).
  const res = await fetch(url, { cache: 'no-cache' });
  if (!res.ok) throw new Error(`${shortName(url)}: HTTP ${res.status}`);
  // Inhalt sofort ganz lesen: Das gibt die Verbindung frei. Sonst blockieren sich bei
  // HTTP/1.1 (max. 6 Verbindungen) die vielen gleichzeitig offenen Antworten gegenseitig.
  const body = await res.arrayBuffer();
  return new Response(body, { status: res.status, statusText: res.statusText, headers: res.headers });
}

// Status für den Hinweis in der App (z. B. Update blockiert), bleibt im Cache gespeichert.
async function setStatus(status) {
  const cache = await caches.open(CACHE_NAME);
  await cache.put(STATUS_KEY, new Response(JSON.stringify(status), { headers: { 'Content-Type': 'application/json' } }));
  const clients = await self.clients.matchAll({ type: 'window' });
  clients.forEach((c) => c.postMessage({ type: 'sw-status', ...status }));
}

async function getStatus() {
  const res = await (await caches.open(CACHE_NAME)).match(STATUS_KEY);
  return res ? res.json() : {};
}

// Holt Seite + CSS/JS aus dem Netz und übernimmt sie nur als vollständiges Paket.
// Ergebnis: 'neu', 'gleich' oder 'abgelehnt'. Wirft bei Netzfehler (dann bleibt alles, wie es war).
async function updatePackage() {
  const pageRes = await fetchOk(PAGE);
  const html = await pageRes.clone().text();
  const urls = assetsOf(html);
  const fetched = await Promise.all(urls.map(async (u) => [u, await fetchOk(u)]));

  const cache = await caches.open(CACHE_NAME);
  const toStore = [];
  const changedSameVersion = [];
  for (const [u, res] of fetched) {
    const old = await cache.match(u);
    if (!old) { toStore.push([u, res]); continue; }
    const [a, b] = await Promise.all([old.text(), res.clone().text()]);
    if (a !== b) changedSameVersion.push(shortName(u));
  }

  // Gleiche Adresse (gleiches ?v=), anderer Inhalt: Nummer wurde nicht erhöht.
  // Paket nicht übernehmen, sonst könnten alte und neue Dateien gemischt werden.
  if (changedSameVersion.length) {
    console.warn('Update blockiert – Version (?v=) nicht erhöht:', changedSameVersion.join(', '));
    await setStatus({ blocked: true, files: changedSameVersion });
    return 'abgelehnt';
  }

  const oldPage = await cache.match(PAGE);
  const oldHtml = oldPage ? await oldPage.text() : null;
  const pageChanged = oldHtml !== html;

  // Zuerst alle Dateien, zuletzt die Seite: erst dann zeigt die Seite auf das neue Paket.
  for (const [u, res] of toStore) await cache.put(u, res);
  if (pageChanged) {
    await cache.put(PAGE, pageRes);
    // Aufräumen: nur das neue und das vorherige Paket behalten
    // (eine gerade startende Seite der alten Version braucht ihre Dateien noch).
    const keep = new Set([...urls, ...(oldHtml ? assetsOf(oldHtml) : [])]);
    for (const req of await cache.keys()) {
      if (isVersionedAsset(req.url) && !keep.has(req.url)) await cache.delete(req);
    }
  }
  const status = await getStatus();
  if (status.blocked) await setStatus({ blocked: false });
  return pageChanged || toStore.length ? 'neu' : 'gleich';
}

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await Promise.all(STATIC_ASSETS.map(async (u) => cache.put(u, await fetchOk(u))));
    await updatePackage();
  })());
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((names) => Promise.all(names.filter((n) => n !== CACHE_NAME).map((n) => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

// Seite: Paket aus dem Netz, wenn es innert NETWORK_TIMEOUT_MS vollständig da ist,
// sonst das gespeicherte Paket. Das Laden läuft im Hintergrund weiter (nächster Start).
async function servePage(event) {
  const cache = await caches.open(CACHE_NAME);
  const update = updatePackage();
  event.waitUntil(update.catch((err) => console.warn('Update nicht möglich:', err.message)));

  const cached = await cache.match(PAGE);
  if (!cached) {
    // Noch nichts gespeichert: auf das Netz warten.
    try {
      await update;
      const page = await cache.match(PAGE);
      if (page) return page;
    } catch (e) { /* unten direkt aus dem Netz */ }
    return fetch(event.request);
  }

  const inTime = await Promise.race([
    update.then(() => true, () => false),
    sleep(NETWORK_TIMEOUT_MS).then(() => false)
  ]);
  return inTime ? ((await cache.match(PAGE)) || cached) : cached;
}

// CSS/JS: genau die Datei mit dieser Adresse (inkl. ?v=) aus dem Cache.
async function serveVersioned(req) {
  return (await caches.match(req)) || fetch(req);
}

// Icons, Logo, Manifest: sofort aus dem Cache, im Hintergrund nachführen.
async function serveStatic(event) {
  const cache = await caches.open(CACHE_NAME);
  const url = event.request.url;
  const hit = await cache.match(url);
  const refresh = fetchOk(url).then(async (res) => { await cache.put(url, res.clone()); return res; });
  if (hit) {
    event.waitUntil(refresh.catch(() => {}));
    return hit;
  }
  return refresh.catch(() => Response.error());
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  const path = url.origin + url.pathname;

  if (req.mode === 'navigate') {
    if (path === SCOPE || path === PAGE) event.respondWith(servePage(event));
    return;
  }
  if (isVersionedAsset(req.url)) { event.respondWith(serveVersioned(req)); return; }
  if (STATIC_ASSETS.includes(path)) event.respondWith(serveStatic(event));
});

// Die App fragt beim Start nach dem Status (für den Hinweis im Badge).
self.addEventListener('message', (event) => {
  if (event.data === 'sw-status?' && event.source) {
    event.waitUntil(getStatus().then((s) => event.source.postMessage({ type: 'sw-status', ...s })));
  }
});
