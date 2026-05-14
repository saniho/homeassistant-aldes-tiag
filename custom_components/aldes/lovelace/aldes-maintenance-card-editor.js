import { LitElement, html } from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

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
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${this.config.modem_entity || ""}"
          @value-changed="${(ev) => this._valueChanged(ev, "modem_entity")}"
          label="Modem Entity (Pending Commands)"
          allow-custom-entity
        ></ha-entity-picker>
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${this.config.connectivity_entity || ""}"
          @value-changed="${(ev) => this._valueChanged(ev, "connectivity_entity")}"
          label="Connectivity Sensor (API Health)"
          allow-custom-entity
        ></ha-entity-picker>
      </div>
    `;
  }

  _valueChanged(ev, key) {
    const val = ev.detail && ev.detail.value ? ev.detail.value : "";
    const config = { ...this.config, [key]: val };
    this.config = config;
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config } }));
  }
}
customElements.define("aldes-maintenance-card-editor", AldesMaintenanceCardEditor);
