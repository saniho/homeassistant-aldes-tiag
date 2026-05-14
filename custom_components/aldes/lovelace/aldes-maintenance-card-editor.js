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
          .value="${this.config.modem_entity}"
          .configValue="${'modem_entity'}"
          @value-changed="${this._valueChanged}"
          label="Modem Entity"
          allow-custom-entity
        ></ha-entity-picker>
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${this.config.connectivity_entity}"
          .configValue="${'connectivity_entity'}"
          @value-changed="${this._valueChanged}"
          label="Connectivity Sensor (API Health)"
          allow-custom-entity
        ></ha-entity-picker>
      </div>
    `;
  }

  _valueChanged(ev) {
    const config = { ...this.config, [ev.target.configValue]: ev.detail.value };
    this.config = config;
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config } }));
  }
}
customElements.define("aldes-maintenance-card-editor", AldesMaintenanceCardEditor);
