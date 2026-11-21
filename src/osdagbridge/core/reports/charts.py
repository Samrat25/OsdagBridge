# =============================================================================
# OsdagBridge — Report Charts Generator
# =============================================================================
"""
Matplotlib chart generation module for bridge design reports.
Follows formatting, colors, and typography defined in styles.py.
Uses the Agg backend for headless rendering.
"""

import os
import tempfile
os.environ.setdefault('MPLCONFIGDIR', os.path.join(tempfile.gettempdir(), 'matplotlib_osdag'))
import logging
from typing import Dict, Any, Optional

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from osdagbridge.core.reports.styles import (
    setup_matplotlib_style,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_ACCENT,
    COLOR_OSDAG_GREEN,
    COLOR_PASS,
    COLOR_FAIL,
    COLOR_WARNING,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    CHART_CONFIG
)

from osdagbridge.core.utils.common import (
    KEY_SPAN,
    KEY_TS_NO_OF_GIRDERS,
    KEY_TS_GIRDER_SPACING,
    KEY_TS_DECK_THICKNESS,
    KEY_MP_ED_TYPE,
    KEY_DD_M_ULS_SAG,
    KEY_DD_MU_BOT,
    KEY_DD_M_ULS_HOG,
    KEY_DD_MU_TOP,
    KEY_DD_M_ULS_OH,
    KEY_DD_MU_OH,
    KEY_DD_PUNCH_VED,
    KEY_DD_VRD_C_MPA,
    KEY_DD_SHEAR_VED,
    KEY_DD_SHEAR_VRDC
)

logger = logging.getLogger("osdagbridge.core.reports.charts")


def _max_member_efficiency(pair_designs: Any) -> Optional[float]:
    """Maximum Osdag efficiency (utilization ratio) over a cross-bracing or
    end-diaphragm result dump (nested pair -> member -> force_type -> raw)."""
    if not isinstance(pair_designs, dict):
        return None
    try:
        from osdagbridge.core.bridge_types.plate_girder.results_data import _extract_osdag_summary
    except ImportError:
        return None

    best = None
    for members in pair_designs.values():
        if not isinstance(members, dict):
            continue
        for force_types in members.values():
            if not isinstance(force_types, dict):
                continue
            for raw in force_types.values():
                try:
                    val = _extract_osdag_summary(raw or {}).get("efficiency")
                    if val is None:
                        continue
                    f = float(val)
                    if best is None or f > best:
                        best = f
                except (TypeError, ValueError, AttributeError):
                    continue
    return best


def extract_governing_urs(bridge: Any) -> Dict[str, Optional[float]]:
    """
    Extract governing (maximum) Utilization Ratio for the 4 primary components:
      - Steel Plate Girders
      - Concrete Deck Slab
      - Cross Bracing
      - End Diaphragms
    Uses the exact same data sources as the report tables.
    """
    output_dict = getattr(bridge, "output_dict", {}) or {}
    input_dict = getattr(bridge, "input_dict", {}) or {}

    # 1. Steel Plate Girders
    girder_urs = []
    design_results = output_dict.get("design_results", {}) or {}
    pg = design_results.get("per_girder", {}) or {}
    for g, gd in pg.items():
        if str(g).startswith("EB"):
            continue
        for chk in gd.get("checks") or []:
            try:
                v = chk.get("dcr")
                if v is not None:
                    girder_urs.append(float(v))
            except (TypeError, ValueError):
                pass
        for lc, ld in (gd.get("per_lc") or {}).items():
            if str(lc).lower().startswith("envelope"):
                continue
            for chk in ld.get("checks") or []:
                try:
                    v = chk.get("dcr")
                    if v is not None:
                        girder_urs.append(float(v))
                except (TypeError, ValueError):
                    pass
    girder_ur = max(girder_urs) if girder_urs else None

    # 2. Concrete Deck Slab
    deck_results = output_dict.get("deck_design_results", {}) or {}
    deck_urs = []
    for k, v in deck_results.items():
        if str(k).startswith("ur_"):
            try:
                if v is not None:
                    deck_urs.append(float(v))
            except (TypeError, ValueError):
                pass
    for dem_k, cap_k in [
        (KEY_DD_M_ULS_SAG, KEY_DD_MU_BOT),
        (KEY_DD_M_ULS_HOG, KEY_DD_MU_TOP),
        (KEY_DD_M_ULS_OH,  KEY_DD_MU_OH),
        (KEY_DD_PUNCH_VED, KEY_DD_VRD_C_MPA),
        (KEY_DD_SHEAR_VED, KEY_DD_SHEAR_VRDC)
    ]:
        d_val = input_dict.get(dem_k) or output_dict.get(dem_k)
        c_val = input_dict.get(cap_k) or output_dict.get(cap_k)
        try:
            if d_val is not None and c_val is not None and float(c_val) > 0:
                deck_urs.append(float(d_val) / float(c_val))
        except (TypeError, ValueError):
            pass
    deck_ur = max(deck_urs) if deck_urs else None

    # 3. Cross Bracing
    cb_urs = []
    cb_results = output_dict.get("crossbracing_design_results", {}) or {}
    if cb_results:
        m = _max_member_efficiency(cb_results)
        if m is not None:
            cb_urs.append(m)
    if hasattr(bridge, "get_cb_pairs") and hasattr(bridge, "get_cb_efficiency"):
        try:
            for pair in bridge.get_cb_pairs():
                for member in ("diagonal", "chord"):
                    for ft in ("compression", "tension"):
                        eff = bridge.get_cb_efficiency(pair, member, ft)
                        if eff not in (None, "", "---"):
                            cb_urs.append(float(eff))
        except Exception:
            pass
    cb_ur = max(cb_urs) if cb_urs else None

    # 4. End Diaphragms
    ed_urs = []
    ed_results = output_dict.get("end_diaphragm_design_results", {}) or {}
    if ed_results:
        m = _max_member_efficiency(ed_results)
        if m is not None:
            ed_urs.append(m)
    ed_type = ""
    for _k, _v in input_dict.items():
        if str(_k).startswith(KEY_MP_ED_TYPE) and _v:
            ed_type = str(_v)
            break
    if "brac" in ed_type.strip().lower() and cb_ur is not None:
        ed_urs.append(cb_ur)
    ed_ur = max(ed_urs) if ed_urs else None

    return {
        "Steel Plate Girders": girder_ur,
        "Concrete Deck Slab": deck_ur,
        "Cross Bracing": cb_ur,
        "End Diaphragms": ed_ur,
    }


