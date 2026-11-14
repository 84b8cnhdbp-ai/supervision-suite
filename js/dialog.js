// Eigene Fenster und Hinweise (ersetzen alert, confirm und prompt)
//
// zeigeFenster(optionen) öffnet ein Fenster (<dialog>, mit Esc schliessbar, Hintergrund gesperrt) und
// liefert ein Promise mit { knopf, eingabe }: knopf = Wert des gewählten Knopfs (Esc = abbruchWert),
// eingabe = Inhalt des Eingabefelds (falls vorhanden).
//   titel, text       Überschrift und Erklärung
//   liste             [{ text, aktion }] – antippbare Einträge; aktion läuft, nachdem das Fenster zu ist
//   eingabe           { wert, label } – einzeiliges Eingabefeld; Enter = Hauptknopf
//   knoepfe           [{ text, wert, art: 'normal' | 'primaer' | 'gefahr', fokus: true }]
//   abbruchWert       Wert bei Esc (Standard null)

let fensterNr = 0;

function zeigeFenster({ titel, text, liste, eingabe, knoepfe = [], abbruchWert = null }) {
  return new Promise((resolve) => {
    const nr = ++fensterNr;
    const dlg = document.createElement('dialog');
    dlg.className = 'fenster';
    dlg.setAttribute('aria-labelledby', `fenster-titel-${nr}`);

    const h = document.createElement('h2');
    h.className = 'fenster-titel';
    h.id = `fenster-titel-${nr}`;
    h.textContent = titel;
    dlg.appendChild(h);

    if (text) {
      const p = document.createElement('p');
      p.className = 'fenster-text';
      p.textContent = text;
      dlg.appendChild(p);
    }

    let ergebnis = { knopf: abbruchWert, eingabe: null };
    let nachher = null;   // Aktion eines Listeneintrags, läuft nach dem Schliessen
    const schliessen = (wert) => {
      ergebnis = { knopf: wert, eingabe: feld ? feld.value : null };
      dlg.close();
    };

    if (liste && liste.length) {
      const ul = document.createElement('ul');
      ul.className = 'fenster-liste';
      liste.forEach((eintrag) => {
        const li = document.createElement('li');
        const b = document.createElement('button');
        b.type = 'button';
        b.className = 'fenster-eintrag';
        b.textContent = eintrag.text;
        b.addEventListener('click', () => { nachher = eintrag.aktion; schliessen(abbruchWert); });
        li.appendChild(b);
        ul.appendChild(li);
      });
      dlg.appendChild(ul);
    }

    let feld = null;
    if (eingabe) {
      feld = document.createElement('input');
      feld.type = 'text';
      feld.className = 'fenster-eingabe';
      feld.value = eingabe.wert || '';
      feld.setAttribute('aria-label', eingabe.label || titel);
      feld.autocomplete = 'off';
      feld.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          const haupt = knoepfe.find((k) => k.art === 'primaer');
          if (haupt) schliessen(haupt.wert);
        }
      });
      dlg.appendChild(feld);
    }

    const reihe = document.createElement('div');
    reihe.className = 'fenster-knoepfe';
    let fokus = feld;
    knoepfe.forEach((k) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'fenster-knopf' + (k.art ? ' fenster-knopf-' + k.art : '');
      b.textContent = k.text;
      b.addEventListener('click', () => schliessen(k.wert));
      if (k.fokus) fokus = b;
      reihe.appendChild(b);
    });
    dlg.appendChild(reihe);

    dlg.addEventListener('cancel', () => { ergebnis = { knopf: abbruchWert, eingabe: null }; });
    dlg.addEventListener('close', () => {
      dlg.remove();
      resolve(ergebnis);
      // nach dem Schliessen setzt der Browser den Fokus zurück; erst danach die Aktion ausführen
      if (nachher) setTimeout(nachher, 0);
    });

    document.body.appendChild(dlg);
    dlg.showModal();
    if (fokus) {
      fokus.focus();
      if (fokus === feld) feld.select();
    }
  });
}

// Ja/Nein-Frage. „Abbrechen“ ist vorgewählt (Enter löscht nichts). gefahr: Hauptknopf rot.
async function bestaetigen({ titel, text, ja, gefahr = false }) {
  const r = await zeigeFenster({
    titel, text, abbruchWert: false,
    knoepfe: [
      { text: t('dlg_cancel'), wert: false, fokus: true },
      { text: ja, wert: true, art: gefahr ? 'gefahr' : 'primaer' }
    ]
  });
  return r.knopf === true;
}

// Eingabe eines Textes; liefert den Text oder null (Abbrechen / Esc).
async function eingeben({ titel, text, wert, ok }) {
  const r = await zeigeFenster({
    titel, text, eingabe: { wert, label: titel }, abbruchWert: null,
    knoepfe: [
      { text: t('dlg_cancel'), wert: null },
      { text: ok || t('dlg_ok'), wert: 'ok', art: 'primaer' }
    ]
  });
  return r.knopf === 'ok' ? r.eingabe : null;
}

// Meldung mit einem OK-Knopf.
function melden({ titel, text }) {
  return zeigeFenster({ titel, text, knoepfe: [{ text: t('dlg_ok'), wert: true, art: 'primaer', fokus: true }] });
}

// Kurzer Hinweis unten (verschwindet von selbst). art: 'info' | 'ok' | 'fehler'
function zeigeToast(text, art = 'info', dauer = 3000) {
  let box = document.getElementById('toastBox');
  if (!box) {
    box = document.createElement('div');
    box.id = 'toastBox';
    box.className = 'toast-box';
    box.setAttribute('role', 'status');
    box.setAttribute('aria-live', 'polite');
    document.body.appendChild(box);
  }
  const el = document.createElement('div');
  el.className = 'toast toast-' + art;
  el.textContent = text;
  box.appendChild(el);
  requestAnimationFrame(() => el.classList.add('sichtbar'));
  setTimeout(() => {
    el.classList.remove('sichtbar');
    setTimeout(() => el.remove(), 300);
  }, dauer);
  return el;
}

// Zu einem Feld springen: in die Mitte scrollen, Fokus setzen, kurz hervorheben.
function springeZuFeld(feld, hervorheben) {
  if (!feld) return;
  const ruhig = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const rahmen = hervorheben || feld;
  rahmen.scrollIntoView({ block: 'center', behavior: ruhig ? 'auto' : 'smooth' });
  feld.focus({ preventScroll: true });
  rahmen.classList.remove('feld-hervorheben');
  void rahmen.offsetWidth;   // Animation neu starten
  rahmen.classList.add('feld-hervorheben');
  setTimeout(() => rahmen.classList.remove('feld-hervorheben'), 2500);
}
