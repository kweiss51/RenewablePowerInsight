import feedparser
import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from energy_calculator.calculations import (
    calculate_pv_solar,
    calculate_wind_turbine,
    calculate_hydropower,
    calculate_geothermal,
)


st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}
.stButton>button {
    width: 100%;
}
</style>
""", unsafe_allow_html=True)



# --- Sidebar: Renewable Energy News RSS Feed ---
import re
st.sidebar.title("📰 Renewable Energy News")
feed_urls = [
    "https://www.sciencedaily.com/rss/earth_climate/renewable_energy.xml",
    "https://feeds.reuters.com/reuters/environment",
]
news_found = False
for feed_url in feed_urls:
    try:
        feed = feedparser.parse(feed_url)
        if not feed.entries:
            continue
        max_items = 5
        for entry in feed.entries[:max_items]:
            img_url = None
            # ScienceDaily: media_content or summary
            if 'media_content' in entry and entry.media_content:
                img_url = entry.media_content[0].get('url')
            elif 'summary' in entry and '<img' in entry.summary:
                match = re.search(r'<img[^>]+src=[\'\"]([^\'\"]+)', entry.summary)
                if match:
                    img_url = match.group(1)
            # Reuters: media_thumbnail or media_content
            elif 'media_thumbnail' in entry and entry.media_thumbnail:
                img_url = entry.media_thumbnail[0].get('url')
            if img_url:
                st.sidebar.image(img_url, width=80)
            st.sidebar.markdown(f"[{entry.title}]({entry.link})", unsafe_allow_html=True)
            st.sidebar.caption(entry.published if 'published' in entry else "")
        news_found = True
        break
    except Exception as e:
        continue
if not news_found:
    st.sidebar.info("No news found or unable to fetch news at this time.")

st.title("🌱 Home Renewable Energy Potential Calculator")
st.write("""
Enter your home or site details for each energy source to estimate your daily renewable energy potential. 
Use the expanders below to enter details for each source. Results will appear at the bottom.
""")



# Unit system selector (must be above all uses)
unit_system = st.radio("Select unit system:", ["SI (Metric)", "Imperial"], horizontal=True)
use_imperial = unit_system == "Imperial"

# --- Home Energy Need Section ---
st.markdown("---")
st.header("🏠 Home Energy Requirement")
city_defaults = {
    "New York": 30,
    "Los Angeles": 25,
    "Chicago": 28,
    "Houston": 35,
    "Miami": 33,
    "Denver": 27,
    "Phoenix": 32,
    "Seattle": 24,
    "Boston": 26,
    "Other (custom)": 30,
}
# Typical solar irradiance (kW/m²) and wind speed (m/s) for each city
city_solar_irradiance = {
    "New York": 0.16,
    "Los Angeles": 0.21,
    "Chicago": 0.17,
    "Houston": 0.19,
    "Miami": 0.20,
    "Denver": 0.22,
    "Phoenix": 0.23,
    "Seattle": 0.14,
    "Boston": 0.16,
    "Other (custom)": 0.18,
}
city_wind_speed = {
    "New York": 4.5,
    "Los Angeles": 3.5,
    "Chicago": 6.0,
    "Houston": 4.0,
    "Miami": 3.5,
    "Denver": 5.0,
    "Phoenix": 3.0,
    "Seattle": 3.5,
    "Boston": 4.0,
    "Other (custom)": 4.0,
}
city = st.selectbox("Select the city nearest to you:", list(city_defaults.keys()), index=0)
default_need = city_defaults[city]
default_irradiance = city_solar_irradiance[city]
default_wind_speed = city_wind_speed[city]
home_size = st.slider("Home Size (sq ft)", 500, 6000, 2000, step=100) if use_imperial else st.slider("Home Size (m²)", 50, 600, 185, step=5)
if use_imperial:
    base_need = st.number_input("Average Daily Energy Need (kWh)", min_value=5.0, value=float(default_need), help="Typical US home: 25-35 kWh/day. Adjust as needed.")
else:
    base_need = st.number_input("Average Daily Energy Need (kWh)", min_value=5.0, value=float(default_need), help="Typical EU home: 10-20 kWh/day. Adjust as needed.")

# --- Source Selection ---
st.markdown("---")
st.header("⚡ Select Energy Sources to Include")
use_solar = st.checkbox("PV Solar", value=True)
use_wind = st.checkbox("Wind Turbine", value=False)
use_hydro = st.checkbox("Hydropower", value=False)
use_geo = st.checkbox("Geothermal", value=False)

results = {}

if use_solar:
    with st.expander("☀️ PV Solar Power", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            if use_imperial:
                area = st.number_input("Panel Area (ft²)", min_value=0.0, value=107.6, help="Total area of your solar panels.")
                area_si = area * 0.092903  # ft² to m²
            else:
                area = st.number_input("Panel Area (m²)", min_value=0.0, value=10.0, help="Total area of your solar panels.")
                area_si = area
            efficiency = st.slider("Panel Efficiency (%)", 0, 100, 18, help="Typical range: 15-22%.") / 100
        with c2:
            if use_imperial:
                default_irradiance_imp = default_irradiance / 10.7639
                irradiance = st.number_input("Avg. Solar Irradiance (kW/ft²)", min_value=0.0, value=default_irradiance_imp, help="Average for your location. 0.014-0.023 is common. City default shown.")
                irradiance_si = irradiance / 10.7639  # kW/ft² to kW/m²
            else:
                irradiance = st.number_input("Avg. Solar Irradiance (kW/m²)", min_value=0.0, value=default_irradiance, help="Average for your location. 0.15-0.25 is common. City default shown.")
                irradiance_si = irradiance
            hours_sun = st.number_input("Avg. Sunlight Hours/Day", min_value=0.0, value=5.0, help="Average daily hours of full sun.")
        if st.button("Calculate PV Solar", key="solar"):
            solar_energy = calculate_pv_solar(area_si, efficiency, irradiance_si, hours_sun)
            results["PV Solar"] = solar_energy
        elif "PV Solar" in results:
            del results["PV Solar"]

if use_wind:
    with st.expander("💨 Wind Turbine", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            if use_imperial:
                rotor = st.number_input("Rotor Diameter (ft)", min_value=0.0, value=6.56, help="Diameter of the wind turbine rotor.")
                rotor_si = rotor * 0.3048  # ft to m
            else:
                rotor = st.number_input("Rotor Diameter (m)", min_value=0.0, value=2.0, help="Diameter of the wind turbine rotor.")
                rotor_si = rotor
            wind_eff = st.slider("Turbine Efficiency (%)", 0, 100, 30, help="Typical range: 25-45%.") / 100
        with c2:
            if use_imperial:
                default_wind_speed_imp = default_wind_speed / 0.44704
                wind_speed = st.number_input("Avg. Wind Speed (mph)", min_value=0.0, value=default_wind_speed_imp, help="Average wind speed at your site. City default shown.")
                wind_speed_si = wind_speed * 0.44704  # mph to m/s
            else:
                wind_speed = st.number_input("Avg. Wind Speed (m/s)", min_value=0.0, value=default_wind_speed, help="Average wind speed at your site. City default shown.")
                wind_speed_si = wind_speed
            wind_hours = st.number_input("Avg. Wind Hours/Day", min_value=0.0, value=8.0, help="Average daily hours with usable wind.")
        if st.button("Calculate Wind Turbine", key="wind"):
            wind_energy = calculate_wind_turbine(rotor_si, wind_speed_si, wind_eff, wind_hours)
            results["Wind Turbine"] = wind_energy
        elif "Wind Turbine" in results:
            del results["Wind Turbine"]

if use_hydro:
    with st.expander("💧 Hydropower", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            if use_imperial:
                flow = st.number_input("Flow Rate (ft³/s)", min_value=0.0, value=1.77, help="Stream or river flow rate.")
                flow_si = flow * 0.0283168  # ft³/s to m³/s
            else:
                flow = st.number_input("Flow Rate (m³/s)", min_value=0.0, value=0.05, help="Stream or river flow rate.")
                flow_si = flow
            hydro_eff = st.slider("Hydro Efficiency (%)", 0, 100, 60, help="Typical range: 50-80%.") / 100
        with c2:
            if use_imperial:
                head = st.number_input("Head (ft)", min_value=0.0, value=6.56, help="Vertical drop (height difference) in feet.")
                head_si = head * 0.3048  # ft to m
            else:
                head = st.number_input("Head (m)", min_value=0.0, value=2.0, help="Vertical drop (height difference) in meters.")
                head_si = head
            hydro_hours = st.number_input("Avg. Hydro Hours/Day", min_value=0.0, value=24.0, help="Hours per day with water flow.")
        if st.button("Calculate Hydropower", key="hydro"):
            hydro_energy = calculate_hydropower(flow_si, head_si, hydro_eff, hydro_hours)
            results["Hydropower"] = hydro_energy
        elif "Hydropower" in results:
            del results["Hydropower"]

if use_geo:
    with st.expander("🌋 Geothermal", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            if use_imperial:
                geothermal_power = st.number_input("Thermal Power Available (BTU/hr)", min_value=0.0, value=17060.0, help="Thermal power available for conversion.")
                geothermal_power_si = geothermal_power * 0.000293071  # BTU/hr to kW
            else:
                geothermal_power = st.number_input("Thermal Power Available (kW)", min_value=0.0, value=5.0, help="Thermal power available for conversion.")
                geothermal_power_si = geothermal_power
            geothermal_eff = st.slider("Conversion Efficiency (%)", 0, 100, 40, help="Typical range: 10-45%.") / 100
        with c2:
            geo_hours = st.number_input("Avg. Geothermal Hours/Day", min_value=0.0, value=24.0, help="Hours per day geothermal is available.")
        if st.button("Calculate Geothermal", key="geo"):
            geo_energy = calculate_geothermal(geothermal_power_si, geothermal_eff, geo_hours)
            results["Geothermal"] = geo_energy
        elif "Geothermal" in results:
            del results["Geothermal"]


# --- Results and Comparison ---
if results:
    st.markdown("---")
    st.subheader("🔋 Estimated Daily Energy Potential")
    total_energy = sum(results.values())
    for source, energy in results.items():
        st.success(f"{source}: {energy:.2f} kWh per day")
    st.info(f"**Total Renewable Energy: {total_energy:.2f} kWh per day**")
    st.info(f"**Your Home Needs: {base_need:.2f} kWh per day**")
    if total_energy >= base_need:
        st.success("✅ You can generate enough renewable energy to power your home!")
    else:
        st.error(f"❌ You need {base_need - total_energy:.2f} kWh more per day to fully power your home.")
