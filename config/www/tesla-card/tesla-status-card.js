// Tesla status card for the Bilen view: the car seen from above with tyre
// pressures at the wheels, battery and range, and status chips. Reads the
// TeslaMate MQTT entities from packages/otto_von_bismarck.yaml.
//
//   type: custom:tesla-status-card
//   prefix: otto_von_bismarck      # entity ids are <domain>.<prefix>_<key>
//   name: Otto von Bismarck
//   model: Model 3
//   recommended_pressure: 2.9      # bar; optional, below it minus 0.1 reads as low
//   broken_tyres: [rear_right]     # sensors that no longer report; shown as such
//   image: /local/tesla-card/model3_top.webp?v=2   # top view, front pointing up

// Every entity the card reads, as [domain, key]; changes to anything else are ignored
const ENTITIES = [
  ...["state", "geofence", "battery", "range", "charge_limit", "charging_state", "charger_power", "time_to_full_charge",
    "update_version", "odometer", "temperature_inside", "temperature_outside"].map((k) => ["sensor", k]),
  ...["front_left", "front_right", "rear_left", "rear_right"].flatMap((t) => [["sensor", `tpms_${t}`], ["binary_sensor", `tpms_soft_warning_${t}`]]),
  ...["locked", "sentry_mode", "doors_open", "windows_open", "trunk_open", "frunk_open", "climate_on", "update_available",
    "plugged_in"].map((k) => ["binary_sensor", k]),
];

