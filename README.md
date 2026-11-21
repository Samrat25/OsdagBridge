# OsdagBridge

OsdagBridge is a modular, shared-core software plugin for the analysis and design of steel bridges within the Osdag ecosystem.  
It supports desktop (PySide6), web (Django + React), and CLI interfaces through a unified Python core.

The system currently supports:
- Plate Girder Bridges  
 

Additional bridge types can be added through the plugin architecture.

---

## Key Features

### Shared Core Architecture
All numerical logic and I/O are implemented once in `osdagbridge.core`.  
The desktop GUI, web app, and CLI all reuse the same core for consistent behavior.

### Modular Bridge-Type System
Each bridge type includes:
- DTO (input model schema)
- Initial sizing routines
- Structural analysis configuration
- Design and code-check modules
- CAD geometry generation
- Report generation utilities

### Reusable Bridge Components
Common structural elements are defined in `bridge_components/`:
- Girders  
- Decks  
- Crash barriers  
- Pedestals  
- Piers  
- Foundations  
- Piles and pile caps  

Components are shared across multiple bridge types.

### Multi-Solver Analysis Support
Multiple analysis backends are supported:
- Native lightweight FEM solver  
- OpenSeesPy  
- OspGrillage  

Solvers are switchable at runtime via adapters.

### Integrated Indian Standards
Included under `core/utils/codes/`:
- IRC:6–2017  
- IRC:22–2015  
- IRC:24–2010  

These modules provide load models, combinations, material factors, and code checks.

---

## Project Structure

```
OsdagBridge/
├── docs/
├── examples/
├── tests/
└── src/
    └── osdagbridge/
        ├── core/              # Analysis, design, IO, solvers, codes
        ├── bridge_types/      # Plate girder, box girder, truss
        ├── bridge_components/ # Reusable components
        ├── cli/               # Command-line interface
        ├── desktop/           # PySide6 GUI
        └── web/               # Django + React web stack
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/osdag-admin/OsdagBridge.git
cd OsdagBridge
```

Install in editable mode:

```bash
pip install -e .
```

---

## Usage

### Command-Line Interface

Run an analysis:

```bash
osdagbridge analyze project.yaml --solver native
```

Generate a report:

```bash
osdagbridge report project.yaml report.pdf
```

### Desktop Application

```bash
python -m osdagbridge.desktop
```

### Web Application

Backend:

```bash
python src/osdagbridge/web/backend/manage.py runserver
```

Frontend:

```bash
cd src/osdagbridge/web/frontend
npm install
npm start
```

---

## Report Generation & Architecture

OsdagBridge features an automated, code-compliant PDF design report generator built on top of PyLaTeX and LaTeX (TinyTeX / TeX Live). The report compiles engineering design outputs, load combinations, code checks, and structural drawings into a publication-ready PDF document adhering to Indian Standards (IRC 5, IRC 6, IRC 22, IRC 24, IS 800, IS 456).

### Headless Report Generation

To regenerate design reports directly from the terminal without launching the GUI (e.g., in CI or server environments):

```bash
# Generate report using default test configuration (outputs Report_After.pdf and Report_After.tex)
python generate_test_report.py Report_After
```

The script automatically sets up the environment, mocks finite-element dependencies if not installed locally, applies bridge sizing and IRC loading rules, generates all data-driven visual charts, and compiles the document using the portable TinyTeX distribution.

### Desktop GUI Report Generation

To generate reports interactively through the desktop application:

```bash
cd src
python -m osdagbridge.desktop
```

1. Navigate to the **Plate Girder** bridge design window.
2. Configure parameters or keep default geometric and material properties.
3. In the Additional Inputs dialog, customize **Loading** parameters (select desired IRC vehicle classes, impact factors, and footpath configurations).
4. Click **Design** to perform grillage analysis and design code checks.
5. Click **Generate Report** to launch the report options dialog, select desired chapters, and click **Save PDF**.

### Key Report Refactoring Highlights

- **Centralized Style Architecture (`styles.py`)**: All layout rules, page geometry (`top=22mm, bottom=28mm, footskip=18pt`), margins, color palettes (`#91B014`, `#2C3E50`, `#C0392B`, `#1E8449`), table row spacing, header/footer pagestyles (`fancyhdr`), and Matplotlib figure configurations are centralized in a single module.
- **Repeating Headers on Multi-Page Tables**: All tables spanning multiple pages are standardized with LaTeX `longtable` using `\endfirsthead`, `\endhead`, `\endfoot`, and `\endlastfoot`, ensuring column titles repeat across page boundaries with clear `(Continued)` indicators.
- **Footer Collision Prevention**: Resolved multi-line row bleeding into footers (such as girder G4 check rows) by adjusting page geometry (`bottom=28mm`, `footskip=18pt`), binding multi-row records with `\\*[6pt]`, and applying `\needspace` buffers.
- **Structured Chapter 3 Loads**: Split combined loads into two dedicated tables:
  1. *Live Loads (LL)*: Tabulates selected vehicle classes, dynamic impact factors $(1 + i_m)$, longitudinal braking forces (kN), and tangent centrifugal forces (0.00 kN) matching user-selected UI inputs.
  2. *Footway & Pedestrian Live Load*: Details footpath configuration, width, thickness, pressure mode, and design pedestrian load ($4.905\text{ kN/m}^2$ per IRC 6 Cl. 206.1) with a dedicated Unit column.
- **Dynamic Data-Driven Visual Charts (`charts.py`)**:
  - *Section 5.5 Overall Design Check Summary*: Embedded high-resolution Matplotlib bar chart of governing Utilization Ratios across Girders, Deck Slab, Cross Bracing, and End Diaphragms, with a red dashed line at $UR = 1.0$ and visual fail distinctions.
  - *Chapter 7 Material Take-off*: Embedded dual charts showing structural steel tonnage breakdown (MT) and concrete volume ($m^3$) vs. reinforcement steel weight (MT).

---

## Testing

Run the complete test suite:

```bash
pytest -q
```

Continuous integration runs automatically through GitHub Actions (`.github/workflows/ci.yml`).

---

## Development Guidelines

### Key Code Locations
- Core logic: `src/osdagbridge/core/`
- Codes & standards: `src/osdagbridge/core/utils/codes/`
- Bridge types: `src/osdagbridge/bridge_types/`
- Components: `src/osdagbridge/bridge_components/`
- CLI: `src/osdagbridge/cli/`
- Desktop GUI: `src/osdagbridge/desktop/`
- Web backend/frontend: `src/osdagbridge/web/`

### Contribution Workflow
1. Fork the repository  
2. Create a feature branch  
3. Ensure all tests pass (`pytest`)  
4. Submit a pull request

---

## Acknowledgements

OsdagBridge is part of the Osdag project, promoting open-source tools for steel design education, research, and practice.

---

## License

This project is licensed under the MIT License.  
See the `LICENSE` file for full details.
