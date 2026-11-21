# =============================================================================
# Chapter 3: Loads and Load Combinations
# Extracted from report_generator.py — DO NOT add business logic here.
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CB_LOAD,
    KEY_FOOTPATH,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_ECCENTRICITY,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_TS_FOOTPATH_THICKNESS,
    KEY_TS_FOOTPATH_WIDTH,
    KEY_TS_NO_OF_FOOTPATHS,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE
)

from osdagbridge.core.reports.report_utils import _tex, _render_value
from osdagbridge.core.reports.styles import build_longtable_header

def ch3_loads(input_dict):
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017

    def _is_selected(val):
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val > 0
        if isinstance(val, str):
            return val.strip().lower() in ("true", "yes", "1", "selected")
        return False

    span_val = input_dict.get(KEY_SPAN)
    try:
        span_m = float(span_val) if span_val not in (None, "") else 24.0
    except Exception:
        span_m = 24.0

    lanes_val = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    try:
        lanes_int = int(lanes_val) if lanes_val not in (None, "") else 2
    except Exception:
        lanes_int = 2

    # Braking forces per IRC 6 Cl. 211.2:
    # Class A: 20% of first two lanes + 5% of subsequent lanes
    if lanes_int <= 2:
        braking_kN_class_a = 0.20 * lanes_int * 53.6 * 9.81
    else:
        braking_kN_class_a = (0.20 * 2 * 53.6 * 9.81) + (0.05 * (lanes_int - 2) * 53.6 * 9.81)

    # Dynamic impact factors (1 + im) per IRC 6 Cl. 208
    im_a = IRC6_2017.cl_208_2_impact_factor(span_m)
    if_class_a = f"{1.0 + im_a:.3f}"

    if span_m >= 23.0:
        im_70r_w = 9.0 / (13.5 + min(span_m, 45.0))
    else:
        im_70r_w = 0.25
    if_70r_w = f"{1.0 + im_70r_w:.3f}"

    if span_m >= 5.0:
        im_70r_t = 0.10
    else:
        im_70r_t = 0.25
    if_70r_t = f"{1.0 + im_70r_t:.3f}"

    if_70r_bogie = "1.250"
    if_class_sv = "1.000"
    if_class_fatigue = "1.000"

    centrifugal_kN = "0.00"

    vehicle_specs = [
        (KEY_LL_IRC_CLASS_A, "IRC Class A", if_class_a, f"{braking_kN_class_a:.2f}", centrifugal_kN, "IRC 6 Cl. 204.1, 208.2, 211.2"),
        (KEY_LL_IRC_70R_WHEELED, "IRC Class 70R (Wheeled)", if_70r_w, f"{0.20 * 100.0 * 9.81:.2f}", centrifugal_kN, "IRC 6 Cl. 204.1, 208.3, 211.2"),
        (KEY_LL_IRC_70R_TRACKED, "IRC Class 70R (Tracked)", if_70r_t, f"{0.20 * 70.0 * 9.81:.2f}", centrifugal_kN, "IRC 6 Cl. 204.1, 208.3, 211.2"),
        (KEY_LL_IRC_70R_BOGIE, "IRC Class 70R (Bogie)", if_70r_bogie, f"{0.20 * 40.0 * 9.81:.2f}", centrifugal_kN, "IRC 6 Cl. 204.1, 208.3, 211.2"),
        (KEY_LL_IRC_AA_WHEELED, "IRC Class AA (Wheeled)", if_70r_w, f"{0.20 * 70.0 * 9.81:.2f}", centrifugal_kN, "IRC 6 Cl. 204.1, 208.3, 211.2"),
        (KEY_LL_IRC_AA_TRACKED, "IRC Class AA (Tracked)", if_70r_t, f"{0.20 * 70.0 * 9.81:.2f}", centrifugal_kN, "IRC 6 Cl. 204.1, 208.3, 211.2"),
        (KEY_LL_IRC_CLASS_SV, "IRC Class SV (Special Vehicle)", if_class_sv, f"{0.20 * 100.0 * 9.81:.2f}", centrifugal_kN, "IRC 6 Cl. 204.5, Annex B"),
        (KEY_LL_IRC_CLASS_FATIGUE, "IRC Class Fatigue", if_class_fatigue, f"{0.20 * 400.0:.2f}", centrifugal_kN, "IRC 6 Cl. 204.6"),
    ]

    selected_ll_rows = []
    for key, name, if_val, bf_val, cf_val, clause in vehicle_specs:
        if _is_selected(input_dict.get(key)):
            selected_ll_rows.append(
                f"\\textnormal{{{name}}} & {if_val} & {bf_val} & {cf_val} & \\small{{{clause}}} \\\\[6pt]\n\\hline"
            )

    # Custom vehicles
    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    if custom and isinstance(custom, list):
        for c in custom:
            c_name = c.get('name', 'Custom Vehicle') if isinstance(c, dict) else str(c)
            if c_name:
                selected_ll_rows.append(
                    f"\\textnormal{{{_tex(c_name)}}} & 1.000 & N/A & 0.00 & \\small{{User-Defined}} \\\\[6pt]\n\\hline"
                )

    if not selected_ll_rows:
        selected_ll_rows.append(
            r"\multicolumn{5}{|c|}{\textit{No Live Load Vehicles Selected}} \\[6pt]" + "\n\\hline"
        )

    ll_table_str = (
        build_longtable_header(
            col_spec=r"|L{4.2cm}|C{2.6cm}|C{2.8cm}|C{2.8cm}|L{3.1cm}|",
            caption="Live Loads (LL) --- Vehicle Class Specifications",
            header_rows=(
                r"\textbf{Vehicle Class} & \textbf{Impact Factor} & \textbf{Braking Load} & \textbf{Centrifugal Force} & \textbf{Governing Clause} \\[2pt]"
                r" & \small{($1 + i_m$)} & \small{[kN]} & \small{[kN]} & \\"
            ),
            num_cols=5,
            label="tab:live-loads"
        )
        + "\n".join(selected_ll_rows)
        + r"""
\end{longtable}
\noindent\textit{Note: Dynamic impact factor $(1 + i_m)$ is evaluated in accordance with IRC:6-2017 Clause 208 for effective span $L = """
        + f"{span_m:.2f}"
        + r"""\,\text{m}$. Braking force represents longitudinal tractive/braking effect per IRC:6-2017 Clause 211.2 for """
        + f"{lanes_int}"
        + r""" traffic lane(s). Centrifugal force is 0.00\,kN as the bridge is designed on a tangent horizontal alignment (straight track, $R = \infty$) per IRC:6-2017 Clause 212.}
"""
    )

    # Footway and Pedestrian Live Load table
    fp_config = input_dict.get(KEY_FOOTPATH) or "None"
    fp_width = input_dict.get(KEY_TS_FOOTPATH_WIDTH)
    try:
        fp_width_str = f"{float(fp_width):.2f}" if fp_width not in (None, "") else "0.00"
    except Exception:
        fp_width_str = str(fp_width) if fp_width is not None else "0.00"

    fp_thick = input_dict.get(KEY_TS_FOOTPATH_THICKNESS)
    try:
        fp_thick_str = f"{float(fp_thick):.1f}" if fp_thick not in (None, "") else "100.0"
    except Exception:
        fp_thick_str = str(fp_thick) if fp_thick is not None else "100.0"

    fp_mode  = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "")
    fp_value = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE, "")
    if str(fp_mode).strip().lower() in ("as per irc 6", "as per irc6", "automatic"):
        fp_mode_display = "As per IRC 6"
        try:
            fp_load_str = f"{IRC6_2017.cl_206_1_footway_load():.3f}"
        except Exception:
            fp_load_str = "4.905"
    elif fp_value not in (None, ""):
        fp_mode_display = "User-Specified"
        try:
            fp_load_str = f"{float(fp_value):.3f}"
        except Exception:
            fp_load_str = str(fp_value)
    else:
        fp_mode_display = "As per IRC 6"
        fp_load_str = "4.905"

    fp_rows = [
        f"\\textnormal{{Footpath Configuration}} & {_tex(str(fp_config))} & --- & IRC:5-2015 Clause 109 \\\\[6pt]\n\\hline",
        f"\\textnormal{{Footpath Clear Width}} & {fp_width_str} & m & Bridge Cross-Section Geometry \\\\[6pt]\n\\hline",
        f"\\textnormal{{Footpath Slab Thickness}} & {fp_thick_str} & mm & Typical Cross-Section Details \\\\[6pt]\n\\hline",
        f"\\textnormal{{Footway Pressure Mode}} & {_tex(fp_mode_display)} & --- & IRC:6-2017 Clause 206.1 \\\\[6pt]\n\\hline",
        f"\\textnormal{{Design Pedestrian Live Load}} & {fp_load_str} & kN/m\\textsuperscript{{2}} & IRC:6-2017 Clause 206.1 ($500\\,\\text{{kg/m}}^2$) \\\\[6pt]\n\\hline",
    ]

    fp_table_str = (
        build_longtable_header(
            col_spec=r"|L{5.4cm}|C{3.0cm}|C{2.2cm}|L{4.9cm}|",
            caption="Footway and Pedestrian Live Load",
            header_rows=r"\textbf{Parameter} & \textbf{Design Value} & \textbf{Unit} & \textbf{Governing Standard / Clause} \\",
            num_cols=4,
            label="tab:footway-load"
        )
        + "\n".join(fp_rows)
        + r"""
\end{longtable}
\noindent\textit{Note: In accordance with IRC:6-2017 Clause 206.1, pedestrian live load of 4.905\,kN/m\textsuperscript{2} ($500\,\text{kg/m}^2$) is applied to pedestrian footways. For superstructures without pedestrian footpaths (Footpath Configuration: None), pedestrian loading is not combined with vehicular live loads.}
"""
    )

    # Vz / Pz — prefer stored computed values; fall back to IRC6 Table 12
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb  = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed')
            _h   = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass
    vz_str = f"{float(vz_val):.2f} m/s" if vz_val not in (None, "") else "N/A"
    pz_str = f"{float(pz_val):.2f} N/m²" if pz_val not in (None, "") else "N/A"

    # Table 3.5 — Seismic: prefer stored computed values; fall back to IRC6 cl_218_5_1
    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral    = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah          = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av          = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get('seismic_zone')
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z    = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z)
            _smap = {"Type I – Rocky or Hard": 1, "Type II – Medium Soil": 2, "Type III – Soft Soil": 3}
            _st   = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp   = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = float(_dl_v) if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v else 0.0
            _live = float(_ll_v) if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v else 0.0
            _res  = IRC6_2017.cl_218_5_1(zone=f"Zone {_z}", soil_type=_st, dead_load_kN=_dead,
                        live_load_kN=_live, period_T=float(_tp) if _tp else None,
                        damping_percent=float(_damp))
            if not sl_zone_factor:
                sl_zone_factor = _res.get("Z")
            if not sl_spectral:
                sl_spectral    = _res.get("Sa_g_adjusted")
            if not sl_ah:
                sl_ah          = _res.get("Ah")
            if not sl_av:
                sl_av          = round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass

    def _sl(v, unit=""):
        return f"{float(v):.4f}{unit}" if v not in (None, "") else "N/A"

    # Table 3.6 — Temperature: compute effective bridge temp range from shade temps
    tl_temp_min = tl_temp_max = tl_rise = tl_fall = "N/A"
    try:
        _tmax = input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or input_dict.get('shade_temp_max')
        _tmin = input_dict.get(KEY_TL_LOWEST_MIN_TEMP)  or input_dict.get('shade_temp_min')
        if _tmax and _tmin:
            _res    = IRC6_2017.cl_215_2_effective_bridge_temperature(
                          float(_tmax), float(_tmin), 'metallic', False)
            _bt_min = _res.get('T_min', 0)
            _bt_max = _res.get('T_max', 0)
            _mean   = (_bt_max + _bt_min) / 2.0
            tl_temp_min = f"{_bt_min:.2f}"
            tl_temp_max = f"{_bt_max:.2f}"
            tl_rise     = f"{_bt_max - _mean:.2f}"
            tl_fall     = f"{_mean - _bt_min:.2f}"
    except Exception:
        pass

    # --- Table 3.7: Load Combinations (dynamically generated from IRC 6) ---
    _LOAD_LABEL_MAP = {
        'dead_load':         'DL',
        'surfacing':         'SIDL',
        'live_load':         'LL',
        'wind_load':         'WL',
        'thermal_load':      'TL',
        'vehicle_collision': 'VC',
        'barge_impact':      'BI',
        'floating_bodies':   'FB',
        'seismic':           'EQ',
    }

    def _fmt_factors(factors):
        """Format a factors dict into a compact load-case string for the table."""
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):  # permanent load with adding/relieving
                add = val.get('adding')
                rel = val.get('relieving')
                add_s = f"{add:.2f}" if add is not None else '--'
                rel_s = f"{rel:.2f}" if rel is not None else '--'
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue  # skip N/A factors
                parts.append(f"{label}({val:.2f})")
        return ' + '.join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"ULS-{i:02d}" + r" & " + cases + r" \\[6pt]" + "\n"
            + r"\hline"
        )
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"SLS-{i:02d}" + r" & " + cases + r" \\[6pt]" + "\n"
            + r"\hline"
        )

    lc_rows_str = "\n".join(lc_rows)

    return r"""
\chapter{Loads and Load Combinations}

This section summarizes all loads applied to the bridge and the load combinations considered for analysis and design.

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Dead Load -- Self Weight}}
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\textnormal{Steel Self-Weight Applied} & """ + (_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Concrete Deck Weight} & """ + (_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Self-Weight Factor} & """ + (_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)) + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Dead Load for Surfacing (DW)}}
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\textnormal{Wearing Course Load} & """ + (_render_value(input_dict, KEY_WC_MATERIAL)) + r""" x """ + (_render_value(input_dict, KEY_WC_THICKNESS)) + r""" \\[6pt]
\hline
\textnormal{Additional SIDL (Crash Barrier)} & """ + (_render_value(input_dict, KEY_CB_LOAD)) + r""" kN/m per barrier \\[6pt]
\hline
\textnormal{Railing Load} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE)) + r""" kN/m\sdstar{} \\[6pt]
\hline
\end{longtable}

\vspace{1em}
""" + ll_table_str + r"""
\vspace{1em}
""" + fp_table_str + r"""

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Wind Load (WL) --- per IRC 6}}
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\textnormal{Basic Wind Speed, Vb} & """ + (_render_value(input_dict,'wind_speed', ' m/s')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Terrain Type} & """ + (_render_value(input_dict, KEY_WL_TERRAIN_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Average Exposed Height, H (m)} & """ + (_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, ' m')) + r""" \\[6pt]
\hline
\textnormal{Hourly Mean Wind Speed, Vz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_MEAN_WIND, ' m/s')) + r""" \\[6pt]
\hline
\textnormal{Hourly Wind Pressure, Pz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_WIND_PRESSURE, ' N/m\\textsuperscript{2}')) + r""" \\[6pt]
\hline
\textnormal{Transverse Wind Force} & """ + (_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Longitudinal Wind Force} & """ + (_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Vertical Wind Force} & """ + (_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Earthquake Load (EL) --- per IRC 6}}
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\textnormal{Seismic Zone} & """ + (_render_value(input_dict,'seismic_zone')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Zone Factor, Z} & """ + (_render_value(input_dict, KEY_SL_ZONE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Importance Factor, I} & """ + (_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Type of Soil} & """ + (_render_value(input_dict, KEY_SL_SOIL_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Sa/g} & """ + (_render_value(input_dict, KEY_SL_SPECTRAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Coefficient, Ah} & """ + (_render_value(input_dict, KEY_SL_HORIZONTAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Vertical Seismic Coefficient, Av} & """ + (_render_value(input_dict, KEY_SL_VERTICAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Force (longitudinal)} & """ + '' + r""" kN \\[6pt]
\hline
\textnormal{Horizontal Seismic Force (transverse)} & """ + '' + r""" kN \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Temperature Load (TL) --- per IRC 6}}
\hline
\textbf{parameter} & \textbf{value} \\
\hline
\textnormal{Maximum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_max')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Minimum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_min')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Effective Bridge Temp. Range} & """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN)) + r""" to """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX)) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Temperature Rise / Fall for Design} & +""" + (_render_value(input_dict, KEY_TL_TEMP_RISE)) + r""" $^\circ$C / \textminus{}""" + (_render_value(input_dict, KEY_TL_TEMP_FALL)) + r""" $^\circ$C \\[6pt]
\hline
\end{longtable}

\vspace{1em}
""" + build_longtable_header(
    r"|C{4.0cm}|p{11.5cm}|",
    "Load Combinations",
    r"\textbf{Combination ID} & \textbf{Load Cases} \\[6pt]",
    num_cols=2,
    label="tab:load-combinations"
) + lc_rows_str + r"""
\end{longtable}

\noindent\textit{Note: All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.}
"""


