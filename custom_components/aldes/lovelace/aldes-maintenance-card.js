import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

class AldesMaintenanceCard extends LitElement {
  static get properties() {
    return {
      hass: {},
      config: {},
    };
  }

  static get styles() {
    return css`
      :host {
        display: block;
        padding: 16px;
        background: var(--ha-card-background, var(--card-background-color, white));
        border-radius: var(--ha-card-border-radius, 12px);
        box-shadow: var(--ha-card-box-shadow, 0px 2px 4px rgba(0,0,0,0.1));
      }
      .header {
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      .title { display: flex; align-items: center; gap: 8px; }
      .grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
      }
      .item {
        display: flex;
        flex-direction: column;
        align-items: center;
        background: var(--secondary-background-color);
        padding: 8px;
        border-radius: 8px;
      }
      .value { font-weight: bold; font-size: 1.1em; }
      .label { font-size: 0.8em; color: var(--secondary-text-color); }
      .alert { color: var(--error-color); }
      .warning { color: var(--warning-color); }
      .connected { color: var(--success-color); }
      .disconnected { color: var(--error-color); }
      .detail-section {
        margin-top: 16px;
      }
      .detail-title {
        font-weight: 600;
        font-size: 0.85em;
        margin-bottom: 4px;
        color: var(--secondary-text-color);
      }
      .detail-list {
        margin: 0;
        padding-left: 20px;
        font-size: 0.85em;
      }
      .detail-list li {
        margin: 2px 0;
      }
      .fail-item { color: var(--error-color); }
      .pending-item { color: var(--warning-color); }
    `;
  }

  static getConfigElement() {
    return document.createElement("aldes-maintenance-card-editor");
  }

  setConfig(config) {
    this.config = config;
  }

  render() {
    if (!this.hass || !this.config) return html``;
    if (!this.config.modem_entity && !this.config.connectivity_entity) {
      return html`<ha-card><ha-alert alert-type="info">Configure the card entities in the editor.</ha-alert></ha-card>`;
    }

    const stateObj = this.config.modem_entity ? this.hass.states[this.config.modem_entity] : null;
    const attrs = stateObj ? stateObj.attributes || {} : {};
    const pending = attrs.pending || [];
    const history = attrs.history || [];
    const failed = attrs.failed || [];
    const current = attrs.current || "—";

    let connected = stateObj ? stateObj.state === "on" || attrs.is_connected : false;
    let connectivityState = "";
    if (this.config.connectivity_entity) {
      const connState = this.hass.states[this.config.connectivity_entity];
      if (connState) {
        connectivityState = connState.state;
        connected = connState.state === "online" || connState.state === "on";
      }
    }

    const showHistory = this.config.show_history_detail !== false;
    const showFailed = this.config.show_failed_detail !== false;
    const showPending = this.config.show_pending_detail !== false;

    return html`
      <div class="header">
        <div class="title">
          <ha-icon icon="mdi:air-filter"></ha-icon>
          <span>Aldes Maintenance</span>
        </div>
        <span class="${connected ? 'connected' : 'disconnected'}">
          ${connected ? "● Connected" : "● Disconnected"}
          ${connectivityState ? html` (${connectivityState})` : ""}
        </span>
      </div>
      ${stateObj ? html`
      <div class="grid">
        <div class="item ${pending.length > 0 ? 'warning' : ''}">
          <span class="value">${pending.length}</span>
          <span class="label">Pending</span>
        </div>
        <div class="item ${failed.length > 0 ? 'alert' : ''}">
          <span class="value">${failed.length}</span>
          <span class="label">Failed</span>
        </div>
        <div class="item" style="grid-column: span 2;">
          <span class="value">${current}</span>
          <span class="label">Current</span>
        </div>
      </div>

      ${showPending && pending.length > 0 ? html`
        <div class="detail-section">
          <div class="detail-title">En attente :</div>
          <ul class="detail-list">
            ${pending.map(p => html`<li class="pending-item">${p}</li>`)}
          </ul>
        </div>
      ` : ""}

      ${showFailed && failed.length > 0 ? html`
        <div class="detail-section">
          <div class="detail-title">Échecs :</div>
          <ul class="detail-list">
            ${failed.map(f => html`<li class="fail-item">${f}</li>`)}
          </ul>
        </div>
      ` : ""}

      ${showHistory && history.length > 0 ? html`
        <div class="detail-section">
          <div class="detail-title">Historique :</div>
          <ul class="detail-list">
            ${history.slice(-5).reverse().map(h => html`<li>${h}</li>`)}
          </ul>
        </div>
      ` : ""}
      ` : ""}
    `;
  }
}

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
customElements.define("aldes-maintenance-card-editor", AldesMaintenanceCardEditor);

customElements.define("aldes-maintenance-card", AldesMaintenanceCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "aldes-maintenance-card",
  name: "Aldes Maintenance Card",
  preview: true,
  description: "A card to monitor your Aldes system maintenance and command queue.",
});
