# =============================================================================
# OsdagBridge — Centralized Report Styling & Layout Theme Module
# =============================================================================
"""
Single centralized style module for OsdagBridge PDF design reports.
Defines layout geometry, color palettes, typography, table styling,
header/footer definitions, chart styling, and standard LaTeX/PyLaTeX
formatting helpers.
"""

from typing import Dict, Any, List, Optional, Tuple
import os

# ─────────────────────────────────────────────────────────────────────────────
# 1. COLOR PALETTE
# ─────────────────────────────────────────────────────────────────────────────

# Canonical Hex Colors
COLOR_OSDAG_GREEN   = "#91B014"   # Primary brand color (Osdag Green)
COLOR_DARK_SLATE    = "#2C3E50"   # Secondary structural dark
COLOR_LIGHT_BG      = "#F8F9FA"   # Very light gray for backgrounds
COLOR_TABLE_HEADER  = "#EAECEE"   # Neutral light gray for table headers
COLOR_TABLE_ALT     = "#F4F6F7"   # Alternating row shading
COLOR_TEXT_MAIN     = "#222222"   # Main body text
COLOR_TEXT_MUTED    = "#555555"   # Notes, references, secondary labels
COLOR_PASS          = "#1E8449"   # Clean pass green (WCAG AA accessible)
COLOR_FAIL          = "#C0392B"   # Clear fail red
COLOR_WARNING       = "#D35400"   # Warning orange
COLOR_INFO_BLUE     = "#2980B9"   # Info blue

# Matplotlib chart color sequence
CHART_PALETTE = [
    COLOR_OSDAG_GREEN,
    "#2980B9",   # Steel blue
    "#8E44AD",   # Royal purple
    "#16A085",   # Turquoise
    "#D35400",   # Rust orange
    "#2C3E50",   # Slate gray
    "#F39C12",   # Warm gold
    "#27AE60",   # Emerald green
]

# LaTeX color definitions string for the document preamble
LATEX_COLOR_DEFS = r"""
\definecolor{osdagGreen}{HTML}{91B014}
\definecolor{osdagDark}{HTML}{2C3E50}
\definecolor{osdagPass}{HTML}{1E8449}
\definecolor{osdagFail}{HTML}{C0392B}
\definecolor{osdagWarn}{HTML}{D35400}
\definecolor{tableHeaderBg}{HTML}{EAECEE}
\definecolor{tableAltBg}{HTML}{F4F6F7}
"""

# ─────────────────────────────────────────────────────────────────────────────
# 2. PAGE GEOMETRY & MARGINS
# ─────────────────────────────────────────────────────────────────────────────

# A4 dimensions with sufficient bottom buffer to prevent footer bleed
GEOMETRY_CONFIG = {
    "paper": "a4paper",
    "top": "22mm",
    "bottom": "28mm",      # Extra clearance for footskip and software default notes
    "left": "20mm",
    "right": "20mm",
    "headheight": "18pt",
    "headsep": "14pt",
    "footskip": "18pt",
}

def get_geometry_latex() -> str:
    """Return LaTeX \\usepackage[...]{geometry} options string."""
    return (
        r"\usepackage[a4paper, "
        f"top={GEOMETRY_CONFIG['top']}, "
        f"bottom={GEOMETRY_CONFIG['bottom']}, "
        f"left={GEOMETRY_CONFIG['left']}, "
        f"right={GEOMETRY_CONFIG['right']}, "
        f"headheight={GEOMETRY_CONFIG['headheight']}, "
        f"headsep={GEOMETRY_CONFIG['headsep']}, "
        f"footskip={GEOMETRY_CONFIG['footskip']}"
        r"]{geometry}"
    )

def apply_geometry(doc) -> None:
    """Apply geometry parameters to a PyLaTeX Document instance if used."""
    try:
        from pylatex import Package
        doc.packages.append(Package("geometry", options=[
            "a4paper",
            f"top={GEOMETRY_CONFIG['top']}",
            f"bottom={GEOMETRY_CONFIG['bottom']}",
            f"left={GEOMETRY_CONFIG['left']}",
            f"right={GEOMETRY_CONFIG['right']}",
            f"headheight={GEOMETRY_CONFIG['headheight']}",
            f"headsep={GEOMETRY_CONFIG['headsep']}",
            f"footskip={GEOMETRY_CONFIG['footskip']}",
        ]))
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# 3. TABLE STYLES & ROW SPACING
# ─────────────────────────────────────────────────────────────────────────────

