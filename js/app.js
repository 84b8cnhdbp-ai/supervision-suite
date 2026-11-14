// Start der App und Service Worker

// Badge oben: Offline-Status. „Update blockiert“ bleibt stehen, solange der Service Worker
// ein Update ablehnt (Version ?v= nicht erhöht); dazu einmal pro Start ein Hinweis.
// (Auf dem iPad ist die Konsole nicht sichtbar.)
let swBlockiert = false;
let swToastGezeigt = false;

function zeigeBadge() {
  const badge = document.getElementById('pwaBadge');
  if (!badge) return;
  if (badge.dataset.status === 'update') { badge.innerText = t('badge_update'); return; }
  badge.dataset.status = swBlockiert ? 'blockiert' : 'bereit';
  badge.innerText = swBlockiert ? t('badge_blocked') : t('badge_ready');
  if (swBlockiert) badge.title = t('badge_blocked_detail', { dateien: (swBlockiert.files || []).join(', ') });
  else badge.removeAttribute('title');
}

function handleSwStatus(e) {
  const d = e.data || {};
  if (d.type !== 'sw-status') return;
  swBlockiert = d.blocked ? d : false;
  zeigeBadge();
  if (d.blocked && !swToastGezeigt) {
    swToastGezeigt = true;
    zeigeToast(t('toast_blocked'), 'fehler', 6000);
  }
}

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.addEventListener('message', handleSwStatus);
  navigator.serviceWorker.startMessages();
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js')
      .then(reg => {
        const badge = document.getElementById('pwaBadge');
        zeigeBadge();
        if (navigator.serviceWorker.controller) navigator.serviceWorker.controller.postMessage('sw-status?');
        const hadController = !!navigator.serviceWorker.controller;
        navigator.serviceWorker.addEventListener('controllerchange', () => {
          if (!hadController || !badge) return;
          badge.dataset.status = 'update';
          badge.innerText = t('badge_update');
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