const esc = (v) =>
  String(v).replace(/[&<>"']/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[ch]);

const STATE_LABELS = {
  online: "Vaken",
  asleep: "Sover",
  offline: "Offline",
  driving: "Kör",
  charging: "Laddar",
  updating: "Uppdaterar",
  suspended: "Vilar",
};

class TeslaStatusCard extends HTMLElement {
  setConfig(config) {
    if (!config.prefix) throw new Error("prefix krävs, t.ex. otto_von_bismarck");
    this._config = config;
    this._seen = undefined;
  }

  static getStubConfig() {
    return { prefix: "otto_von_bismarck", name: "Otto von Bismarck", model: "Model 3" };
  }

  getCardSize() {
    return 9;
  }

  _id(domain, key) {
    return `${domain}.${this._config.prefix}_${key}`;
  }

  _st(domain, key) {
    return this._hass.states[this._id(domain, key)];
  }

  // undefined when HA has no real value, so "unknown" never ends up on screen
  _val(domain, key) {
    const s = this._st(domain, key);
    return s && !["unknown", "unavailable", ""].includes(s.state) ? s.state : undefined;
  }

  _num(domain, key) {
    const n = Number(this._val(domain, key));
    return Number.isFinite(n) ? n : undefined;
  }

  _on(key) {
    return this._val("binary_sensor", key) === "on";
  }

  // true / false, or undefined when the sensor has no value
  _bool(key) {
    const v = this._val("binary_sensor", key);
    return v === undefined ? undefined : v === "on";
  }

  set hass(hass) {
    this._hass = hass;
    // HA hands over a new state object only when that entity changed
    const seen = ENTITIES.map(([d, k]) => hass.states[this._id(d, k)]);
    if (this._seen && seen.every((st, i) => st === this._seen[i])) return;
    this._seen = seen;
    this._render();
  }

  _fmt(n, decimals = 0) {
    return n === undefined
      ? "–"
      : n.toLocaleString("sv-SE", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  }

  _tyre(pos, key) {
    if ((this._config.broken_tyres || []).includes(key)) {
      return {
        low: false,
        html: `<div class="tyre ${pos} broken" data-entity="${this._id("sensor", `tpms_${key}`)}">
          <div class="pressure">–<span class="unit">bar</span></div>
          <div class="tyre-sub">Givare ur funktion</div>
        </div>`,
      };
    }
    const bar = this._num("sensor", `tpms_${key}`);
    const rec = this._config.recommended_pressure;
    const low = this._on(`tpms_soft_warning_${key}`) || (rec !== undefined && bar !== undefined && bar < rec - 0.1);
    return {
      low,
      html: `<div class="tyre ${pos} ${low ? "low" : ""}" data-entity="${this._id("sensor", `tpms_${key}`)}">
        <div class="pressure">${this._fmt(bar, 2)}<span class="unit">bar</span></div>
        <div class="tyre-sub">${low ? "Lågt" : "OK"}</div>
      </div>`,
    };
  }

  _chip(icon, text, kind, entity) {
    return `<div class="chip ${kind}" data-entity="${entity}"><ha-icon icon="${icon}"></ha-icon>${esc(text)}</div>`;
  }

  // Chip for a binary sensor: [icon, text, kind] for on and off, grey "?" text when unknown
  _flag(key, on, off, unknown) {
    const v = this._bool(key);
    const [icon, text, kind] = v === undefined ? [off[0], unknown, "unknown"] : v ? on : off;
    return this._chip(icon, text, kind, this._id("binary_sensor", key));
  }

  _chargeText() {
    const state = this._val("sensor", "charging_state");
    if (state === "Charging") {
      const kw = this._num("sensor", "charger_power");
      const h = this._num("sensor", "time_to_full_charge");
      const min = h ? Math.round(h * 60) : 0;
      const left = min ? ` · ${Math.floor(min / 60)} h ${min % 60} min kvar` : "";
      return `Laddar ${this._fmt(kw, 1)} kW${left}`;
    }
    const plugged = this._bool("plugged_in");
    if (plugged === undefined) return "Laddkabel okänd";
    if (!plugged) return "Inte inkopplad";
    return { Complete: "Inkopplad · laddning klar", Stopped: "Inkopplad · laddning pausad", NoPower: "Inkopplad · ingen ström" }[
      state
    ] || "Inkopplad";
  }

  _render() {
    if (!this._hass || !this._config) return;
    if (!this.shadowRoot) this.attachShadow({ mode: "open" });
    const c = this._config;
    const state = this._val("sensor", "state");
    const geofence = this._val("sensor", "geofence");
    const title = state === "driving" ? "På väg" : geofence && geofence !== "nil" ? geofence : "Parkerad";
    const battery = this._num("sensor", "battery");
    const limit = this._num("sensor", "charge_limit");
    const range = this._num("sensor", "range");
    const tyres = [this._tyre("fl", "front_left"), this._tyre("fr", "front_right"), this._tyre("rl", "rear_left"), this._tyre("rr", "rear_right")];
    const locked = this._bool("locked");
    const lockIcon = locked === undefined ? "mdi:lock-question" : locked ? "mdi:lock" : "mdi:lock-open-variant";

    const chips = [
      this._flag("locked", [lockIcon, "Låst", "ok"], [lockIcon, "Olåst", "warn"], "Lås okänt"),
      this._flag("sentry_mode", ["mdi:cctv", "Vaktläge på", "ok"], ["mdi:cctv", "Vaktläge av", "off"], "Vaktläge okänt"),
      this._flag("doors_open", ["mdi:car-door", "Dörr öppen", "warn"], ["mdi:car-door", "Dörrar stängda", "ok"], "Dörrar okänt"),
      this._flag("windows_open", ["mdi:car-windshield-outline", "Fönster öppet", "warn"], ["mdi:car-windshield-outline", "Fönster stängda", "ok"], "Fönster okänt"),
    ];
    if (this._on("trunk_open")) chips.push(this._chip("mdi:car-back", "Bagagelucka öppen", "warn", this._id("binary_sensor", "trunk_open")));
    if (this._on("frunk_open")) chips.push(this._chip("mdi:car-select", "Frunk öppen", "warn", this._id("binary_sensor", "frunk_open")));
    chips.push(this._flag("climate_on", ["mdi:fan", "Klimat på", "ok"], ["mdi:fan", "Klimat av", "off"], "Klimat okänt"));
    if (this._on("update_available")) {
      const version = this._val("sensor", "update_version");
      chips.push(this._chip("mdi:update", version ? `Uppdatering ${version}` : "Uppdatering", "update", this._id("binary_sensor", "update_available")));
    }

    const odometer = this._num("sensor", "odometer");
    const inside = this._num("sensor", "temperature_inside");
    const outside = this._num("sensor", "temperature_outside");

    this.shadowRoot.innerHTML = `
      <style>${STYLE}</style>
      <ha-card>
        <div class="wrap">
          <div class="head">
            <div>
              <div class="sub">${esc(c.model || "Tesla")} · ${esc(c.name || "")}</div>
              <div class="title">${esc(title)}</div>
            </div>
            <div class="pill ${STATE_LABELS[state] ? state : ""}" data-entity="${this._id("sensor", "state")}">
              <span class="dot"></span>${esc(STATE_LABELS[state] || state || "Okänt")}
            </div>
          </div>
          <div class="car-grid">
            ${tyres[0].html}
            <div class="car-wrap" data-entity="${this._id("binary_sensor", "locked")}">
              <div class="wheel fl"></div><div class="wheel fr"></div>
              <div class="wheel rl"></div><div class="wheel rr"></div>
              ${c.image ? `<img class="car" src="${esc(c.image)}" alt="">` : ""}
              <ha-icon class="lock" icon="${lockIcon}"></ha-icon>
            </div>
            ${tyres[1].html}
            ${tyres[2].html}
            ${tyres[3].html}
          </div>
          ${c.recommended_pressure ? `<div class="rec">${this._fmt(c.recommended_pressure, 1)} bar rekommenderat, fram och bak</div>` : ""}
          <div class="battery-row">
            <div class="soc" data-entity="${this._id("sensor", "battery")}">${this._fmt(battery)}<span>%</span></div>
            <div class="range" data-entity="${this._id("sensor", "range")}">
              <div><b>${this._fmt(range)}</b> km</div>
              <div class="muted">beräknad räckvidd</div>
            </div>
          </div>
          <div class="bar" data-entity="${this._id("sensor", "charge_limit")}">
            <div class="fill" style="width:${battery || 0}%"></div>
            ${limit !== undefined ? `<div class="limit" style="left:${limit}%"><span>${limit}%</span></div>` : ""}
          </div>
          <div class="charge" data-entity="${this._id("sensor", "charging_state")}">${this._chargeText()}</div>
          <div class="chips">${chips.join("")}</div>
          <div class="foot">${this._fmt(odometer)} km · ${this._fmt(inside, 1)}° inne · ${this._fmt(outside, 1)}° ute</div>
        </div>
      </ha-card>`;

    // Wheel colour follows the tyre next to it
    ["fl", "fr", "rl", "rr"].forEach((pos, i) => {
      if (tyres[i].low) this.shadowRoot.querySelector(`.wheel.${pos}`).classList.add("low");
    });
    this.shadowRoot.querySelectorAll("[data-entity]").forEach((el) =>
      el.addEventListener("click", (ev) => {
        ev.stopPropagation();
        this.dispatchEvent(
          new CustomEvent("hass-more-info", { detail: { entityId: el.dataset.entity }, bubbles: true, composed: true })
        );
      })
    );
  }
}

const STYLE = `
  ha-card {
    background: radial-gradient(120% 80% at 50% 0%, #1d2b44 0%, #121a2a 60%, #0d1320 100%);
    color: #e8edf4;
    border-radius: 24px;
    border: 1px solid rgba(255,255,255,0.08);
    overflow: hidden;
  }
  .wrap { max-width: 560px; margin: 0 auto; padding: 20px 22px 18px; }
  [data-entity] { cursor: pointer; }
  .head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
  .sub { color: #9aa7b8; font-size: 15px; }
  .title { font-size: 26px; font-weight: 600; margin-top: 2px; }
  .pill {
    display: flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 999px;
    background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12); font-weight: 600; white-space: nowrap;
  }
  .pill .dot { width: 8px; height: 8px; border-radius: 50%; background: #8fa0b5; }
  .pill.online .dot, .pill.driving .dot { background: #4cd3b0; }
  .pill.charging .dot { background: #4cd3b0; box-shadow: 0 0 8px #4cd3b0; }
  .pill.offline .dot { background: #e0533d; }
  .pill.updating .dot { background: #b48cf2; }
  .car-grid {
    display: grid; grid-template-columns: 1fr minmax(130px, 210px) 1fr; grid-template-rows: auto auto;
    align-items: center; margin-top: 14px;
  }
  .car-wrap { grid-column: 2; grid-row: 1 / span 2; position: relative; }
  .car-wrap::before {
    content: ""; position: absolute; inset: -6% -30%;
    background: radial-gradient(closest-side, rgba(74,123,208,0.28), rgba(74,123,208,0));
  }
  .car { position: relative; z-index: 1; width: 100%; display: block; filter: drop-shadow(0 12px 18px rgba(0,0,0,0.55)); }
  /* Wheels sit under the body; only their outer edge shows. Axles at about 20 % and 80 % of the length. */
  .wheel { position: absolute; z-index: 0; width: 10%; height: 14%; border-radius: 40%; background: #2a3240; }
  .wheel.fl { left: 3%; top: 13%; }
  .wheel.fr { right: 3%; top: 13%; }
  .wheel.rl { left: 1%; top: 73%; }
  .wheel.rr { right: 1%; top: 73%; }
  .wheel.low { background: #c98a3a; box-shadow: 0 0 16px 5px rgba(240,170,80,0.5); }
  .lock { position: absolute; z-index: 2; left: 50%; top: 62%; transform: translate(-50%, -50%); color: #c9d3df; --mdc-icon-size: 20px; }
  .tyre { text-align: center; padding: 30px 4px; }
  .tyre.fl { grid-column: 1; grid-row: 1; }
  .tyre.fr { grid-column: 3; grid-row: 1; }
  .tyre.rl { grid-column: 1; grid-row: 2; }
  .tyre.rr { grid-column: 3; grid-row: 2; }
  .pressure { font-size: 34px; font-weight: 300; color: #e8edf4; }
  .pressure .unit { font-size: 15px; margin-left: 4px; color: #9aa7b8; }
  .tyre-sub { font-size: 14px; font-weight: 600; color: #8fa0b5; }
  .tyre.low .pressure { color: #f0b061; }
  .tyre.low .tyre-sub { color: #e2a04f; }
  .tyre.broken .pressure, .tyre.broken .tyre-sub { color: #5f6b7c; }
  .rec { text-align: center; color: #7f8ca0; font-size: 14px; margin: 6px 0 14px; }
  .battery-row { display: flex; justify-content: space-between; align-items: flex-end; }
  .soc { font-size: 64px; font-weight: 200; line-height: 1; }
  .soc span { font-size: 26px; margin-left: 2px; color: #b8c3d1; }
  .range { text-align: right; font-size: 18px; }
  .range b { font-size: 28px; font-weight: 500; }
  .muted { color: #9aa7b8; font-size: 15px; }
  .bar { position: relative; height: 16px; border-radius: 8px; background: rgba(255,255,255,0.08); margin: 18px 0 26px; }
  .bar .fill {
    height: 100%; border-radius: 8px; background: linear-gradient(90deg, #2f9e8a, #5fd6c0);
    box-shadow: 0 0 12px rgba(95,214,192,0.35);
  }
  .bar .limit { position: absolute; top: -4px; bottom: -4px; width: 2px; background: #e8edf4; }
  .bar .limit span { position: absolute; top: 26px; left: 50%; transform: translateX(-50%); font-size: 13px; color: #9aa7b8; }
  .charge { font-size: 17px; margin-bottom: 14px; }
  .chips { display: flex; flex-wrap: wrap; gap: 8px; }
  .chip {
    display: flex; align-items: center; gap: 6px; padding: 7px 12px; border-radius: 12px; font-size: 15px; font-weight: 600;
    border: 1px solid rgba(255,255,255,0.14); color: #9aa7b8; --mdc-icon-size: 18px;
  }
  .chip.ok { color: #6fdcc4; border-color: rgba(95,214,192,0.35); background: rgba(95,214,192,0.07); }
  .chip.warn { color: #f0b061; border-color: rgba(240,176,97,0.45); background: rgba(240,176,97,0.08); }
  .chip.unknown { color: #6f7b8c; border-style: dashed; }
  .chip.update { color: #c5a3ff; border-color: rgba(180,140,242,0.45); background: rgba(180,140,242,0.1); }
  .foot { margin-top: 14px; color: #8f9cae; font-size: 15px; }
  @media (max-width: 420px) {
    .wrap { padding: 16px 14px; }
    .pressure { font-size: 28px; }
    .soc { font-size: 54px; }
  }
`;

customElements.define("tesla-status-card", TeslaStatusCard);
window.customCards = window.customCards || [];
window.customCards.push({ type: "tesla-status-card", name: "Tesla status", description: "Bilen uppifrån med däcktryck, batteri och status" });
