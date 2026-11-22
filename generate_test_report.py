import os
import sys

# Ensure site-packages on D:\ are included if running D:\python.exe or standalone
d_site = r"D:\Lib\site-packages"
if os.path.exists(d_site) and d_site not in sys.path:
    sys.path.insert(0, d_site)

import unittest.mock

# Ensure openseespy is mocked if not installed
if 'openseespy' not in sys.modules:
    sys.modules['openseespy'] = unittest.mock.MagicMock()
    sys.modules['openseespy.opensees'] = unittest.mock.MagicMock()

# Ensure .tinytex pdflatex is in PATH
tinytex_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.tinytex', 'TinyTeX', 'bin', 'windows')
if os.path.exists(tinytex_bin) and tinytex_bin not in os.environ.get('PATH', ''):
    os.environ['PATH'] = tinytex_bin + os.pathsep + os.environ.get('PATH', '')

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from osdagbridge.core.bridge_types.plate_girder.defaults import solve_extend_basic_input_dict, BASIC_INPUT_DICT
from osdagbridge.core.reports.report_generator import build_report_payload, generate_report, ReportRequest, ReportMetadata, ReportOptions
from osdagbridge.core.utils.common import KEY_SPAN, KEY_CARRIAGEWAY_WIDTH, KEY_SKEW_ANGLE

def run(output_stem="Report_Test"):
    inp = dict(BASIC_INPUT_DICT)
    inp[KEY_SPAN] = 24.0
    inp[KEY_CARRIAGEWAY_WIDTH] = 7.5
    inp[KEY_SKEW_ANGLE] = 0.0
    solve_extend_basic_input_dict(inp)
    req = ReportRequest(
        metadata=ReportMetadata(
            project_name='Short-Span Steel Girder Bridge',
            project_location='Mumbai, MH',
            designer='Osdag Team',
            client='Ministry of Road Transport',
            company='IIT Bombay'
        ),
        options=ReportOptions(
            sections=['loads', 'analysis', 'design_checks', 'drawings'],
            include_figures=True,
            include_toc=True,
            include_pdf=True
        ),
        output_dir='.',
        file_stem=output_stem
    )
    payload = build_report_payload(req, inp, {})
    res = generate_report(payload, req)
    print("Report result:", res)
    return res

if __name__ == '__main__':
    stem = sys.argv[1] if len(sys.argv) > 1 else "Report_Test"
    run(stem)
