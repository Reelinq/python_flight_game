const state = {
  airports: [],
  filtered: [],
  selected: null,
  map: null,
  markers: [],
};

const formStatus = document.getElementById("form-status");
const airportStatus = document.getElementById("airports-status");
const listEl = document.getElementById("airport-list");
const filterEl = document.getElementById("airport-filter");
const nameInput = document.getElementById("player-name");
const startBtn = document.getElementById("start-game");

function setStatus(el, msg, isError = false) {
  el.textContent = msg || "";
  el.style.color = isError ? "#c0392b" : "";
}

function debounce(fn, wait = 200) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  };
}

function initMap() {
  state.map = L.map("start-map").setView([20, 0], 2);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 8,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
  }).addTo(state.map);
}

function renderAirports() {
  listEl.innerHTML = "";
  state.markers.forEach((m) => m.marker.remove());
  state.markers = [];

  const results = state.filtered;
  if (!results.length) {
    setStatus(airportStatus, "No airports match your search.", true);
    return;
  }
  setStatus(airportStatus, `${results.length} airports loaded in view`);

  results.forEach((a) => {
    const card = document.createElement("div");
    card.className = "airport-card";
    card.innerHTML = `
      <h3>${a.ident} — ${a.name || "Unknown"}</h3>
      <small>${a.municipality || "Unknown"}, ${a.iso_country || ""}</small>
      <span class="pill">Select</span>
    `;
    card.addEventListener("click", () => selectAirport(a.ident));
    listEl.appendChild(card);

    if (a.latitude_deg && a.longitude_deg) {
      const marker = L.circleMarker([a.latitude_deg, a.longitude_deg], {
        radius: 6,
        color: "#5d9bff",
        weight: 2,
        fillColor: "#7f6cf1",
        fillOpacity: 0.9,
      });
      marker.on("click", () => selectAirport(a.ident));
      marker.addTo(state.map);
      state.markers.push({ airport: a, marker });
    }
  });
}

function selectAirport(ident) {
  state.selected = state.airports.find((a) => a.ident === ident) || null;
  if (!state.selected) return;
  formStatus.textContent = `Selected ${state.selected.ident} – ${
    state.selected.municipality || state.selected.name || ""
  }`;

  state.markers.forEach(({ airport, marker }) => {
    const isSelected = airport.ident === ident;
    marker.setStyle({
      color: isSelected ? "#f39c12" : "#5d9bff",
      fillColor: isSelected ? "#f1c40f" : "#7f6cf1",
      radius: isSelected ? 8 : 6,
    });
    if (isSelected) {
      marker.bringToFront();
      state.map.flyTo([airport.latitude_deg, airport.longitude_deg], 4, {
        duration: 0.4,
      });
    }
  });
}

async function loadAirportsForView() {
  const bounds = state.map.getBounds();
  const params = new URLSearchParams({
    min_lat: bounds.getSouth(),
    max_lat: bounds.getNorth(),
    min_lon: bounds.getWest(),
    max_lon: bounds.getEast(),
    limit: 600,
  });
  setStatus(airportStatus, "Loading airports in view…");
  try {
    const res = await fetch(`/airports/viewport?${params.toString()}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const mapByIdent = new Map(state.airports.map((a) => [a.ident, a]));
    data.forEach((a) => mapByIdent.set(a.ident, a));
    state.airports = Array.from(mapByIdent.values());
    applyFilter();
  } catch (err) {
    console.error(err);
    setStatus(
      airportStatus,
      "Failed to load airports. Please move the map or reload.",
      true
    );
  }
}

function applyFilter() {
  const term = filterEl.value.trim().toLowerCase();
  if (!term) {
    state.filtered = state.airports;
  } else {
    state.filtered = state.airports.filter(
      (a) =>
        (a.name || "").toLowerCase().includes(term) ||
        (a.municipality || "").toLowerCase().includes(term) ||
        (a.ident || "").toLowerCase().includes(term)
    );
  }
  renderAirports();
}

async function startGame() {
  const screenName = nameInput.value.trim();
  if (!screenName) {
    setStatus(formStatus, "Please enter your screen name.", true);
    return;
  }
  if (!state.selected) {
    setStatus(formStatus, "Pick a starting airport on the map.", true);
    return;
  }
  setStatus(formStatus, "Starting game…");
  try {
    const savedSettings = localStorage.getItem("flightGame:settings");
    const settings = savedSettings ? JSON.parse(savedSettings) : { budget: 2000, rate: 20, unit: "per100" };

    const res = await fetch("/game/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        screen_name: screenName,
        start_airport_ident: state.selected.ident,
        initial_co2_budget: settings.budget,
        co2_per_100km: settings.unit === "per100" ? settings.rate : settings.rate * 100,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || `HTTP ${res.status}`);
    }
    localStorage.setItem("flightGame:gameId", data.id);
    localStorage.setItem("flightGame:screenName", data.screen_name);
    localStorage.setItem("flightGame:startAirport", state.selected.ident);
    window.location.href = `/ui/move?gameId=${data.id}`;
  } catch (err) {
    console.error(err);
    setStatus(formStatus, err.message || "Could not start game.", true);
  }
}

function init() {
  initMap();
  loadAirportsForView();
  state.map.on("moveend", debounce(loadAirportsForView, 250));
  filterEl.addEventListener("input", applyFilter);
  startBtn.addEventListener("click", startGame);
}

document.addEventListener("DOMContentLoaded", init);
