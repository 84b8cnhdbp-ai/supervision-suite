// Start der App und Service Worker
// (aus index.html ausgelagert, Etappe 1; Hinweis bei blockiertem Update ergänzt)

// Hinweis im Badge, wenn der Service Worker ein Update ablehnt, weil ?v= nicht erhöht wurde.
// (Auf dem iPad ist die Konsole nicht sichtbar.)
function handleSwStatus(e) {
  const d = e.data || {};
  if (d.type !== 'sw-status' || !d.blocked) return;
  const badge = document.getElementById('pwaBadge');
  if (!badge) return;
  badge.innerText = "⚠ Update blockiert – Version nicht erhöht";
  badge.title = "Auf dem Server gibt es geänderte Dateien mit gleicher Versionsnummer (?v=). "
    + "Die bisherige Version bleibt aktiv. Betroffen: " + (d.files || []).join(', ');
}

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.addEventListener('message', handleSwStatus);
  navigator.serviceWorker.startMessages();
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js')
      .then(reg => {
        const badge = document.getElementById('pwaBadge');
        if (badge) badge.innerText = "● PWA Ready";
        if (navigator.serviceWorker.controller) navigator.serviceWorker.controller.postMessage('sw-status?');
        const hadController = !!navigator.serviceWorker.controller;
        navigator.serviceWorker.addEventListener('controllerchange', () => {
          if (!hadController || !badge) return;
          badge.innerText = "⟳ Neue Version – tippen zum Laden";
          badge.style.cursor = "pointer";
          badge.onclick = () => location.reload();
        });
      })
      .catch(err => {
        console.log('SW registration error:', err);
      });
  });
}

window.addEventListener('DOMContentLoaded', initApp);
