# Energy calculation logic for each renewable source

def calculate_pv_solar(area_m2, efficiency, solar_irradiance, hours):
    """
    area_m2: Area of solar panels in square meters
    efficiency: Panel efficiency (0-1)
    solar_irradiance: Average solar irradiance (kW/m^2)
    hours: Average sunlight hours per day
    Returns daily energy in kWh
    """
    return area_m2 * efficiency * solar_irradiance * hours

def calculate_wind_turbine(rotor_diameter, wind_speed, efficiency, hours):
    """
    rotor_diameter: Diameter of the rotor in meters
    wind_speed: Average wind speed in m/s
    efficiency: Turbine efficiency (0-1)
    hours: Average wind hours per day
    Returns daily energy in kWh
    """
    swept_area = 3.1416 * (rotor_diameter / 2) ** 2
    air_density = 1.225  # kg/m^3
    power = 0.5 * air_density * swept_area * (wind_speed ** 3) * efficiency / 1000  # kW
    return power * hours

def calculate_hydropower(flow_rate, head, efficiency, hours):
    """
    flow_rate: Water flow in m^3/s
    head: Height difference in meters
    efficiency: Turbine efficiency (0-1)
    hours: Average hours per day
    Returns daily energy in kWh
    """
    g = 9.81  # m/s^2
    power = flow_rate * head * g * efficiency / 1000  # kW
    return power * hours

def calculate_geothermal(thermal_power_kw, efficiency, hours):
    """
    thermal_power_kw: Available thermal power in kW
    efficiency: Conversion efficiency (0-1)
    hours: Average hours per day
    Returns daily energy in kWh
    """
    return thermal_power_kw * efficiency * hours
