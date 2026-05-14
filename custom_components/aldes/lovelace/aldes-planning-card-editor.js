import { LitElement, html } from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

const MODE_LABELS = { A: "Chauffage Prog A", B: "Chauffage Prog B", C: "Climatisation Prog C", D: "Climatisation Prog D" };

class AldesPlanningCardEditor extends LitElement {
  static get properties() {
    return { hass: {}, config: {} };
  }

  setConfig(config) {
    this.config = config;
  }

  render() {
    if (!this.hass || !this.config) return html``;

    const allPlanning = Object.keys(this.hass.states).filter(
      (eid) =>
        eid.startsWith("sensor.aldes_") &&
        (eid.includes("_planning_heating_") || eid.includes("_planning_cooling_"))
    ).sort();

    const configured = this.config.entities || [];
    const discovered = configured.length === 0;

    return html`
      <div class="card-config">
        <ha-formfield label="Mode découverte automatique">
          <ha-switch
            .checked="${discovered}"
            @change="${this._toggleDiscovery}"
          ></ha-switch>
        </ha-formfield>

        ${discovered
          ? html`
            <div style="color: var(--secondary-text-color); font-size: 0.9em; padding: 8px 0;">
              Découverte auto : ${allPlanning.length} planning(s) trouvé(s)
            </div>
          `
          : html`
            ${allPlanning.map((eid) => {
              const label = eid.replace(/^sensor\./, "");
              const selected = configured.includes(eid);
              return html`
                <ha-formfield label="${label}">
                  <ha-checkbox
                    .checked="${selected}"
                    @change="${(ev) => this._toggleEntity(eid, ev.target.checked)}"
                  ></ha-checkbox>
                </ha-formfield>
              `;
            })}
            ${allPlanning.length === 0
              ? html`<div style="color: var(--secondary-text-color);">Aucune entité planning trouvée</div>`
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
customElements.define("aldes-planning-card-editor", AldesPlanningCardEditor);
