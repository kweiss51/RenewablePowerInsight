function calcPV() {
  const area = parseFloat(document.getElementById('pv_area').value);
  const eff = parseFloat(document.getElementById('pv_eff').value);
  const irr = parseFloat(document.getElementById('pv_irr').value);
  const hours = parseFloat(document.getElementById('pv_hours').value);
  const energy = area * eff * irr * hours;
  document.getElementById('pv_result').innerText = "Daily Energy: " + energy.toFixed(2) + " kWh";
}
