const gameState = {
  gameId: null,
  screenName: null,
  currentState: null,
  map: null,
  markers: {
    current: null,
    targets: [],
  },
  selectedDestination: null,
  isLoading: false,
  lastLocationIdent: null,
};

const playerNameEl = document.getElementById("player-name");
const currentAirportEl = document.getElementById("current-airport-name");
const currentAirportCodeEl = document.getElementById("current-airport-code");
const budgetUsedEl = document.getElementById("budget-used");
const budgetUsedTextEl = document.getElementById("budget-used-text");
const budgetTotalTextEl = document.getElementById("budget-total-text");
const budgetRemainingTextEl = document.getElementById("budget-remaining-text");
const targetListEl = document.getElementById("target-list");
const targetsCountEl = document.getElementById("targets-count");
const statusMessageEl = document.getElementById("status-message");
const destinationInfoEl = document.getElementById("destination-info");
const destAirportNameEl = document.getElementById("dest-airport-name");
const destAirportCodeEl = document.getElementById("dest-airport-code");
const destMunicipalityEl = document.getElementById("dest-municipality");
const destCountryEl = document.getElementById("dest-country");
const destDistanceEl = document.getElementById("dest-distance");
const destCo2CostEl = document.getElementById("dest-co2-cost");
const travelBtnEl = document.getElementById("travel-btn");
const cancelDestinationBtnEl = document.getElementById("cancel-destination-btn");

function haversine(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function showStatus(message, type = "default") {
  statusMessageEl.textContent = message;
  statusMessageEl.className = `status-message ${type}`;
}

function initMap() {
  gameState.map = L.map("move-map").setView([20, 0], 2);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 13,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
  }).addTo(gameState.map);
}

function createMarkerIcon(type = "target", isVisited = false) {
  let color, size;

  if (type === "current") {
    color = "#3498db";
    size = 12;
  } else if (type === "target") {
    color = isVisited ? "#27ae60" : "#f39c12";
    size = 10;
  }

  return L.circleMarker([0, 0], {
    radius: size,
    color: color,
    weight: 2,
    fillColor: color,
    fillOpacity: 0.8,
  });
}

function updateMapMarkers() {
  if (!gameState.currentState) return;

  const currentLocation = gameState.currentState.current_airport.ident;
  const isLocationChanged = gameState.lastLocationIdent !== currentLocation;

  Object.values(gameState.markers.targets).forEach((m) => m.remove());
  gameState.markers.targets = [];
  if (gameState.markers.current) gameState.markers.current.remove();

  const current = gameState.currentState.current_airport;
  const visited = new Set(gameState.currentState.visited_idents || []);

  const currentMarker = L.circleMarker(
    [current.latitude_deg, current.longitude_deg],
    {
      radius: 12,
      color: "#3498db",
      weight: 3,
      fillColor: "#3498db",
      fillOpacity: 0.9,
    }
  );

  currentMarker.bindPopup(
    `<strong>${current.ident}</strong><br>${current.name}<br><small>${current.municipality}</small>`
  );
  currentMarker.addTo(gameState.map);
  gameState.markers.current = currentMarker;

  gameState.currentState.target_airports.forEach((airport) => {
    const isVisited = visited.has(airport.ident);
    const marker = L.circleMarker(
      [airport.latitude_deg, airport.longitude_deg],
      {
        radius: isVisited ? 9 : 11,
        color: isVisited ? "#27ae60" : "#e74c3c",
        weight: 2,
        fillColor: isVisited ? "#27ae60" : "#e74c3c",
        fillOpacity: isVisited ? 0.6 : 0.8,
        opacity: isVisited ? 0.6 : 1,
      }
    );

    const popupText = `<strong>${airport.ident}</strong><br>${airport.name}<br><small>${airport.municipality}</small>${
      isVisited ? "<br><strong style='color:green'>✓ Visited</strong>" : ""
    }`;
    marker.bindPopup(popupText);

    marker.on("click", () => {
      selectDestination(airport);
    });

    marker.addTo(gameState.map);
    gameState.markers.targets.push(marker);
  });

  if (!gameState.lastLocationIdent || isLocationChanged) {
    const allMarkers = [gameState.markers.current, ...gameState.markers.targets];
    const bounds = L.latLngBounds(
      allMarkers.map((m) => m.getLatLng())
    );
    gameState.map.fitBounds(bounds, { padding: [50, 50] });
  }

  gameState.lastLocationIdent = currentLocation;
}

