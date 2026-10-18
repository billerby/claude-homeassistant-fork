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

const STATE_LABELS = {
  online: "Vaken",
  asleep: "Sover",
  offline: "Offline",
  driving: "Kör",
  charging: "Laddar",
  updating: "Uppdaterar",
  suspended: "Vilar",
};

const CAR_SVG = `
<svg viewBox="0 0 200 400" class="car" aria-hidden="true">
  <defs>
    <linearGradient id="body" x1="0" x2="1">
      <stop offset="0" stop-color="#9aa3ad"/>
      <stop offset="0.25" stop-color="#e9edf1"/>
      <stop offset="0.5" stop-color="#ffffff"/>
      <stop offset="0.75" stop-color="#e9edf1"/>
      <stop offset="1" stop-color="#9aa3ad"/>
    </linearGradient>
    <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2b3a4f"/>
      <stop offset="0.5" stop-color="#16202e"/>
      <stop offset="1" stop-color="#253246"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#4a7bd0" stop-opacity="0.35"/>
      <stop offset="1" stop-color="#4a7bd0" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <ellipse cx="100" cy="200" rx="110" ry="200" fill="url(#glow)"/>
  <rect class="wheel fl" x="14" y="72" width="16" height="52" rx="7"/>
  <rect class="wheel fr" x="170" y="72" width="16" height="52" rx="7"/>
  <rect class="wheel rl" x="14" y="276" width="16" height="52" rx="7"/>
  <rect class="wheel rr" x="170" y="276" width="16" height="52" rx="7"/>
  <path fill="url(#body)" d="M100,16 C142,16 164,28 169,62 L175,150 C178,205 178,262 175,318 C172,362 148,384 100,384 C52,384 28,362 25,318 C22,262 22,205 25,150 L31,62 C36,28 58,16 100,16 Z"/>
  <ellipse cx="20" cy="132" rx="9" ry="6" fill="#cfd5db"/>
  <ellipse cx="180" cy="132" rx="9" ry="6" fill="#cfd5db"/>
  <path d="M52,40 C70,32 130,32 148,40" fill="none" stroke="#b9c1c9" stroke-width="1.5"/>
  <path d="M40,30 C46,24 58,20 66,20" fill="none" stroke="#7d8ea3" stroke-width="3" stroke-linecap="round"/>
  <path d="M160,30 C154,24 142,20 134,20" fill="none" stroke="#7d8ea3" stroke-width="3" stroke-linecap="round"/>
  <path fill="url(#glass)" d="M100,104 C136,104 153,112 157,126 L159,298 C152,322 132,332 100,332 C68,332 48,322 41,298 L43,126 C47,112 64,104 100,104 Z"/>
  <path d="M48,130 C70,118 130,118 152,130" fill="none" stroke="#3d4d63" stroke-width="2"/>
  <path d="M46,296 C70,308 130,308 154,296" fill="none" stroke="#3d4d63" stroke-width="2"/>
  <path d="M60,140 L60,290 M140,140 L140,290" stroke="#ffffff" stroke-opacity="0.06" stroke-width="10"/>
  <path d="M42,372 C60,380 140,380 158,372" fill="none" stroke="#c0392b" stroke-width="4" stroke-linecap="round"/>
</svg>`;

