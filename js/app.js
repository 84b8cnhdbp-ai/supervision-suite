// Start der App und Service Worker
// (aus index.html ausgelagert, Etappe 1 – Code unverändert)

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js')
      .then(reg => {
        const badge = document.getElementById('pwaBadge');
        if (badge) badge.innerText = "● PWA Ready";
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
