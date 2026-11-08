// Panoul din bara laterală: încarcă pagina (Casa 3D sau configuratorul NTC)
// într-un iframe. Pagina folosește direct sesiunea Home Assistant a ferestrei
// părinte, deci nu are nevoie de token.
const MENU = 'M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z';

class Casa3DPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._narrow = false;
  }

  set hass(hass) { this._hass = hass; this._updateBar(); }
  set narrow(narrow) { this._narrow = narrow; this._updateBar(); }
  set route(_route) { /* nefolosit */ }
  set panel(panel) { this._panel = panel; this._render(); }

  _render() {
    const cfg = (this._panel && this._panel.config) || {};
    if (!cfg.page || cfg.page === this._page) return;
    this._page = cfg.page;
    this.shadowRoot.innerHTML = `
      <style>
        /* Containerul panoului din HA nu are înălțime fixă: panoul ocupă ecranul vizibil
           (fără zonele sigure, pe care HA le adaugă ca margini). */
        :host { display: flex; flex-direction: column; overflow: hidden; background: var(--primary-background-color);
          height: calc(100vh - env(safe-area-inset-top, 0px) - env(safe-area-inset-bottom, 0px));
          height: calc(100dvh - env(safe-area-inset-top, 0px) - env(safe-area-inset-bottom, 0px)); }
        .bar { display: none; align-items: center; gap: 4px; flex: none; box-sizing: border-box;
          height: var(--header-height, 56px); padding: 0 4px;
          background: var(--app-header-background-color, var(--primary-color)); color: var(--app-header-text-color, #fff);
          border-bottom: var(--app-header-border-bottom, none); }
        .bar.show { display: flex; }
        button { width: 48px; height: 48px; border: 0; border-radius: 50%; background: none; color: inherit; cursor: pointer;
          display: grid; place-items: center; }
        button:hover { background: rgba(127, 127, 127, .15); }
        svg { width: 24px; height: 24px; fill: currentColor; }
        .title { font-size: 20px; font-weight: 400; margin-left: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        iframe { flex: 1 1 auto; width: 100%; border: 0; display: block; }
      </style>
      <div class="bar">
        <button type="button" aria-label="Meniu"><svg viewBox="0 0 24 24"><path d="${MENU}"></path></svg></button>
        <div class="title"></div>
      </div>
      <iframe allow="fullscreen"></iframe>`;
    this.shadowRoot.querySelector('.title').textContent = cfg.title || '';
    this.shadowRoot.querySelector('iframe').src = cfg.page;
    this.shadowRoot.querySelector('button').addEventListener('click', () => {
      this.dispatchEvent(new Event('hass-toggle-menu', { bubbles: true, composed: true }));
    });
    this._updateBar();
  }

  // Bara cu butonul de meniu apare doar când bara laterală e ascunsă (telefon).
  _updateBar() {
    const bar = this.shadowRoot.querySelector('.bar');
    if (!bar) return;
    const hidden = !!(this._hass && this._hass.dockedSidebar === 'always_hidden');
    bar.classList.toggle('show', !!this._narrow || hidden);
  }
}

if (!customElements.get('casa-3d-panel')) customElements.define('casa-3d-panel', Casa3DPanel);