class TeslaStatusCard extends HTMLElement {
  setConfig(config) {
    if (!config.prefix) throw new Error("prefix krävs, t.ex. otto_von_bismarck");
    this._config = config;
    this._key = "";
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

  _val(domain, key) {
    const s = this._st(domain, key);
    return s ? s.state : undefined;
  }

  _num(domain, key) {
    const n = Number(this._val(domain, key));
    return Number.isFinite(n) ? n : undefined;
  }

  _on(key) {
    return this._val("binary_sensor", key) === "on";
  }

  set hass(hass) {
    this._hass = hass;
    // Only re-render when one of our entities changed
    const prefix = `_${this._config.prefix}_`;
    const key = Object.keys(hass.states)
      .filter((id) => id.includes(prefix) || id.endsWith(`.${this._config.prefix}`))
      .map((id) => `${id}=${hass.states[id].state}@${hass.states[id].last_changed}`)
      .join("|");
    if (key === this._key) return;
    this._key = key;
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
    return `<div class="chip ${kind}" data-entity="${entity}"><ha-icon icon="${icon}"></ha-icon>${text}</div>`;
  }

  _chargeText() {
    const state = this._val("sensor", "charging_state");
    if (state === "Charging") {
      const kw = this._num("sensor", "charger_power");
      const h = this._num("sensor", "time_to_full_charge");
      const left = h ? ` · ${Math.floor(h)} h ${Math.round((h % 1) * 60)} min kvar` : "";
      return `Laddar ${this._fmt(kw, 1)} kW${left}`;
    }
    if (!this._on("plugged_in")) return "Inte inkopplad";
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
    const title =
      state === "driving" ? "På väg" : geofence && geofence !== "unknown" && geofence !== "nil" ? geofence : "Parkerad";
    const battery = this._num("sensor", "battery");
    const limit = this._num("sensor", "charge_limit");
    const range = this._num("sensor", "range");
    const tyres = [this._tyre("fl", "front_left"), this._tyre("fr", "front_right"), this._tyre("rl", "rear_left"), this._tyre("rr", "rear_right")];
    const locked = this._on("locked");
    const update = this._on("update_available");

    const chips = [
      this._chip(locked ? "mdi:lock" : "mdi:lock-open-variant", locked ? "Låst" : "Olåst", locked ? "ok" : "warn", this._id("binary_sensor", "locked")),
      this._chip("mdi:cctv", this._on("sentry_mode") ? "Vaktläge på" : "Vaktläge av", this._on("sentry_mode") ? "ok" : "off", this._id("binary_sensor", "sentry_mode")),
      this._chip("mdi:car-door", this._on("doors_open") ? "Dörr öppen" : "Dörrar stängda", this._on("doors_open") ? "warn" : "ok", this._id("binary_sensor", "doors_open")),
      this._chip("mdi:car-windshield-outline", this._on("windows_open") ? "Fönster öppet" : "Fönster stängda", this._on("windows_open") ? "warn" : "ok", this._id("binary_sensor", "windows_open")),
    ];
    if (this._on("trunk_open")) chips.push(this._chip("mdi:car-back", "Bagagelucka öppen", "warn", this._id("binary_sensor", "trunk_open")));
    if (this._on("frunk_open")) chips.push(this._chip("mdi:car-select", "Frunk öppen", "warn", this._id("binary_sensor", "frunk_open")));
    chips.push(this._chip("mdi:fan", this._on("climate_on") ? "Klimat på" : "Klimat av", this._on("climate_on") ? "ok" : "off", this._id("binary_sensor", "climate_on")));
    if (update)
      chips.push(this._chip("mdi:update", `Uppdatering ${this._val("sensor", "update_version") || ""}`, "update", this._id("binary_sensor", "update_available")));

    const odometer = this._num("sensor", "odometer");
    const inside = this._num("sensor", "temperature_inside");
    const outside = this._num("sensor", "temperature_outside");

    this.shadowRoot.innerHTML = `
      <style>${STYLE}</style>
      <ha-card>
        <div class="wrap">
          <div class="head">
            <div>
              <div class="sub">${c.model || "Tesla"} · ${c.name || ""}</div>
              <div class="title">${title}</div>
            </div>
            <div class="pill ${state || ""}" data-entity="${this._id("sensor", "state")}">
              <span class="dot"></span>${STATE_LABELS[state] || state || "Okänt"}
            </div>
          </div>
          <div class="car-grid">
            ${tyres[0].html}
            <div class="car-wrap" data-entity="${this._id("binary_sensor", "locked")}">
              ${CAR_SVG}
              <ha-icon class="lock" icon="${locked ? "mdi:lock" : "mdi:lock-open-variant"}"></ha-icon>
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
    display: grid; grid-template-columns: 1fr minmax(120px, 170px) 1fr; grid-template-rows: auto auto;
    align-items: center; margin-top: 14px;
  }
  .car-wrap { grid-column: 2; grid-row: 1 / span 2; position: relative; }
  .car { width: 100%; display: block; }
  .car .wheel { fill: #2a3240; }
  .car .wheel.low { fill: #b8813a; filter: drop-shadow(0 0 6px rgba(240,170,80,0.7)); }
  .lock { position: absolute; left: 50%; top: 52%; transform: translate(-50%, -50%); color: #c9d3df; --mdc-icon-size: 20px; }
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
