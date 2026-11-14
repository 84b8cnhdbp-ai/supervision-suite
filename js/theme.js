// Darstellung: 'auto' (folgt dem System), 'light' oder 'dark'.
// Wird im <head> geladen, damit beim Start nichts kurz hell aufblitzt.
const THEME_KEY = 'referee_theme_preference';

function getThemePref() {
  try {
    const p = localStorage.getItem(THEME_KEY);
    return p === 'light' || p === 'dark' ? p : 'auto';
  } catch (e) {
    return 'auto';
  }
}

function isDarkTheme() {
  const p = getThemePref();
  return p === 'dark' || (p === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches);
}

function applyTheme() {
  const p = getThemePref();
  if (p === 'auto') document.documentElement.removeAttribute('data-theme');
  else document.documentElement.setAttribute('data-theme', p);
}

applyTheme();
