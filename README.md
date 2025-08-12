# Energy Calculator Module

This folder contains the Python logic for calculating the daily energy potential from four renewable sources:

- **PV Solar Power**
- **Wind Turbine**
- **Hydropower**
- **Geothermal**

## Usage

Import the functions from `calculations.py` in your Python code:

```python
from calculations import (
    calculate_pv_solar,
    calculate_wind_turbine,
    calculate_hydropower,
    calculate_geothermal
)

# Example usage:
pv_energy = calculate_pv_solar(area_m2=10, efficiency=0.18, solar_irradiance=1, hours=5)
print(f"PV Solar Daily Energy: {pv_energy} kWh")
```

## Functions

- `calculate_pv_solar(area_m2, efficiency, solar_irradiance, hours)`
- `calculate_wind_turbine(rotor_diameter, wind_speed, efficiency, hours)`
- `calculate_hydropower(flow_rate, head, efficiency, hours)`
- `calculate_geothermal(thermal_power_kw, efficiency, hours)`

See the docstrings in `calculations.py` for parameter details.

---

## License

MIT