function updateUI() {
  if (!gameState.currentState) return;

  const state = gameState.currentState;

  playerNameEl.textContent = state.screen_name;

  currentAirportEl.textContent = `${state.current_airport.name}`;
  currentAirportCodeEl.textContent = state.current_airport.ident;

  const totalBudget = state.co2_budget;
  const usedBudget = state.co2_consumed;
  const remainingBudget = state.remainingBudget;

  const percentUsed = (usedBudget / totalBudget) * 100;
  budgetUsedEl.style.width = `${percentUsed}%`;
  budgetUsedTextEl.textContent = `${Math.round(usedBudget * 10) / 10} kg`;
  budgetTotalTextEl.textContent = `${Math.round(totalBudget)} kg`;
  budgetRemainingTextEl.textContent = `${Math.round(remainingBudget * 10) / 10} kg`;

  const remaining = state.remaining_targets || [];
  targetsCountEl.textContent = remaining.length;

  renderTargetList(state.target_airports, new Set(state.visited_idents || []));

  checkGameOver();
}

function renderTargetList(targets, visited) {
  targetListEl.innerHTML = "";

  targets.forEach((airport) => {
    const isVisited = visited.has(airport.ident);
    const div = document.createElement("div");
    div.className = `target-item ${isVisited ? "completed" : ""}`;

    const distance = haversine(
      gameState.currentState.current_airport.latitude_deg,
      gameState.currentState.current_airport.longitude_deg,
      airport.latitude_deg,
      airport.longitude_deg
    );

    div.innerHTML = `
      <h4>${airport.ident} — ${airport.name}</h4>
      <small>${airport.municipality}, ${airport.iso_country}</small>
      <small style="margin-top: 4px; display: block;">Distance: ${Math.round(distance * 10) / 10} km</small>
    `;

    if (!isVisited) {
      div.addEventListener("click", () => selectDestination(airport));
    }

    targetListEl.appendChild(div);
  });
}

function selectDestination(airport) {
  gameState.selectedDestination = airport;

  const current = gameState.currentState.current_airport;
  const distance = haversine(
    current.latitude_deg,
    current.longitude_deg,
    airport.latitude_deg,
    airport.longitude_deg
  );

  const co2Cost = (distance / 100) * 20;

  destAirportNameEl.textContent = airport.name;
  destAirportCodeEl.textContent = airport.ident;
  destMunicipalityEl.textContent = airport.municipality;
  destCountryEl.textContent = airport.iso_country;
  destDistanceEl.textContent = `${Math.round(distance * 10) / 10}`;
  destCo2CostEl.textContent = `${Math.round(co2Cost * 10) / 10}`;

  const canTravel = co2Cost <= gameState.currentState.remainingBudget;
  travelBtnEl.disabled = !canTravel;

  if (!canTravel) {
    travelBtnEl.textContent = "Insufficient CO₂ Budget";
  } else {
    travelBtnEl.textContent = "Travel Here";
  }

  destinationInfoEl.style.display = "block";

  gameState.map.flyTo([airport.latitude_deg, airport.longitude_deg], 6, {
    duration: 0.5,
  });
}

function cancelDestination() {
  gameState.selectedDestination = null;
  destinationInfoEl.style.display = "none";
}

async function travelToDestination() {
  if (!gameState.selectedDestination) return;
  if (gameState.isLoading) return;

  gameState.isLoading = true;
  travelBtnEl.disabled = true;

  try {
    const response = await fetch(
      `/game/${gameState.gameId}/travel`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          destination_ident: gameState.selectedDestination.ident,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Failed to travel");
    }

    showStatus(data.message, "success");
    cancelDestination();

    await loadGameState();
  } catch (error) {
    console.error(error);
    showStatus(error.message || "Travel failed", "error");
  } finally {
    gameState.isLoading = false;
    travelBtnEl.disabled = false;
  }
}

async function loadGameState() {
  try {
    const response = await fetch(`/game/${gameState.gameId}/state`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Failed to load game state");
    }

    gameState.currentState = data;
    updateUI();
    updateMapMarkers();
  } catch (error) {
    console.error(error);
    showStatus("Failed to load game state", "error");
  }
}

async function checkGameOver() {
  try {
    const response = await fetch(
      `/game/${gameState.gameId}/over`
    );
    const data = await response.json();

    if (data.game_over) {
      showStatus("", "default");
      travelBtnEl.disabled = true;
    }
  } catch (error) {
    console.error("Failed to check game over status", error);
  }
}

async function init() {
  const params = new URLSearchParams(window.location.search);
  gameState.gameId = params.get("gameId") || localStorage.getItem("flightGame:gameId");
  gameState.screenName = localStorage.getItem("flightGame:screenName");

  if (!gameState.gameId) {
    window.location.href = "/ui/";
    return;
  }

  initMap();
  await loadGameState();

  travelBtnEl.addEventListener("click", travelToDestination);
  cancelDestinationBtnEl.addEventListener("click", cancelDestination);

  setInterval(loadGameState, 2000);

  showStatus("Welcome! Click on a target airport (red markers) to select a destination.");
}

document.addEventListener("DOMContentLoaded", init);
