# Climate and Weather

- Climate lives on coarse lat/long grids per body: `ClimateGrid { body, width, height, mean_temp_K, mean_precip, mean_humidity }` (Q16.16 everywhere; temps are `TempK`). Fields are registered via `climate_mean_temp`, `climate_mean_precip`, `climate_mean_humidity`.
- Weather is a lower-resolution surface grid per body: `WeatherGrid { pressure, temp, humidity, wind_u, wind_v, cloud }` (all Q16.16; pressure and wind share the same fixed-point scale). Cloud cover has a dedicated field `cloud_cover`.
- Sources: orbit/tilt/spin and body constants seed climate. `dclimate_init_grid` uses `dbody` orbital data, albedo, and greenhouse factors; latitude bands cool toward the poles and heights reduce temperature via a fixed lapse rate.
- Queries: `dclimate_sample_at_tile` / `dclimate_sample_at_lat_lon` fetch mean values for a tile or lat/long/height; height is a Q16.16 metres input.
- Weather stepping: `dweather_init_grid` builds grids, `dweather_seed_from_climate` pulls the climate means into the initial state, and `dweather_step(body, ticks)` advances pressure/temp/humidity/cloud with simple deterministic wiggles and pressure-derived winds.
- Tile projection: `dweather_get_surface_weather_at_tile` and `dweather_project_fields_for_tile` interpolate grid cells to tile fields; callers use `dfield_q16_to_*` codecs to write `air_pressure`, `air_temp`, `humidity`, `wind_u`, `wind_v`, and `cloud_cover`.
- Gameplay feeds: precipitation output goes to `dhydro_add_rainfall`, wind feeds turbines/vehicles, and cloud cover gates solar exposure and visuals.
- Policy: integer-only fixed point; no private 3D arrays. All tile-level fields flow through `dfield` handles so the shared field registry owns the storage layout.
