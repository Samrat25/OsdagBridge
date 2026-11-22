from osdagbridge.core.reports.report_utils import _tex
from osdagbridge.core.reports.styles import build_longtable_header


def ch1_project_info(m):
    return r"""
\chapter{Project Information}

This section records all project metadata as entered by the designer.

\section{Project and Design Team Details}
\label{sec:project-details}

""" + build_longtable_header(
    col_spec=r"|L{5.5cm}|L{8.5cm}|",
    caption="Project and Design Team Details",
    header_rows=r"\textbf{Parameter} & \textbf{Details} \\",
    num_cols=2,
    label="tab:project-details"
) + r"""
\textnormal{Project Name} & """ + _tex(m.project_name) + r""" \\
\hline
\textnormal{Project Location} & """ + _tex(m.project_location) + r""" \\
\hline
\textnormal{Designer} & """ + _tex(m.designer) + r""" \\
\hline
\textnormal{Reviewer} & """ + _tex(m.reviewer) + r""" \\
\hline
\textnormal{Organization} & """ + _tex(m.company) + r""" \\
\hline
\textnormal{Client} & """ + _tex(m.client) + r""" \\
\hline
\textnormal{Software Version} & OsdagBridge \\
\hline
\end{longtable}


\section{Applicable Codes and Standards}
\label{sec:codes}

\begin{itemize}
\item Indian Roads Congress (IRC) 5: General Features of Design
\item Indian Roads Congress (IRC) 6: Loads and Load Combinations
\item Indian Roads Congress (IRC) 22: Composite Construction (Limit State Design)
\item Indian Roads Congress (IRC) 24: Steel Road Bridges (Limit State Method)
\item Indian Roads Congress (IRC) 112: Concrete Road Bridges (deck design)
\item Indian Roads Congress Special Publication (IRC SP) 114: Seismic Design of Road Bridges
\item Indian Standard (IS) 800: General Construction in Steel
\item Indian Standard (IS) 2062: Hot Rolled Structural Steel Specification
\item Indian Standard (IS) 6006: Steel Bearings
\end{itemize}
"""


