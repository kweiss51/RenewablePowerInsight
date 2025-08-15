"""
Renewable Power Calculator Module
Provides calculations for solar and wind power potential
"""

def calculate_solar_potential(consumption: float, location: str) -> dict:
    """
    Calculate solar power potential based on consumption and location
    
    Args:
        consumption: Monthly energy consumption in kWh
        location: ZIP code or location identifier
        
    Returns:
        Dictionary containing solar power calculations
    """
    # This would normally use location data to get actual solar insolation values
    # For now using example values
    avg_sun_hours = 5.5  # Average sun hours per day
    panel_efficiency = 0.20  # 20% efficient panels
    panel_size = 1.6  # Size in square meters
    panel_rating = 0.250  # 250W panel
    
    daily_energy_needed = consumption / 30  # Convert monthly to daily
    panels_needed = daily_energy_needed / (avg_sun_hours * panel_rating)
    
    return {
        "panels_needed": round(panels_needed),
        "total_area": round(panels_needed * panel_size, 2),
        "estimated_cost": round(panels_needed * 500, 2),  # Example cost of $500 per panel
        "payback_period": round((panels_needed * 500) / (consumption * 0.12 * 12), 1)  # Years
    }

def calculate_wind_potential(consumption: float, location: str) -> dict:
    """
    Calculate wind power potential based on consumption and location
    
    Args:
        consumption: Monthly energy consumption in kWh
        location: ZIP code or location identifier
        
    Returns:
        Dictionary containing wind power calculations
    """
    # This would normally use location data to get actual wind speed values
    avg_wind_speed = 5.0  # m/s
    turbine_efficiency = 0.35
    air_density = 1.225  # kg/m³
    
    # Calculate required turbine size
    daily_energy = consumption / 30
    hours_at_rated = 6  # Assumed hours at rated power per day
    
    # Power = 0.5 * air density * swept area * wind speed³ * efficiency
    required_power = daily_energy / hours_at_rated
    swept_area = (required_power * 2) / (air_density * (avg_wind_speed ** 3) * turbine_efficiency)
    
    # Convert swept area to rotor diameter
    rotor_diameter = (swept_area * 4 / 3.14159) ** 0.5
    
    return {
        "turbine_size_kw": round(required_power / 1000, 1),
        "rotor_diameter": round(rotor_diameter, 1),
        "estimated_cost": round(required_power * 2000, 2),  # Example cost of $2000 per kW
        "payback_period": round((required_power * 2000) / (consumption * 0.12 * 12), 1)  # Years
    }

def estimate_co2_reduction(energy_kwh: float) -> float:
    """
    Estimate CO2 emissions reduction
    
    Args:
        energy_kwh: Amount of renewable energy generated in kWh
        
    Returns:
        CO2 reduction in kg
    """
    # Average CO2 emissions per kWh (varies by region)
    co2_per_kwh = 0.85  # kg CO2 per kWh
    return energy_kwh * co2_per_kwh
