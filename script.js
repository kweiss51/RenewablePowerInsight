document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById('calculator-container');
    if (!container) return; // Ensure the container exists

    // SPA-like navigation
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.site-section');

    function showSection(sectionId) {
      sections.forEach(sec => {
        sec.style.display = (sec.id === sectionId) ? 'block' : 'none';
      });
      navLinks.forEach(link => {
        if (link.dataset.section === sectionId) {
          link.classList.add('active');
        } else {
          link.classList.remove('active');
        }
      });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    navLinks.forEach(link => {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        const sectionId = this.dataset.section;
        history.pushState({ section: sectionId }, '', '#' + sectionId);
        showSection(sectionId);
      });
    });

    window.addEventListener('popstate', function (e) {
      const sectionId = (e.state && e.state.section) || location.hash.replace('#', '') || 'about';
      showSection(sectionId);
    });

    const initialSection = location.hash.replace('#', '') || 'about';
    showSection(initialSection);

    // Calculator UI
    container.innerHTML = `
      <div class="energy-calc-section">
      <h3>PV Solar Power</h3>
      <label>Panel Area (m²): <input type="number" id="pv_area" value="10" min="0"></label>
      <label>Panel Efficiency (0-1): <input type="number" step="0.01" id="pv_eff" value="0.18" min="0" max="1"></label>
      <label>Solar Irradiance (kW/m²): <input type="number" step="0.01" id="pv_irr" value="1" min="0"></label>
      <label>Sunlight Hours/Day: <input type="number" step="0.1" id="pv_hours" value="5" min="0"></label>
      <button onclick="calcPV()">Calculate</button>
      <div class="energy-calc-result" id="pv_result"></div>
      </div>
      <div class="energy-calc-section">
      <h3>Wind Turbine</h3>
      <label>Rotor Diameter (m): <input type="number" id="wind_diam" value="2" min="0"></label>
      <label>Average Wind Speed (m/s): <input type="number" step="0.1" id="wind_speed" value="5" min="0"></label>
      <label>Turbine Efficiency (0-1): <input type="number" step="0.01" id="wind_eff" value="0.35" min="0" max="1"></label>
      <label>Wind Hours/Day: <input type="number" step="0.1" id="wind_hours" value="8" min="0"></label>
      <button onclick="calcWind()">Calculate</button>
      <div class="energy-calc-result" id="wind_result"></div>
      </div>
      <div class="energy-calc-section">
      <h3>Hydropower</h3>
      <label>Flow Rate (m³/s): <input type="number" step="0.01" id="hydro_flow" value="0.1" min="0"></label>
      <label>Head (m): <input type="number" step="0.1" id="hydro_head" value="5" min="0"></label>
      <label>Turbine Efficiency (0-1): <input type="number" step="0.01" id="hydro_eff" value="0.6" min="0" max="1"></label>
      <label>Hours/Day: <input type="number" step="0.1" id="hydro_hours" value="24" min="0"></label>
      <button onclick="calcHydro()">Calculate</button>
      <div class="energy-calc-result" id="hydro_result"></div>
      </div>
      <div class="energy-calc-section">
      <h3>Geothermal</h3>
      <label>Thermal Power (kW): <input type="number" id="geo_power" value="5" min="0"></label>
      <label>Conversion Efficiency (0-1): <input type="number" step="0.01" id="geo_eff" value="0.4" min="0" max="1"></label>
      <label>Hours/Day: <input type="number" step="0.1" id="geo_hours" value="24" min="0"></label>
      <button onclick="calcGeo()">Calculate</button>
      <div class="energy-calc-result" id="geo_result"></div>
      </div>
    `;
  });

  function calcPV() {
    var area = parseFloat(document.getElementById('pv_area').value);
    var eff = parseFloat(document.getElementById('pv_eff').value);
    var irr = parseFloat(document.getElementById('pv_irr').value);
    var hours = parseFloat(document.getElementById('pv_hours').value);
    if (isNaN(area) || isNaN(eff) || isNaN(irr) || isNaN(hours) || area < 0 || eff < 0 || eff > 1 || irr < 0 || hours < 0) {
      document.getElementById('pv_result').innerText = "Please enter valid values.";
      return;
    }
    var energy = area * eff * irr * hours;
    document.getElementById('pv_result').innerText = "Daily Energy: " + energy.toFixed(2) + " kWh";
  }

  function calcWind() {
    var diam = parseFloat(document.getElementById('wind_diam').value);
    var speed = parseFloat(document.getElementById('wind_speed').value);
    var eff = parseFloat(document.getElementById('wind_eff').value);
    var hours = parseFloat(document.getElementById('wind_hours').value);
    if (isNaN(diam) || isNaN(speed) || isNaN(eff) || isNaN(hours) || diam < 0 || speed < 0 || eff < 0 || eff > 1 || hours < 0) {
      document.getElementById('wind_result').innerText = "Please enter valid values.";
      return;
    }
    var swept = Math.PI * Math.pow(diam/2, 2);
    var air_density = 1.225;
    var power = 0.5 * air_density * swept * Math.pow(speed,3) * eff / 1000;
    var energy = power * hours;
    document.getElementById('wind_result').innerText = "Daily Energy: " + energy.toFixed(2) + " kWh";
  }

  function calcHydro() {
    var flow = parseFloat(document.getElementById('hydro_flow').value);
    var head = parseFloat(document.getElementById('hydro_head').value);
    var eff = parseFloat(document.getElementById('hydro_eff').value);
    var hours = parseFloat(document.getElementById('hydro_hours').value);
    if (isNaN(flow) || isNaN(head) || isNaN(eff) || isNaN(hours) || flow < 0 || head < 0 || eff < 0 || eff > 1 || hours < 0) {
      document.getElementById('hydro_result').innerText = "Please enter valid values.";
      return;
    }
    var g = 9.81;
    var power = flow * head * g * eff / 1000;
    var energy = power * hours;
    document.getElementById('hydro_result').innerText = "Daily Energy: " + energy.toFixed(2) + " kWh";
  }

  function calcGeo() {
    var power = parseFloat(document.getElementById('geo_power').value);
    var eff = parseFloat(document.getElementById('geo_eff').value);
    var hours = parseFloat(document.getElementById('geo_hours').value);
    if (isNaN(power) || isNaN(eff) || isNaN(hours) || power < 0 || eff < 0 || eff > 1 || hours < 0) {
      document.getElementById('geo_result').innerText = "Please enter valid values.";
      return;
    }
    var energy = power * eff * hours;
    document.getElementById('geo_result').innerText = "Daily Energy: " + energy.toFixed(2) + " kWh";
  }

    container.innerHTML = `
      <div class="energy-calc-section">
        <h3>PV Solar Power</h3>
        <label>Panel Area (m²): <input type="number" id="pv_area" value="10"></label>
        <label>Panel Efficiency (0-1): <input type="number" step="0.01" id="pv_eff" value="0.18"></label>
        <label>Solar Irradiance (kW/m²): <input type="number" step="0.01" id="pv_irr" value="1"></label>
        <label>Sunlight Hours/Day: <input type="number" step="0.1" id="pv_hours" value="5"></label>
        <button onclick="calcPV()">Calculate</button>
        <div class="energy-calc-result" id="pv_result"></div>
      </div>
      <div class="energy-calc-section">
        <h3>Wind Turbine</h3>
        <label>Rotor Diameter (m): <input type="number" id="wind_diam" value="2"></label>
        <label>Average Wind Speed (m/s): <input type="number" step="0.1" id="wind_speed" value="5"></label>
        <label>Turbine Efficiency (0-1): <input type="number" step="0.01" id="wind_eff" value="0.35"></label>
        <label>Wind Hours/Day: <input type="number" step="0.1" id="wind_hours" value="8"></label>
        <button onclick="calcWind()">Calculate</button>
        <div class="energy-calc-result" id="wind_result"></div>
      </div>
      <div class="energy-calc-section">
        <h3>Hydropower</h3>
        <label>Flow Rate (m³/s): <input type="number" step="0.01" id="hydro_flow" value="0.1"></label>
        <label>Head (m): <input type="number" step="0.1" id="hydro_head" value="5"></label>
        <label>Turbine Efficiency (0-1): <input type="number" step="0.01" id="hydro_eff" value="0.6"></label>
        <label>Hours/Day: <input type="number" step="0.1" id="hydro_hours" value="24"></label>
        <button onclick="calcHydro()">Calculate</button>
        <div class="energy-calc-result" id="hydro_result"></div>
      </div>
      <div class="energy-calc-section">
        <h3>Geothermal</h3>
        <label>Thermal Power (kW): <input type="number" id="geo_power" value="5"></label>
        <label>Conversion Efficiency (0-1): <input type="number" step="0.01" id="geo_eff" value="0.4"></label>
        <label>Hours/Day: <input type="number" step="0.1" id="geo_hours" value="24"></label>
        <button onclick="calcGeo()">Calculate</button>
        <div class="energy-calc-result" id="geo_result"></div>
      </div>
    `;

