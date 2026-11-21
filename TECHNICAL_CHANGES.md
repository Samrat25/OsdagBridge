# Technical Changes: Report Generator Refactoring & Enhancement

**Project:** OsdagBridge (FOSSEE / IIT Bombay)  
**Branch:** `feature/report-refactor`  
**Baseline Artifact:** `Report_Before.pdf` (45 pages)  
**Enhanced Artifact:** `Report_After.pdf` (51 pages)  

---

## 1. Executive Summary

This document details the refactoring and feature enhancement of the OsdagBridge design report generation subsystem. The original report generator converted bridge design outputs into a PDF document using PyLaTeX, but suffered from decentralized formatting, multi-page tables lacking repeated headers, table rows colliding with page footers (notably girder check row G4), combined/unstructured live load tables, and an absence of visual analytical charts.

All requirements have been implemented with small, well-scoped commits, strict backward compatibility, and end-to-end PDF validation.

---

## 2. Centralized Style Module Architecture (`styles.py`)

A single centralized module, `src/osdagbridge/core/reports/styles.py`, was created to govern all layout, typography, palette, and visual formatting rules across all report chapters.

### Key Components of `styles.py`:

1. **Color Palette & Design Tokens:**
   - `COLOR_OSDAG_GREEN` (`#91B014`): Primary brand color for rules, highlights, and passing indicators.
   - `COLOR_DARK_SLATE` / `COLOR_PRIMARY` (`#2C3E50`): Deep slate navy for headers and primary series.
   - `COLOR_PASS` (`#1E8449`): WCAG AA accessible forest green for passing checks ($UR \le 1.0$).
   - `COLOR_FAIL` (`#C0392B`): Crimson red for failing checks ($UR > 1.0$) and threshold alert lines.
   - `COLOR_WARNING` (`#D35400`) & `COLOR_INFO_BLUE` / `COLOR_ACCENT` (`#2980B9`).
   - `LATEX_COLOR_DEFS`: Preamble macro defining LaTeX RGB/HTML color names (`\definecolor{osdagGreen}...`).

2. **Page Geometry & Margins (`GEOMETRY_CONFIG`):**
   - Paper: A4 (`210mm` $\times$ `297mm`).
   - Margins: `top=22mm`, `bottom=28mm`, `left=22mm`, `right=20mm`.
   - Header/Footer Distances: `headheight=18pt`, `headsep=14pt`, `footskip=18pt`.
   - *Rationale:* The expanded `bottom=28mm` margin paired with `footskip=18pt` creates an ample physical separation between the lowest table row and the running footer rule, permanently eliminating footer bleed.

3. **Standard Table Setup & Helper (`build_longtable_header`):**
   - Standard parameters: `\tabcolsep=5pt`, `\arraystretch=1.18`, `\extrarowheight=0.8pt`, `\arrayrulewidth=0.5pt`.
   - Standardized `longtable` generator implementing:
     - `\begin{longtable}{col_spec}` preceded by `\needspace{...}` to prevent orphan headers.
     - `\caption{\textbf{...}} \label{...} \\ \hline <header_row> \hline \endfirsthead` for initial display.
     - Repeating header with `\small\textit{<Caption> (Continued)}` under `\endhead`.
     - Intermediate footer `\multicolumn{n}{r}{\footnotesize\textit{Continued on next page\dots}} \\ \endfoot`.
     - Clean `\endlastfoot` without trailing extra lines to prevent phantom page breaks.

4. **Running Headers and Footers (`get_fancyhdr_latex`):**
   - Defines `main`, `plain`, and `firstpage` styles.
   - Header: Left: Project Name and Job Number; Right: Date and Revision; Underlined with a 1pt `osdagGreen` rule.
   - Footer: Left: "Osdag | FOSSEE | Indian Institute of Technology Bombay"; Right: "Page \thepage\ of \pageref{LastPage}".

5. **Headless Matplotlib Style Configuration (`setup_matplotlib_style`):**
   - Configures `matplotlib.use('Agg')` for headless execution in terminal or container environments.
   - Standardizes font families (`DejaVu Sans`, `Arial`, `Helvetica`), bold titles, 300 DPI resolution, custom gridlines (`#E0E0E0`, dashed), and consistent spine styling.
   - Automatically initializes `MPLCONFIGDIR` in a writable temporary directory to avoid permissions issues on Windows.

6. **Formatting Helpers:**
   - `format_status_badge(status)`: Formats "PASS" in green and "FAIL" in bold red text.
   - `format_ur(val, threshold=1.0)`: Formats Utilization Ratios with red alert coloring if exceeding 1.0.

---

## 3. Multi-Page Tables & Footer Bleed Resolution

