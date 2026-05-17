// Editor is now inline in aldes-maintenance-card.js
// This file kept for backward compatibility.
if (!customElements.get("aldes-maintenance-card-editor")) {
  class AldesMaintenanceCardEditor extends HTMLElement {
    setConfig(config) {
      this._config = config;
    }

    set hass(hass) {
      this._hass = hass;
      this._render();
    }

    _render() {
      if (this._initialized) {
        const form = this.querySelector("ha-form");
        if (form) {
          form.hass = this._hass;
          form.data = this._config;
        }
        return;
      }
      this._initialized = true;

      const schema = [
        { name: "modem_entity", selector: { entity: { domain: "sensor" } } },
        { name: "connectivity_entity", selector: { entity: { domain: "sensor" } } },
        {
          name: "",
          type: "grid",
          column_min_width: "120px",
          schema: [
            { name: "show_history_detail", selector: { boolean: {} } },
            { name: "show_failed_detail", selector: { boolean: {} } },
            { name: "show_pending_detail", selector: { boolean: {} } },
          ],
        },
      ];

      const form = document.createElement("ha-form");
      form.hass = this._hass;
      form.data = this._config;
      form.schema = schema;
      form.computeLabel = (s) => {
        const labels = {
          modem_entity: "Modem Entity (Pending Commands)",
          connectivity_entity: "Connectivity Sensor (API Health)",
          show_history_detail: "Afficher l'historique",
          show_failed_detail: "Afficher les échecs",
          show_pending_detail: "Afficher les en attente",
        };
        return labels[s.name] || s.name;
      };

      form.addEventListener("value-changed", (ev) => {
        this.dispatchEvent(new CustomEvent("config-changed", {
          detail: { config: ev.detail.value },
          bubbles: true,
          composed: true,
        }));
      });

      this.appendChild(form);
    }
  }
  customElements.define("aldes-maintenance-card-editor", AldesMaintenanceCardEditor);
}
