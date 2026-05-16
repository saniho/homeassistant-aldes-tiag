import { LitElement, html } from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

class AldesPlanningCardEditor extends LitElement {
  static get properties() {
    return { hass: {}, config: {} };
  }

  setConfig(config) {
    this.config = config;
  }

  render() {
    if (!this.hass || !this.config) return html``;

    const allPlanning = Object.keys(this.hass.states)
      .filter((eid) => {
        const state = this.hass.states[eid];
        return state && state.attributes && "planning_data" in state.attributes;
      })
      .sort();

    const configured = this.config.entities || [];
    const discovered = configured.length === 0;

    return html`
      <div class="card-config">
        <p style="margin-bottom:12px;">
          <label>
            <input type="checkbox" ?checked="${discovered}" @change="${this._toggleDiscovery}" />
            Découverte automatique
          </label>
        </p>

        ${discovered
          ? html`
            <p style="color: var(--secondary-text-color); font-size: 0.9em;">
              ${allPlanning.length} planning(s) trouvé(s) automatiquement
            </p>
          `
          : html`
            <p style="margin-bottom:8px; font-weight:600;">Sélectionnez les plannings :</p>
            ${allPlanning.map((eid) => {
              const state = this.hass.states[eid];
              const label = state?.attributes?.friendly_name || eid;
              const selected = configured.includes(eid);
              return html`
                <p style="margin:4px 0;">
                  <label>
                    <input type="checkbox" ?checked="${selected}" @change="${(ev) => this._toggleEntity(eid, ev.target.checked)}" />
                    ${label}
                  </label>
                </p>
              `;
            })}
            ${allPlanning.length === 0
              ? html`<p style="color: var(--secondary-text-color);">Aucune entité planning trouvée</p>`
              : ""}
          `}
      </div>
    `;
  }

  _toggleDiscovery(ev) {
    const discovered = ev.target.checked;
    const config = { ...this.config };
    if (discovered) {
      delete config.entities;
    } else {
      config.entities = [];
    }
    this.config = config;
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config } }));
  }

  _toggleEntity(eid, add) {
    const current = this.config.entities || [];
    const config = { ...this.config, entities: add ? [...current, eid] : current.filter((e) => e !== eid) };
    this.config = config;
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config } }));
  }
}
if (!customElements.get("aldes-planning-card-editor")) {
  customElements.define("aldes-planning-card-editor", AldesPlanningCardEditor);
}