### Problem Diagnosis:
In `Report_Before.pdf`, extensive girder check tables (such as Table 5.4 for Section Classification and Table 5.10 for Web Yielding/Buckling) spanned multiple pages without column headers on continuation pages. Furthermore, around page 26–30, girder check rows (notably G4) bled directly into the green footer rule, and multi-row girder records were split awkwardly across page boundaries.

### Technical Remedies:
1. **Repeating Headers on All Multi-Page Tables:**
   - Refactored all 29 design check tables in `chap5.py`, 7 parameter tables in `chap2.py`, Table 3.7 & 3.8 in `chap3.py`, and Table 7.1 in `chap7.py` to use `build_longtable_header`.
   - Continuation pages now consistently display `(Continued)` and full column headers.
2. **Preventing Mid-Girder Page Tears:**
   - In `chap5.py`, girder check builders construct multi-line records (e.g. G1 through G4 with sub-properties). Changed intra-record line breaks from `\\[6pt]` to `\\*[6pt]`. In LaTeX `longtable`, the `*` modifier suppresses page breaks between consecutive lines of the same record, forcing LaTeX to keep all lines of girder G4 together or push the entire block cleanly to the next page.
3. **Bottom Margin & Footskip Adjustments:**
   - Raised bottom margin to `28mm` and adjusted `footskip=18pt` and `headheight=18pt`.
   - Injected `\needspace{10\baselineskip}` before longtable starts, ensuring tables never begin with just a header at the bottom of a page.
4. **Verification:**
   - Confirmed in `Report_After.pdf` that all girder rows for G1, G2, G3, and G4 render with clean whitespace above the footer across all pages, with 20 repeating continuation headers verified via PDF parser.

---

## 4. Chapter 3 Loads Refactoring

### Previous State:
Table 3.3 ("Live Loads (LL)") was a 2-column key-value table that lumped all vehicle classes into a single comma-separated string, showed impact factor as a messy text list, and appended footpath live load into the same table without independent units or structural parameters.

### Technical Implementation:
Split the data into two distinct, professionally structured LaTeX tables:

1. **Table 3.3: Live Loads (LL) — Vehicle Class Specifications:**
   - *Columns:* `[Vehicle Class | Impact Factor (1 + i_m) | Braking Load [kN] | Centrifugal Force [kN] | Governing Clause]`.
   - *Dynamic Data Binding:* Reads user selections dynamically from `input_dict` (`KEY_LL_IRC_CLASS_A`, `KEY_LL_IRC_70R_WHEELED`, `KEY_LL_IRC_70R_TRACKED`, `KEY_LL_IRC_70R_BOGIE`, `KEY_LL_IRC_AA_WHEELED`, `KEY_LL_IRC_AA_TRACKED`, `KEY_LL_IRC_CLASS_SV`, `KEY_LL_IRC_CLASS_FATIGUE`, and custom vehicles). Only vehicles selected by the user in the Loading tab are displayed.
   - *Formulas Applied:*
     - Class A impact: $(1 + i_m) = 1.0 + \frac{9.0}{13.5 + L}$ (IRC 6 Cl. 208.2).
     - Heavy vehicles (70R / Class AA): Tracked vs. wheeled span-dependent formulas (IRC 6 Cl. 208.3).
     - Braking load: Evaluated from IRC 6 Cl. 211.2 per vehicle train and number of traffic lanes ($20\%$ of first 2 lanes $+ 5\%$ of subsequent lanes for Class A; vehicle-specific braking for 70R/AA).
     - Centrifugal force: Set to $0.00\text{ kN}$ as the bridge is designed on a tangent horizontal alignment ($R = \infty$) in accordance with IRC 6 Cl. 212.
2. **Table 3.4: Footway and Pedestrian Live Load:**
   - *Columns:* `[Parameter | Design Value | Unit | Governing Standard / Clause]`.
   - *Parameters Detailed:*
     - Footpath Configuration (None / Single Side / Both Sides per IRC 5 Cl. 109).
     - Footpath Clear Width ($m$).
     - Footpath Slab Thickness ($mm$).
     - Footway Pressure Mode (As per IRC 6 / User-Specified).
     - Design Pedestrian Live Load ($4.905\text{ kN/m}^2$, corresponding to $500\text{ kg/m}^2$ per IRC 6 Cl. 206.1).

---

## 5. Visual Chart Generation (`charts.py`)

A dedicated chart generation module, `src/osdagbridge/core/reports/charts.py`, was implemented using Matplotlib with the headless `Agg` backend:

### 1. Section 5.5: Utilization Ratio Summary Chart
- **Objective:** Provide an immediate visual summary of governing structural demand/capacity ratios across all key components.
- **Components Tracked:** Steel Plate Girders, Concrete Deck Slab, Cross Bracing, End Diaphragms.
- **Features:**
  - Y-axis labeled: `Utilization Ratio (Demand / Capacity)`.
  - Red dashed horizontal reference line at $UR = 1.0$ (`COLOR_FAIL`).
  - Bar colors: Passing checks ($UR \le 1.0$) rendered in `COLOR_OSDAG_GREEN` (`#91B014`); failing checks ($UR > 1.0$) rendered in `COLOR_FAIL` (`#C0392B`).
  - Value labels and status tags (`0.85 (PASS)` or `1.15 (FAIL)`) callouts placed atop each bar.
- **Integration:** Embedded as Figure 5.1 at the top of Section 5.5, immediately preceding the detailed numerical Table 5.22.

### 2. Chapter 7: Material Take-off & Quantity Summary Charts
- **Chart 1: Structural Steel Tonnage Breakdown:**
  - Bar chart showing tonnage (Metric Tonnes, MT) for Girders, Cross Bracing, and End Diaphragms.
  - Sourced dynamically from BOM quantities (`steel_girders_wt_total`, `bracing_top_wt_total`, `bracing_bot_wt_total`, `bracing_diag_wt_total`, and end diaphragm mass/geometry).
  - Displays tonnage values and percentage contributions per element.
- **Chart 2: Concrete Volume vs. Reinforcement Steel Weight:**
  - Dual-scale comparative chart with twin Y-axes:
    - Primary axis (Left): Concrete Volume ($m^3$) in Slate Dark (`#2C3E50`).
    - Secondary axis (Right): Reinforcement Steel Weight (MT) in Osdag Green (`#91B014`).
  - Allows direct visual comparison of materials with disparate physical units without cluttering scales.
- **Integration:** Embedded side-by-side using LaTeX `minipage` environments directly beneath Table 7.1 in Chapter 7.

---

## 6. Summary of Altered Files

| File | Type | Changes Description |
|---|---|---|
| `src/osdagbridge/core/reports/styles.py` | New File | Centralized theme module: geometry, color tokens, table parameters, fancyhdr pagestyles, `build_longtable_header`, Matplotlib setup. |
| `src/osdagbridge/core/reports/charts.py` | New File | Headless Matplotlib charts: UR summary bar chart, steel tonnage breakdown, concrete volume vs. rebar weight comparison. |
| `src/osdagbridge/core/reports/report_generator.py` | Modified | Integrated centralized styles, preamble geometry, dynamic chart generation in temp directories, and chapter payload routing. |
| `src/osdagbridge/core/reports/executive_summary.py` | Modified | Replaced hardcoded formatting with `styles.py` tokens; standardized badge and UR formatting. |
| `src/osdagbridge/core/reports/chap2.py` | Modified | Converted Tables 2.6–2.12 to repeating `build_longtable_header`; fixed column spec mismatches. |
| `src/osdagbridge/core/reports/chap3.py` | Modified | Split Table 3.3 into dedicated Live Loads and Footway Load tables with dynamic vehicle filtering and proper units; converted Table 3.7. |
| `src/osdagbridge/core/reports/chap5.py` | Modified | Converted all 29 design tables to `build_longtable_header`; added `\\*[6pt]` non-breaking line grouping; embedded Section 5.5 UR chart. |
| `src/osdagbridge/core/reports/chap7.py` | Modified | Converted BOM Table 7.1 to `build_longtable_header`; embedded steel tonnage and concrete-rebar charts. |
| `src/osdagbridge/core/reports/chap8.py` | Modified | Replaced formatting with style module imports. |
| `generate_test_report.py` | Updated | Headless report generation script supporting custom output stems and mocking OpenSees dependencies. |
| `README.md` | Updated | Added complete "Report Generation & Architecture" guide covering headless and desktop workflows. |

---

## 7. Verification & Quality Assurance

1. **Baseline Preservation:** `Report_Before.pdf` remains untouched in repository root as the canonical reference.
2. **Repeating Headers Verification:** Confirmed that multi-page tables repeat headers across 20+ continuation pages with `(Continued)` headers.
3. **Footer Overlap Verification:** Verified across all 51 pages of `Report_After.pdf` that table rows maintain a clean buffer from the running footer, completely resolving the G4 footer collision.
4. **Dynamic Loading Inputs Verification:** Tested vehicle selection filtering with various subsets of IRC Class A, 70R, AA, and SV; verified tables update dynamically without hardcoding.
5. **Headless Compilation:** Verified compilation using portable TinyTeX under PowerShell on Windows without GUI dependencies.
