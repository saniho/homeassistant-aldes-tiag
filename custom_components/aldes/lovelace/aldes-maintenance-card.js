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
    `;
  }

  static getConfigElement() {
    return document.createElement("aldes-maintenance-card-editor");
  }

  setConfig(config) {
    if (!config.modem_entity) {
      throw new Error("You need to define modem_entity");
    }
    this.config = config;
  }

  render() {
    if (!this.hass) return html``;
    const stateObj = this.hass.states[this.config.modem_entity];
    if (!stateObj) return html`Entity not found: ${this.config.modem_entity}`;

    const attrs = stateObj.attributes || {};
    const pending = attrs.pending || [];
    const history = attrs.history || [];
    const failed = attrs.failed || [];
    const current = attrs.current || "Idle";
    const connected = stateObj.state === "on" || attrs.is_connected;

    return html`
      <div class="header">
        <div class="title">
          <ha-icon icon="mdi:air-filter"></ha-icon>
          <span>Aldes Maintenance</span>
        </div>
        <span class="${connected ? 'connected' : 'disconnected'}">
          ${connected ? "● Connected" : "● Disconnected"}
        </span>
      </div>
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
      <div style="margin-top: 16px;">
        <div class="label">Recent History:</div>
        <ul>
          ${history.slice(-3).map(h => html`<li>${h}</li>`)}
        </ul>
      </div>
    `;
  }
}

customElements.define("aldes-maintenance-card", AldesMaintenanceCard);
