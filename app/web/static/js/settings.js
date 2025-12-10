const budgetInput = document.getElementById("co2-budget");
const rateInput = document.getElementById("co2-rate");
const saveBtn = document.getElementById("save-settings");
const randomizeBtn = document.getElementById("randomize-btn");
const statusEl = document.getElementById("settings-status");

function loadSettings() {
  const saved = localStorage.getItem("flightGame:settings");
  if (saved) {
    const settings = JSON.parse(saved);
    budgetInput.value = settings.budget || 2000;
    rateInput.value = settings.rate || 20;
    const unitRadios = document.querySelectorAll('input[name="co2Unit"]');
    unitRadios.forEach((radio) => {
      radio.checked = radio.value === (settings.unit || "per100");
    });
  }
}

function saveSettings() {
  const budget = parseFloat(budgetInput.value);
  const rate = parseFloat(rateInput.value);
  const unitRadios = document.querySelectorAll('input[name="co2Unit"]');
  const unit = Array.from(unitRadios).find((r) => r.checked)?.value || "per100";

  if (!budget || budget < 100) {
    statusEl.textContent = "Budget must be at least 100";
    statusEl.style.color = "#c0392b";
    return;
  }

  if (!rate || rate <= 0) {
    statusEl.textContent = "CO2 rate must be greater than 0";
    statusEl.style.color = "#c0392b";
    return;
  }

  const settings = { budget, rate, unit };
  localStorage.setItem("flightGame:settings", JSON.stringify(settings));

  statusEl.textContent = `Settings saved! Budget: ${budget} kg, Rate: ${rate} CO2 ${unit === "per100" ? "per 100km" : "per km"}`;
  statusEl.style.color = "#27ae60";
}

function randomizeSettings() {
  const randomBudget = Math.floor(Math.random() * (5000 - 500 + 1)) + 500;
  const randomRate = (Math.random() * (50 - 5) + 5).toFixed(1);

  budgetInput.value = randomBudget;
  rateInput.value = randomRate;

  saveSettings();
}

saveBtn.addEventListener("click", saveSettings);
randomizeBtn.addEventListener("click", randomizeSettings);

document.addEventListener("DOMContentLoaded", loadSettings);
