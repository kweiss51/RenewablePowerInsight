// Calculator functions translated from Python
const calculatorUtils = {
    calculateSolarPotential(consumption, location) {
        // Using same constants as Python version
        const avgSunHours = 5.5;  // Average sun hours per day
        const panelEfficiency = 0.20;  // 20% efficient panels
        const panelSize = 1.6;  // Size in square meters
        const panelRating = 0.250;  // 250W panel
        
        const dailyEnergyNeeded = consumption / 30;  // Convert monthly to daily
        const panelsNeeded = dailyEnergyNeeded / (avgSunHours * panelRating);
        
        return {
            panelsNeeded: Math.round(panelsNeeded),
            totalArea: Math.round(panelsNeeded * panelSize * 100) / 100,
            estimatedCost: Math.round(panelsNeeded * 500),
            paybackPeriod: Math.round((panelsNeeded * 500) / (consumption * 0.12 * 12) * 10) / 10
        };
    },

    calculateWindPotential(consumption, location) {
        // Using same constants as Python version
        const avgWindSpeed = 5.0;  // m/s
        const turbineEfficiency = 0.35;
        const airDensity = 1.225;  // kg/m³
        
        const dailyEnergy = consumption / 30;
        const hoursAtRated = 6;  // Assumed hours at rated power per day
        
        // Power = 0.5 * air density * swept area * wind speed³ * efficiency
        const requiredPower = dailyEnergy / hoursAtRated;
        const sweptArea = (requiredPower * 2) / (airDensity * Math.pow(avgWindSpeed, 3) * turbineEfficiency);
        
        // Convert swept area to rotor diameter
        const rotorDiameter = Math.sqrt((sweptArea * 4 / Math.PI));
        
        return {
            turbineSizeKw: Math.round(requiredPower / 1000 * 10) / 10,
            rotorDiameter: Math.round(rotorDiameter * 10) / 10,
            estimatedCost: Math.round(requiredPower * 2000),
            paybackPeriod: Math.round((requiredPower * 2000) / (consumption * 0.12 * 12) * 10) / 10
        };
    },

    estimateCo2Reduction(energyKwh) {
        const co2PerKwh = 0.85;  // kg CO2 per kWh
        return energyKwh * co2PerKwh;
    }
};

// DOM Elements
const calculatorForm = document.querySelector('#calculator');
const consumptionInput = document.querySelector('#consumption');
const locationInput = document.querySelector('#location');
const calculateButton = document.querySelector('#calculate');
const resultsDiv = document.querySelector('#results');
const blogPostsContainer = document.querySelector('#blog-posts');

// Calculator functionality
calculateButton.addEventListener('click', () => {
    const consumption = parseFloat(consumptionInput.value);
    const location = locationInput.value;

    if (!consumption || !location) {
        showError('Please fill in all fields');
        return;
    }

    try {
        const solarResults = calculatorUtils.calculateSolarPotential(consumption, location);
        const windResults = calculatorUtils.calculateWindPotential(consumption, location);
        const monthlyCo2Reduction = calculatorUtils.estimateCo2Reduction(consumption);
        
        displayResults({
            solar: {
                ...solarResults,
                co2Reduction: monthlyCo2Reduction
            },
            wind: {
                ...windResults,
                co2Reduction: monthlyCo2Reduction
            }
        });
    } catch (error) {
        showError('Error calculating results. Please try again.');
        console.error(error);
    }
});

function displayResults(results) {
    resultsDiv.innerHTML = `
        <div class="bg-gray-50 p-4 rounded-md">
            <h3 class="text-lg font-semibold text-primary mb-3">Your Renewable Options</h3>
            
            <div class="mb-4">
                <h4 class="font-medium text-dark">Solar Power</h4>
                <ul class="mt-2 space-y-1">
                    <li>Panels needed: ${results.solar.panelsNeeded}</li>
                    <li>Total area required: ${results.solar.totalArea} m²</li>
                    <li>Estimated cost: $${results.solar.estimatedCost.toLocaleString()}</li>
                    <li>Payback period: ${results.solar.paybackPeriod} years</li>
                    <li>CO2 reduction: ${results.solar.co2Reduction.toFixed(2)} kg/month</li>
                </ul>
            </div>

            <div>
                <h4 class="font-medium text-dark">Wind Power</h4>
                <ul class="mt-2 space-y-1">
                    <li>Recommended turbine size: ${results.wind.turbineSizeKw} kW</li>
                    <li>Rotor diameter needed: ${results.wind.rotorDiameter} m</li>
                    <li>Estimated cost: $${results.wind.estimatedCost.toLocaleString()}</li>
                    <li>Payback period: ${results.wind.paybackPeriod} years</li>
                    <li>CO2 reduction: ${results.wind.co2Reduction.toFixed(2)} kg/month</li>
                </ul>
            </div>
        </div>
    `;
    resultsDiv.classList.remove('hidden');
}

function showError(message) {
    resultsDiv.innerHTML = `
        <div class="bg-red-50 text-red-700 p-4 rounded-md">
            ${message}
        </div>
    `;
    resultsDiv.classList.remove('hidden');
}

// Blog functionality
const blogPosts = [
    {
        title: "Understanding Solar Panel Efficiency",
        excerpt: "Learn about the factors that affect solar panel performance and how to maximize your energy production.",
        date: "2025-08-14"
    },
    {
        title: "Wind Power: A Comprehensive Guide",
        excerpt: "Everything you need to know about residential wind power systems and their benefits.",
        date: "2025-08-10"
    }
];

function displayBlogPosts() {
    blogPostsContainer.innerHTML = blogPosts.map(post => `
        <article class="bg-white p-6 rounded-lg shadow-md">
            <h3 class="text-xl font-semibold text-primary mb-2">${post.title}</h3>
            <p class="text-gray-600 mb-3">${post.excerpt}</p>
            <time class="text-sm text-gray-500">${new Date(post.date).toLocaleDateString()}</time>
        </article>
    `).join('');
}

// Initialize blog posts
displayBlogPosts();