TABLE_CONFIG = {
    "tabcolsep": "5pt",           # Horizontal padding between columns
    "arraystretch": "1.18",       # Vertical row expansion factor
    "extrarowheight": "0.8pt",    # Extra space above horizontal rules
    "arrayrulewidth": "0.5pt",    # Outline border width
    "lt_pre": "0pt",              # Space before longtable
    "lt_post": "6pt",             # Space after longtable
    "needspace_lines": "5",       # Minimum lines remaining before page break
}

def get_table_setup_latex() -> str:
    """Return standard LaTeX table parameters string."""
    return (
        f"\\setlength{{\\tabcolsep}}{{{TABLE_CONFIG['tabcolsep']}}}\n"
        f"\\renewcommand{{\\arraystretch}}{{{TABLE_CONFIG['arraystretch']}}}\n"
        f"\\setlength{{\\extrarowheight}}{{{TABLE_CONFIG['extrarowheight']}}}\n"
        f"\\setlength{{\\arrayrulewidth}}{{{TABLE_CONFIG['arrayrulewidth']}}}\n"
        f"\\setlength{{\\LTpre}}{{{TABLE_CONFIG['lt_pre']}}}\n"
        f"\\setlength{{\\LTpost}}{{{TABLE_CONFIG['lt_post']}}}\n"
        f"\\setlength{{\\LTleft}}{{\\fill}}\n"
        f"\\setlength{{\\LTright}}{{\\fill}}\n"
        f"\\BeforeBeginEnvironment{{table}}{{\\needspace{{{TABLE_CONFIG['needspace_lines']}\\baselineskip}}}}\n"
        f"\\BeforeBeginEnvironment{{longtable}}{{\\needspace{{{TABLE_CONFIG['needspace_lines']}\\baselineskip}}}}\n"
    )

# ─────────────────────────────────────────────────────────────────────────────
# 4. HEADER & FOOTER SETTINGS
# ─────────────────────────────────────────────────────────────────────────────

def get_fancyhdr_latex(project_name: str, job_number: str, report_date: str, report_version: str = "Rev 0") -> str:
    """Return LaTeX fancyhdr pagestyles (main, plain, firstpage)."""
    return r"""
\fancypagestyle{main}{
  \fancyhf{}
  \fancyhead[L]{""" + project_name + r""" $|$ """ + job_number + r"""}
  \fancyhead[R]{""" + report_date + r""" $|$ """ + report_version + r"""}
  \fancyfoot[L]{Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}
  \fancyfoot[R]{Page \thepage\ of \pageref{LastPage}}
  \renewcommand{\headrule}{\color{osdagGreen}\hrule width\headwidth height 1pt \vspace{2pt}}
  \renewcommand{\footrule}{%
    \ifbool{hasSDonPage}{%
      \vspace{-18pt}%
      \hbox to \headwidth{\textcolor{black}{\footnotesize\textit{* Software default value}}\hfil}%
      \vspace{4pt}%
    }{%
      \vspace{-6pt}%
    }%
    \color{osdagGreen}\hrule width\headwidth height 1pt \vspace{6pt}%
  }
}
\fancypagestyle{plain}{
  \fancyhf{}
  \fancyhead[L]{""" + project_name + r""" $|$ """ + job_number + r"""}
  \fancyhead[R]{""" + report_date + r""" $|$ """ + report_version + r"""}
  \fancyfoot[L]{Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}
  \fancyfoot[R]{Page \thepage\ of \pageref{LastPage}}
  \renewcommand{\headrule}{\color{osdagGreen}\hrule width\headwidth height 1pt \vspace{2pt}}
  \renewcommand{\footrule}{%
    \ifbool{hasSDonPage}{%
      \vspace{-18pt}%
      \hbox to \headwidth{\textcolor{black}{\footnotesize\textit{* Software default value}}\hfil}%
      \vspace{4pt}%
    }{%
      \vspace{-6pt}%
    }%
    \color{osdagGreen}\hrule width\headwidth height 1pt \vspace{6pt}%
  }
}
\fancypagestyle{firstpage}{
  \fancyhf{}
  \renewcommand{\headrulewidth}{0pt}
  \fancyfoot[L]{Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}
  \fancyfoot[R]{Page \thepage\ of \pageref{LastPage}}
  \renewcommand{\footrule}{\vspace{-6pt}\color{osdagGreen}\hrule width\headwidth height 1pt \vspace{6pt}}
}
\pagestyle{main}
"""

# ─────────────────────────────────────────────────────────────────────────────
# 5. CHART STYLING RULES & MATPLOTLIB CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