def generate_ur_summary_chart(bridge: Any, output_path: str) -> bool:
    """
    Generate bar chart of Utilization Ratio for Section 5.5.
    Features:
      - Categories: Steel Plate Girders, Concrete Deck Slab, Cross Bracing, End Diaphragms
      - Y-axis labeled 'Utilization Ratio'
      - Red dashed horizontal line at UR = 1.0
      - Bars above 1.0 visibly colored red (COLOR_FAIL), passing bars green (COLOR_OSDAG_GREEN)
    """
    try:
        setup_matplotlib_style()
        ur_data = extract_governing_urs(bridge)

        categories = [
            "Steel Plate\nGirders",
            "Concrete\nDeck Slab",
            "Cross\nBracing",
            "End\nDiaphragms"
        ]
        keys = [
            "Steel Plate Girders",
            "Concrete Deck Slab",
            "Cross Bracing",
            "End Diaphragms"
        ]

        vals = []
        bar_colors = []
        labels = []

        has_any_data = any(ur_data[k] is not None for k in keys)

        for k in keys:
            v = ur_data[k]
            if v is not None:
                vals.append(v)
                if v > 1.0:
                    bar_colors.append(COLOR_FAIL)
                    labels.append(f"{v:.2f}\n(FAIL)")
                else:
                    bar_colors.append(COLOR_OSDAG_GREEN)
                    labels.append(f"{v:.2f}\n(PASS)")
            else:
                # If no analysis run yet, show 0.0 with clear N/A label
                vals.append(0.0)
                bar_colors.append(COLOR_TEXT_MUTED)
                labels.append("N/A")

        fig, ax = plt.subplots(figsize=(6.8, 3.8), dpi=CHART_CONFIG['dpi'])

        x_indices = np.arange(len(categories))
        bar_width = 0.52

        bars = ax.bar(
            x_indices,
            vals,
            width=bar_width,
            color=bar_colors,
            edgecolor=CHART_CONFIG['spine_color'],
            linewidth=1.0,
            zorder=3
        )

        # Red dashed threshold line at UR = 1.0
        ax.axhline(
            y=1.0,
            color=COLOR_FAIL,
            linestyle="--",
            linewidth=CHART_CONFIG['threshold_line_width'],
            label="Design Limit (UR = 1.0)",
            zorder=4
        )

        # Y-axis scaling
        max_val = max(vals) if vals else 0.0
        y_max = max(1.25, max_val * 1.25 if max_val > 0 else 1.25)
        ax.set_ylim(0, y_max)
        ax.set_ylabel("Utilization Ratio (Demand / Capacity)", fontsize=9.5, fontweight="bold", color=COLOR_TEXT_MAIN)
        ax.set_title("Overall Design Check Summary — Component Utilization Ratios", fontsize=11, fontweight="bold", pad=12, color=COLOR_TEXT_MAIN)

        ax.set_xticks(x_indices)
        ax.set_xticklabels(categories, fontsize=9.0, fontweight="bold", color=COLOR_TEXT_MAIN)

        # Value annotations above bars
        for idx, (bar, text_lbl, val) in enumerate(zip(bars, labels, vals)):
            y_pos = bar.get_height() + (y_max * 0.03)
            txt_color = COLOR_FAIL if (val > 1.0) else (COLOR_PRIMARY if val > 0 else COLOR_TEXT_MUTED)
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                y_pos,
                text_lbl,
                ha='center',
                va='bottom',
                fontsize=8.5,
                fontweight='bold',
                color=txt_color
            )

        ax.legend(loc="upper right", framealpha=0.9, fontsize=8.5)
        plt.tight_layout()

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.savefig(output_path, dpi=CHART_CONFIG['dpi'])
        plt.close(fig)
        logger.info(f"Generated UR summary chart at: {output_path}")
        return True
    except Exception as exc:
        logger.error(f"Failed to generate UR summary chart: {exc}", exc_info=True)
        return False


