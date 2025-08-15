document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("energyForm");
  const results = document.getElementById("results");
  const outputText = document.getElementById("outputText");
  const offsetText = document.getElementById("offsetText");
  const savingsText = document.getElementById("savingsText");
  const roiText = document.getElementById("roiText");
  const roiBar = document.getElementById("roiBar");

  const zipData = {
    "980": { irradiance: 3.5, windFactor: 2.0, consumption: 11000, rate: 0.12 },
    "850": { irradiance: 5.5, windFactor: 1.5, consumption: 10500, rate: 0.13 },
    "606": { irradiance: 4.2, windFactor: 2.8, consumption: 9500, rate: 0.14 },
    default: { irradiance: 4.0, windFactor: 2.0, consumption: 10000, rate: 0.13 }
  };

  const defaultCosts = {
    solar: 3000,
    wind: 2500
  };

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const zip = document.getElementById("zip").value.trim();
    const energyType = document.getElementById("energyType").value;
    const systemSize = parseFloat(document.getElementById("systemSize").value);
    const installCostInput = parseFloat(document.getElementById("installCost").value);

    if (!zip || isNaN(systemSize) || systemSize <= 0) {
      alert("Please enter a valid ZIP code and system size.");
      return;
    }

    const zipPrefix = zip.substring(0, 3);
    const locationData = zipData[zipPrefix] || zipData.default;

    const irradiance = energyType === "solar" ? locationData.irradiance : locationData.windFactor;
    const annualGeneration = Math.round(irradiance * systemSize * 365);
    const avgConsumption = locationData.consumption;
    const rate = locationData.rate;

    const offsetPercent = Math.min(100, ((annualGeneration / avgConsumption) * 100).toFixed(1));
    const annualSavings = (annualGeneration * rate).toFixed(2);
    const installCost = installCostInput || (defaultCosts[energyType] * systemSize);
    const roiYears = (installCost / (annualGeneration * rate)).toFixed(1);

    outputText.textContent = `Estimated annual generation: ${annualGeneration.toLocaleString()} kWh`;
    offsetText.textContent = `Covers approximately ${offsetPercent}% of the average home's yearly energy use (${avgConsumption.toLocaleString()} kWh).`;
    savingsText.textContent = `Estimated annual savings: $${annualSavings}`;
    roiText.textContent = `Estimated ROI: ${roiYears} years`;

    let barColor = "bg-green-600";
    let label = "Fast ROI";
    if (roiYears > 10) {
      barColor = "bg-red-500";
      label = "Long ROI";
    } else if (roiYears > 1) {
      barColor = "bg-yellow-500";
      label = "Moderate ROI";
    }

    roiBar.className = `${barColor} h-6 rounded text-white text-center text-sm leading-6`;
    roiBar.style.width = `${Math.min(100, (10 / roiYears) * 100)}%`;
    roiBar.textContent = label;

    results.classList.remove("hidden");
  });
});