function calcPV() {
    var area = parseFloat(document.getElementById('pv_area').value);
    var eff = parseFloat(document.getElementById('pv_eff').value);
    var irr = parseFloat(document.getElementById('pv_irr').value);
    var hours = parseFloat(document.getElementById('pv_hours').value);
    var energy = area * eff * irr * hours;
    document.getElementById('pv_result').innerText = "Daily Energy: " + energy.toFixed(2) + " kWh";
}

function calcWind() {
    var diam = parseFloat(document.getElementById('wind_diam').value);
    var speed = parseFloat(document.getElementById('wind_speed').value);
    var eff = parseFloat(document.getElementById('wind_eff').value);
    var hours = parseFloat(document.getElementById('wind_hours').value);
    var swept = Math.PI * Math.pow(diam/2, 2);
    var air_density = 1.225;
    var power = 0.5 * air_density * swept * Math.pow(speed,3) * eff / 1000;
    var energy = power * hours;
    document.getElementById('wind_result').innerText = "Daily Energy: " + energy.toFixed(2) + " kWh";
}

function calcHydro() {
    var flow = parseFloat(document.getElementById('hydro_flow').value);
    var head = parseFloat(document.getElementById('hydro_head').value);
    var eff = parseFloat(document.getElementById('hydro_eff').value);
    var hours = parseFloat(document.getElementById('hydro_hours').value);
    var g = 9.81;
    var power = flow * head * g * eff / 1000;
    var energy = power * hours;
    document.getElementById('hydro_result').innerText = "Daily Energy: " + energy.toFixed(2) + " kWh";
}

function calcGeo() {
    var power = parseFloat(document.getElementById('geo_power').value);
    var eff = parseFloat(document.getElementById('geo_eff').value);
    var hours = parseFloat(document.getElementById('geo_hours').value);
    var energy = power * eff * hours;
    document.getElementById('geo_result').innerText = "Daily Energy: " + energy.toFixed(2) + " kWh";
}