def _get_float_qty(val: Any, default: float = 0.0) -> float:
    try:
        s = str(val).strip().replace(',', '')
        if s.upper() in ("N.A.", "NA", "NONE", "---", ""):
            return default
        return float(s)
    except (TypeError, ValueError):
        return default


def generate_steel_tonnage_chart(input_dict: dict, output_path: str) -> bool:
    """
    Generate structural steel tonnage breakdown chart for Chapter 7.
    Categories: Girders, Cross Bracing, End Diaphragms.
    """
    try:
        setup_matplotlib_style()

        # 1. Girders weight (MT)
        girders_wt = _get_float_qty(input_dict.get("steel_girders_wt_total"))

        # 2. Cross bracing weight (MT)
        cb_top = _get_float_qty(input_dict.get("bracing_top_wt_total"))
        cb_bot = _get_float_qty(input_dict.get("bracing_bot_wt_total"))
        cb_diag = _get_float_qty(input_dict.get("bracing_diag_wt_total"))
        cb_total = cb_top + cb_bot + cb_diag

        # 3. End diaphragms weight (MT)
        # Calculate from end diaphragm mass and geometry if not directly in BOM
        ed_mass = _get_float_qty(input_dict.get("member_properties.end_diaphragm_details.section_properties.mass.G1G2.E1M1"), 15.04)
        spacing = _get_float_qty(input_dict.get(KEY_TS_GIRDER_SPACING), 2.1)
        n_girders = int(_get_float_qty(input_dict.get(KEY_TS_NO_OF_GIRDERS), 4))
        bays = max(1, n_girders - 1)
        # 2 support lines * bays * spacing * mass_per_m in kg -> MT
        ed_total = (2 * bays * spacing * ed_mass) / 1000.0

        # Fallback if cross bracing was N.A. in BOM: compute from section mass
        if cb_total <= 0.0:
            span = _get_float_qty(input_dict.get(KEY_SPAN), 24.0)
            n_panels = max(1, round(span / 5.0))
            cb_mass = 15.04  # IS 100x100x10 ~ 15.04 kg/m
            diag_len = (spacing**2 + 1.6**2)**0.5
            total_cb_len = bays * n_panels * (2 * spacing + 2 * diag_len)
            cb_total = (total_cb_len * cb_mass) / 1000.0

        categories = ["Girders", "Cross Bracing", "End Diaphragms"]
        weights = [girders_wt, cb_total, ed_total]
        total_steel = sum(weights)

        fig, ax = plt.subplots(figsize=(6.0, 3.5), dpi=CHART_CONFIG['dpi'])

        colors = [COLOR_PRIMARY, COLOR_OSDAG_GREEN, COLOR_ACCENT]
        bar_width = 0.48
        x_indices = np.arange(len(categories))

        bars = ax.bar(
            x_indices,
            weights,
            width=bar_width,
            color=colors,
            edgecolor=CHART_CONFIG['spine_color'],
            linewidth=1.0,
            zorder=3
        )

        ax.set_ylabel("Weight (Metric Tonnes, MT)", fontsize=9.5, fontweight="bold", color=COLOR_TEXT_MAIN)
        ax.set_title(f"Structural Steel Tonnage Breakdown (Total: {total_steel:.2f} MT)", fontsize=11, fontweight="bold", pad=12, color=COLOR_TEXT_MAIN)
        ax.set_xticks(x_indices)
        ax.set_xticklabels(categories, fontsize=9.0, fontweight="bold", color=COLOR_TEXT_MAIN)

        max_wt = max(weights) if weights else 0.0
        ax.set_ylim(0, max_wt * 1.25 if max_wt > 0 else 10.0)

        for bar, wt in zip(bars, weights):
            pct = (wt / total_steel * 100.0) if total_steel > 0 else 0.0
            lbl = f"{wt:.2f} MT\n({pct:.1f}%)"
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + (max_wt * 0.03),
                lbl,
                ha='center',
                va='bottom',
                fontsize=8.5,
                fontweight='bold',
                color=COLOR_TEXT_MAIN
            )

        plt.tight_layout()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.savefig(output_path, dpi=CHART_CONFIG['dpi'])
        plt.close(fig)
        logger.info(f"Generated steel tonnage chart at: {output_path}")
        return True
    except Exception as exc:
        logger.error(f"Failed to generate steel tonnage chart: {exc}", exc_info=True)
        return False


