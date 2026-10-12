"""
prepare_sample_data.py
Generates a realistic, domain-authentic sample of the Building Data Genome 2 (BDG2)
dataset for hands-on exercises in the Python for Data Science curriculum.
"""
import os
import numpy as np
import pandas as pd

def generate_bdg2_sample():
    os.makedirs("data", exist_ok=True)
    print("Generating Building Data Genome 2 (BDG2) sample dataset...")

    # 1. Metadata for 10 representative buildings across 3 sites
    buildings = [
        {"building_id": "Office_Alicia", "site_id": "Bear", "primary_space_usage": "Office", "sqm": 8500, "year_built": 1998, "timezone": "US/Eastern"},
        {"building_id": "Office_Bob", "site_id": "Bear", "primary_space_usage": "Office", "sqm": 12400, "year_built": 2005, "timezone": "US/Eastern"},
        {"building_id": "Education_Claire", "site_id": "Bear", "primary_space_usage": "Education", "sqm": 5200, "year_built": 1982, "timezone": "US/Eastern"},
        {"building_id": "Education_Daniel", "site_id": "Fox", "primary_space_usage": "Education", "sqm": 7100, "year_built": 2012, "timezone": "US/Pacific"},
        {"building_id": "Lodging_Elena", "site_id": "Fox", "primary_space_usage": "Lodging", "sqm": 9800, "year_built": 2016, "timezone": "US/Pacific"},
        {"building_id": "Office_Frank", "site_id": "Fox", "primary_space_usage": "Office", "sqm": 14200, "year_built": 2001, "timezone": "US/Pacific"},
        {"building_id": "Laboratory_Grace", "site_id": "Eagle", "primary_space_usage": "Laboratory", "sqm": 6300, "year_built": 2010, "timezone": "US/Central"},
        {"building_id": "Education_Henry", "site_id": "Eagle", "primary_space_usage": "Education", "sqm": 8900, "year_built": 1974, "timezone": "US/Central"},
        {"building_id": "Lodging_Ivy", "site_id": "Eagle", "primary_space_usage": "Lodging", "sqm": 4500, "year_built": 1995, "timezone": "US/Central"},
        {"building_id": "Office_Jack", "site_id": "Eagle", "primary_space_usage": "Office", "sqm": 11000, "year_built": 2019, "timezone": "US/Central"},
    ]
    df_meta = pd.DataFrame(buildings)
    meta_path = os.path.join("data", "building_metadata.csv")
    df_meta.to_csv(meta_path, index=False)
    print(f"[OK] Created metadata: {meta_path} ({len(df_meta)} buildings)")

    # 2. Hourly Weather data for 1 full year (8760 hours in 2023)
    np.random.seed(42)
    timestamps = pd.date_range("2023-01-01 00:00:00", "2023-12-31 23:00:00", freq="h")
    n_hours = len(timestamps)

    weather_frames = []
    for site in ["Bear", "Fox", "Eagle"]:
        # Realistic seasonal temperature curve (sine wave across 365 days + diurnal daily cycle)
        day_of_year = timestamps.dayofyear.values
        hour_of_day = timestamps.hour.values
        
        base_annual = 15.0 + 12.0 * np.sin(2 * np.pi * (day_of_year - 100) / 365)
        diurnal = 6.0 * np.sin(2 * np.pi * (hour_of_day - 8) / 24)
        noise = np.random.normal(0, 2.5, size=n_hours)
        air_temp = np.round(base_annual + diurnal + noise, 1)

        humidity = np.clip(np.round(65.0 - 1.5 * diurnal + np.random.normal(0, 5, size=n_hours), 1), 15.0, 100.0)
        dew_temp = np.round(air_temp - ((100.0 - humidity) / 5.0), 1)
        wind_speed = np.clip(np.round(np.random.exponential(3.2, size=n_hours), 1), 0.0, 25.0)

        site_df = pd.DataFrame({
            "timestamp": timestamps,
            "site_id": site,
            "air_temperature": air_temp.astype(np.float32),
            "dew_temperature": dew_temp.astype(np.float32),
            "relative_humidity": humidity.astype(np.float32),
            "wind_speed": wind_speed.astype(np.float32)
        })
        weather_frames.append(site_df)

    df_weather = pd.concat(weather_frames, ignore_index=True)
    weather_path = os.path.join("data", "weather.parquet")
    df_weather.to_parquet(weather_path, engine="pyarrow", compression="snappy")
    weather_mb = df_weather.memory_usage(deep=True).sum() / (1024**2)
    print(f"[OK] Created weather: {weather_path} ({len(df_weather):,} rows, {weather_mb:.2f} MB)")

    # 3. Telemetry for 10 buildings across 2023
    telemetry_frames = []
    weather_lookup = {s: df_weather[df_weather["site_id"] == s].set_index("timestamp")["air_temperature"].values for s in ["Bear", "Fox", "Eagle"]}

    for b in buildings:
        b_id = b["building_id"]
        site = b["site_id"]
        sqm = b["sqm"]
        usage = b["primary_space_usage"]
        site_temps = weather_lookup[site]

        # Base load scales with building floor area
        base_kw = (sqm / 100.0) * 1.2
        hour = timestamps.hour.values
        is_weekend = timestamps.dayofweek.values >= 5

        # Occupancy schedule multiplier
        if usage == "Office":
            occupancy = np.where(is_weekend, 0.25, np.where((hour >= 7) & (hour <= 19), 1.0, 0.35))
        elif usage == "Education":
            occupancy = np.where(is_weekend, 0.15, np.where((hour >= 8) & (hour <= 17), 0.95, 0.20))
        elif usage == "Laboratory":
            occupancy = np.where((hour >= 8) & (hour <= 18), 1.0, 0.75) # labs run 24/7 baseline
        else: # Lodging
            occupancy = np.where((hour >= 18) | (hour <= 9), 0.95, 0.50)

        # Cooling / Heating degree effect
        cooling_load = np.maximum(site_temps - 18.0, 0.0) * (sqm / 1000.0) * 0.8
        noise = np.random.normal(0, base_kw * 0.05, size=n_hours)
        
        elec_kw = np.clip(np.round(base_kw * occupancy + cooling_load + noise, 2), 0.5, None)

        b_df = pd.DataFrame({
            "timestamp": timestamps,
            "building_id": b_id,
            "meter": "electricity",
            "reading_kw": elec_kw.astype(np.float32)
        })
        telemetry_frames.append(b_df)

    df_telemetry = pd.concat(telemetry_frames, ignore_index=True)
    telemetry_path = os.path.join("data", "building_telemetry.parquet")
    df_telemetry.to_parquet(telemetry_path, engine="pyarrow", compression="snappy")
    telemetry_mb = df_telemetry.memory_usage(deep=True).sum() / (1024**2)
    print(f"[OK] Created telemetry: {telemetry_path} ({len(df_telemetry):,} rows, {telemetry_mb:.2f} MB)")

if __name__ == "__main__":
    generate_bdg2_sample()
