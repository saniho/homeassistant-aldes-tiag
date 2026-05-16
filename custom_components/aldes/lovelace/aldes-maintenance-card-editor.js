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

    const showHistory = this.config.show_history_detail !== false;
    const showFailed = this.config.show_failed_detail !== false;
    const showPending = this.config.show_pending_detail !== false;

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

        <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--divider-color);">
          <div style="font-weight: 600; margin-bottom: 8px;">Détails à afficher :</div>

          <ha-formfield label="Historique">
            <ha-switch
              .checked="${showHistory}"
              @change="${(ev) => this._toggleBool("show_history_detail", ev.target.checked)}"
            ></ha-switch>
          </ha-formfield>

          <ha-formfield label="Échecs">
            <ha-switch
              .checked="${showFailed}"
              @change="${(ev) => this._toggleBool("show_failed_detail", ev.target.checked)}"
            ></ha-switch>
          </ha-formfield>

          <ha-formfield label="En attente">
            <ha-switch
              .checked="${showPending}"
              @change="${(ev) => this._toggleBool("show_pending_detail", ev.target.checked)}"
            ></ha-switch>
          </ha-formfield>
        </div>
      </div>
    `;
  }

  _valueChanged(ev, key) {
    const val = ev.detail && ev.detail.value ? ev.detail.value : "";
    const config = { ...this.config, [key]: val };
    this.config = config;
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config } }));
  }

  _toggleBool(key, checked) {
    const config = { ...this.config, [key]: checked };
    this.config = config;
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config } }));
  }
}
if (!customElements.get("aldes-maintenance-card-editor")) {
  customElements.define("aldes-maintenance-card-editor", AldesMaintenanceCardEditor);
}
