// Editor is now inline in aldes-maintenance-card.js
// This file kept for compatibility - does nothing if already defined.
if (!customElements.get("aldes-maintenance-card-editor")) {
  customElements.define("aldes-maintenance-card-editor", class extends HTMLElement {
    setConfig(c) { this._c = c; }
    set hass(h) { 
      if (!this._form) {
        const schema = [
          { name: "modem_entity", selector: { entity: { domain: "sensor" } } },
          { name: "connectivity_entity", selector: { entity: { domain: "sensor" } } },
          {
            name: "", type: "grid", column_min_width: "120px",
            schema: [
              { name: "show_history_detail", selector: { boolean: {} } },
              { name: "show_failed_detail", selector: { boolean: {} } },
              { name: "show_pending_detail", selector: { boolean: {} } },
            ],
          },
        ];
        const form = document.createElement("ha-form");
        form.hass = h;
        form.data = this._c || {};
        form.schema = schema;
        form.computeLabel = (s) => ({
          modem_entity: "Modem Entity (Pending Commands)",
          connectivity_entity: "Connectivity Sensor (API Health)",
          show_history_detail: "Afficher l'historique",
          show_failed_detail: "Afficher les échecs",
          show_pending_detail: "Afficher les en attente",
        })[s.name] || s.name;
        form.addEventListener("value-changed", (e) => this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: e.detail.value }, bubbles: true, composed: true })));
        this._form = form;
        this.appendChild(form);
      } else {
        this._form.hass = h;
        this._form.data = this._c;
      }
    }
  });
}