def generate_concrete_rebar_chart(input_dict: dict, output_path: str) -> bool:
    """
    Generate chart comparing Concrete Volume (m³) and Reinforcement Steel Weight (MT).
    Uses dual-scale visualization for clear dimensional comparison.
    """
    try:
        setup_matplotlib_style()

        concrete_vol = _get_float_qty(input_dict.get("concrete_deck_vol_total"), 50.40)
        rebar_wt = _get_float_qty(input_dict.get("rebar_deck_wt_total"), 6.05)

        fig, ax1 = plt.subplots(figsize=(6.0, 3.5), dpi=CHART_CONFIG['dpi'])
        ax2 = ax1.twinx()

        x = np.array([0, 1])
        width = 0.42

        # Concrete Bar on Axis 1 (Left)
        b1 = ax1.bar(
            x[0],
            concrete_vol,
            width=width,
            color=COLOR_PRIMARY,
            edgecolor=CHART_CONFIG['spine_color'],
            linewidth=1.0,
            label="Concrete Volume (m³)",
            zorder=3
        )
        ax1.set_ylabel("Concrete Volume (m³)", color=COLOR_PRIMARY, fontsize=9.5, fontweight="bold")
        ax1.tick_params(axis='y', labelcolor=COLOR_PRIMARY)
        ax1.set_ylim(0, concrete_vol * 1.30 if concrete_vol > 0 else 60.0)

        # Rebar Bar on Axis 2 (Right)
        b2 = ax2.bar(
            x[1],
            rebar_wt,
            width=width,
            color=COLOR_OSDAG_GREEN,
            edgecolor=CHART_CONFIG['spine_color'],
            linewidth=1.0,
            label="Rebar Weight (MT)",
            zorder=3
        )
        ax2.set_ylabel("Reinforcement Steel Weight (MT)", color=COLOR_OSDAG_GREEN, fontsize=9.5, fontweight="bold")
        ax2.tick_params(axis='y', labelcolor=COLOR_OSDAG_GREEN)
        ax2.set_ylim(0, rebar_wt * 1.30 if rebar_wt > 0 else 10.0)
        ax2.grid(False)  # Avoid overlapping grid lines

        ax1.set_xticks(x)
        ax1.set_xticklabels([f"Concrete Deck\n({concrete_vol:.2f} m³)", f"Reinforcement Steel\n({rebar_wt:.2f} MT)"], fontsize=9.0, fontweight="bold", color=COLOR_TEXT_MAIN)
        ax1.set_title("Deck Slab: Concrete Volume vs. Reinforcement Steel Weight", fontsize=11, fontweight="bold", pad=12, color=COLOR_TEXT_MAIN)

        # Value labels
        ax1.text(
            x[0],
            concrete_vol + (concrete_vol * 0.04),
            f"{concrete_vol:.2f} m³",
            ha='center',
            va='bottom',
            fontsize=9.0,
            fontweight='bold',
            color=COLOR_PRIMARY
        )
        ax2.text(
            x[1],
            rebar_wt + (rebar_wt * 0.04),
            f"{rebar_wt:.2f} MT",
            ha='center',
            va='bottom',
            fontsize=9.0,
            fontweight='bold',
            color=COLOR_OSDAG_GREEN
        )

        plt.tight_layout()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.savefig(output_path, dpi=CHART_CONFIG['dpi'])
        plt.close(fig)
        logger.info(f"Generated concrete vs rebar chart at: {output_path}")
        return True
    except Exception as exc:
        logger.error(f"Failed to generate concrete vs rebar chart: {exc}", exc_info=True)
        return False
