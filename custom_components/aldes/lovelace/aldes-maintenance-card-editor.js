import { LitElement, html, css } from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

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
        <paper-input
          label="Modem Entity ID"
          .value="${this.config.modem_entity}"
          .configValue="${'modem_entity'}"
          @value-changed="${this._valueChanged}"
        ></paper-input>
      </div>
    `;
  }

  _valueChanged(ev) {
    if (!this.config || !this.hass) return;
    const config = { ...this.config };
    config[ev.target.configValue] = ev.target.value;
    this.config = config;
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config } }));
  }
}
customElements.define("aldes-maintenance-card-editor", AldesMaintenanceCardEditor);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "aldes-maintenance-card",
  name: "Aldes Maintenance Card",
  preview: true,
  description: "A card to monitor your Aldes system maintenance and command queue.",
});
