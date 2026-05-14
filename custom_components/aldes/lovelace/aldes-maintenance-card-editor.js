import { LitElement, html } from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

const OPTIONS = [
  ["modem_entity", "Modem Entity (Pending Commands)"],
  ["connectivity_entity", "Connectivity Sensor (API Health)"],
];

class AldesMaintenanceCardEditor extends LitElement {
  static get properties() {
    return { hass: {}, config: {} };
  }

  setConfig(config) {
    this.config = config;
  }

  render() {
    if (!this.hass || !this.config) return html``;

    return html`
      <div class="card-config">
        ${OPTIONS.map(
          ([key, label]) => html`
            <ha-entity-picker
              .hass="${this.hass}"
              .value="${this.config[key] || ""}"
              .configValue="${key}"
              @value-changed="${this._valueChanged}"
              label="${label}"
              allow-custom-entity
            ></ha-entity-picker>
          `
        )}
      </div>
    `;
  }

  _valueChanged(ev) {
    const key = ev.currentTarget.configValue || ev.target.configValue;
    if (!key) return;
    const config = { ...this.config, [key]: ev.detail.value || undefined };
    this.config = config;
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config } }));
  }
}
customElements.define("aldes-maintenance-card-editor", AldesMaintenanceCardEditor);