CHART_CONFIG = {
    "dpi": 300,
    "font_family": "sans-serif",
    "title_size": 11,
    "label_size": 9.5,
    "tick_size": 8.5,
    "legend_size": 8.5,
    "grid_color": "#E0E0E0",
    "grid_alpha": 0.7,
    "grid_style": "--",
    "spine_color": "#BDC3C7",
    "threshold_line_color": COLOR_FAIL,
    "threshold_line_style": "--",
    "threshold_line_width": 1.4,
}

def setup_matplotlib_style():
    """Apply consistent styling rules to matplotlib for all report figures."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica', 'Liberation Sans'],
        'font.size': CHART_CONFIG['label_size'],
        'axes.titlesize': CHART_CONFIG['title_size'],
        'axes.titleweight': 'bold',
        'axes.labelsize': CHART_CONFIG['label_size'],
        'axes.labelweight': 'bold',
        'axes.edgecolor': CHART_CONFIG['spine_color'],
        'axes.linewidth': 0.8,
        'axes.grid': True,
        'axes.axisbelow': True,
        'grid.color': CHART_CONFIG['grid_color'],
        'grid.linestyle': CHART_CONFIG['grid_style'],
        'grid.linewidth': 0.6,
        'grid.alpha': CHART_CONFIG['grid_alpha'],
        'xtick.labelsize': CHART_CONFIG['tick_size'],
        'ytick.labelsize': CHART_CONFIG['tick_size'],
        'legend.fontsize': CHART_CONFIG['legend_size'],
        'figure.dpi': CHART_CONFIG['dpi'],
        'savefig.dpi': CHART_CONFIG['dpi'],
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.08,
    })

# ─────────────────────────────────────────────────────────────────────────────
# 6. TABLE BUILDER & FORMATTING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def format_status_badge(status_str: str) -> str:
    """Return colored status string (PASS in green, FAIL in red)."""
    s = (status_str or "").strip().upper()
    if "PASS" in s:
        return r"\textcolor{osdagPass}{\textbf{PASS}}"
    elif "FAIL" in s:
        return r"\textcolor{osdagFail}{\textbf{FAIL}}"
    return status_str

def format_ur(val: Any, threshold: float = 1.0) -> str:
    """Format utilization ratio with red alert text if exceeding limit."""
    try:
        f = float(val)
        formatted = f"{f:.2f}"
        if f > threshold:
            return r"\textcolor{osdagFail}{\textbf{" + formatted + r"}}"
        return formatted
    except (TypeError, ValueError):
        return str(val) if val is not None else "---"

def build_longtable_header(
    col_spec: str,
    caption: str,
    header_rows: str,
    cont_caption: Optional[str] = None,
    num_cols: Optional[int] = None,
    label: Optional[str] = None,
) -> str:
    """
    Generate standard longtable structure with repeating headers and footers.
    Includes:
      - First head with primary caption (bold)
      - Subsequent head with continuation caption
      - Intermediate footer indicating continuation
      - Final footer closing the table rule
    """
    import re
    # Clean caption: strip outer \\textbf{...} if already passed
    clean_caption = caption.strip()
    if clean_caption.startswith(r"\textbf{") and clean_caption.endswith("}"):
        clean_caption = clean_caption[8:-1]

    lbl_str = f"\\label{{{label}}}" if label else ""
    cont_cap_text = (cont_caption or (clean_caption + r" \textit{(Continued)}")).strip()

    if num_cols is not None:
        c_num = num_cols
    else:
        # Safely compute column count by stripping curly braces first
        spec_no_braces = re.sub(r"\{[^{}]*\}", "", col_spec)
        c_num = max(spec_no_braces.count('|') - 1, 1) if '|' in spec_no_braces else max(
            spec_no_braces.count('c') + spec_no_braces.count('l') + spec_no_braces.count('r') + spec_no_braces.count('p'),
            1
        )

    return (
        r"\needspace{10\baselineskip}" + "\n"
        r"\begin{longtable}{" + col_spec + r"}" + "\n"
        r"\caption{\textbf{" + clean_caption + r"}} " + lbl_str + r" \\" + "\n"
        r"\hline" + "\n"
        + header_rows + "\n"
        r"\hline" + "\n"
        r"\endfirsthead" + "\n\n"
        r"\multicolumn{" + str(c_num) + r"}{l}{\small\textit{" + cont_cap_text + r"}} \\[4pt]" + "\n"
        r"\hline" + "\n"
        + header_rows + "\n"
        r"\hline" + "\n"
        r"\endhead" + "\n\n"
        r"\hline" + "\n"
        r"\multicolumn{" + str(c_num) + r"}{r}{\footnotesize\textit{Continued on next page\dots}} \\" + "\n"
        r"\endfoot" + "\n\n"
        r"\endlastfoot" + "\n"
    )
