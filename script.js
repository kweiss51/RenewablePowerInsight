document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("energyForm");
  const results = document.getElementById("results");
  const outputText = document.getElementById("outputText");
  const blogPosts = document.getElementById("blogPosts");

  // Mock energy output factors (kWh per kW per year)
  const energyFactors = {
    solar: {
      "Phoenix, AZ": 1700,
      "Seattle, WA": 1100,
      "Denver, CO": 1500,
      default: 1300
    },
    wind: {
      "Amarillo, TX": 3000,
      "Chicago, IL": 2500,
      default: 2200
    },
    hydro: {
      default: 4000
    },
    geothermal: {
      default: 5000
    }
  };

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const city = document.getElementById("city").value.trim();
    const energyType = document.getElementById("energyType").value;
    const systemSize = parseFloat(document.getElementById("systemSize").value);

    if (!city || isNaN(systemSize)) return;

    const cityFactor = energyFactors[energyType][city] || energyFactors[energyType].default;
    const estimatedOutput = cityFactor * systemSize;

    outputText.textContent = `In ${city}, a ${systemSize} kW ${energyType} system could generate approximately ${estimatedOutput.toLocaleString()} kWh per year.`;
    results.classList.remove("hidden");
  });

  // Mock blog posts
  const posts = [
    {
      title: "Solar vs Wind: Which Is Better for Your Region?",
      summary: "Explore the pros and cons of solar and wind energy depending on your climate and geography.",
      link: "#"
    },
    {
      title: "Top 5 Cities for Geothermal Potential",
      summary: "Discover which U.S. cities offer the best conditions for geothermal energy systems.",
      link: "#"
    },
    {
      title: "How to Size Your Renewable System",
      summary: "Learn how to estimate the right system size for your household energy needs.",
      link: "#"
    }
  ];

  posts.forEach(post => {
    const div = document.createElement("div");
    div.className = "bg-gray-50 p-4 rounded shadow";
    div.innerHTML = `
      <h4 class="text-lg font-semibold mb-2">${post.title}</h4>
      <p class="text-gray-700 mb-2">${post.summary}</p>
      <a href="${post.link}" class="text-green-600 underline">Read more</a>
    `;
    blogPosts.appendChild(div);
  });
});
