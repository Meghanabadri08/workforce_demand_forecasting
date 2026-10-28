# Workforce Demand Forecasting & Skill Gap Analysis

A Python + Streamlit prototype that helps a workforce planner explore synthetic monthly demand, employee skills, capacity, allocations, potential gaps, and data-quality exceptions.

> **Project status:** executable prototype using synthetic demonstration data. It is not a production HR system and does not train a validated machine-learning forecasting model. Read [Limitations](#limitations-and-known-gaps) before interpreting results.

## 1. Business problem

Organisations need to understand whether the workforce has the right roles and skills available for planned projects. This prototype provides a small, reproducible environment to explore:

- workforce and project demand over time;
- employee skill profiles and verification/expiry information;
- employee availability, leave, and project allocations;
- estimated skill gaps and potential utilization risks;
- data validation results and labelled edge cases.

## 2. Technology and environment

- **OS:** Windows 10/11 instructions below; macOS/Linux can use equivalent shell commands.
- **Python:** use **Python 3.13.x (64-bit)** for the most predictable compatibility with the dependencies. Python 3.15 is very new and some packages may not yet support it consistently.
- **Editor:** Visual Studio Code (VS Code).
- **Libraries:** pandas, NumPy, Streamlit, Plotly, pytest.
- **Data:** locally generated synthetic CSV files; no external HR data or credentials are needed.

Install Python from [Python for Windows](https://www.python.org/downloads/windows/) and VS Code from [Visual Studio Code](https://code.visualstudio.com/). During Python setup, enable **Add Python to PATH** if the installer offers it. Close and reopen VS Code after installation.

## 3. Download/open the project

1. Download or clone this repository.
2. Extract the ZIP if you downloaded a ZIP file.
3. Open VS Code.
4. Choose **File → Open Folder** and select the `workforce_planning_project` folder — the folder that directly contains `app.py`, `requirements.txt`, `README.md`, `src/`, and `schema/`.
5. In VS Code, choose **Terminal → New Terminal**.
6. Confirm the terminal is in the project folder:

   ```powershell
   pwd
   dir
   ```

   The `dir` output should include `app.py` and `requirements.txt`. If the terminal is one folder above the project, run `cd workforce_planning_project` (adjust the path if you extracted it elsewhere).

### If the ZIP extracted into a nested folder

If VS Code shows `workforce_planning_project` inside another `workforce_planning_project` folder, use this command from the outer folder:

```powershell
cd .\workforce_planning_project\workforce_planning_project
```

Run `dir` and make sure `app.py` and `requirements.txt` are visible before continuing. If your folder structure is not nested, do not use this command; open the folder that directly contains `app.py` instead.

## 4. Set up Python on Windows (PowerShell)

Run these commands in the VS Code terminal, from the project root.

### 4.1 Check Python

```powershell
py --version
```

If the output is not Python 3.13.x, install Python 3.13.x from the official download page above. If `py` is not recognised, restart VS Code after installing Python and try again. You can also check `python --version`.

### 4.2 Create and activate a virtual environment

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
```

If the project is in a location where you do not have write permission, move/extract it into a folder you own, such as a folder under your user profile. If PowerShell reports that script execution is blocked, either use **Command Prompt** and run `.venv\Scripts\activate.bat`, or use the virtual environment's Python directly in the commands below. Do not change machine-wide security policy just to activate the environment.

After activation, the terminal prompt normally begins with `(.venv)`. Confirm the interpreter:

```powershell
python --version
python -m pip --version
```

### 4.3 Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Wait for the command to finish. If dependency installation fails under Python 3.15, install Python 3.13.x and recreate `.venv` with `py -3.13 -m venv .venv`.

## 5. Generate data, validate it, and run the dashboard

Run each command from the project root, with the virtual environment active.

### 5.1 Generate starter data (recommended first run)

```powershell
python src/data_generator.py --scale starter --seed 20261022 --output data
```

This creates reproducible CSV files and supporting JSON artefacts in `data/`.

### 5.2 Run validation

```powershell
python src/validation.py
```

Review `data/validation_summary.json`. The generator and validation script check defined structural and arithmetic rules. Some labelled anomaly cases are intentionally present to support exception demonstrations; inspect `data/ground_truth.json` and the validation report rather than assuming every generated row is clean.

### 5.3 Launch the Streamlit app

```powershell
python -m streamlit run app.py
```

If Python is available as `py` on your Windows computer, this equivalent command also works:

```powershell
py -m streamlit run app.py
```

Run the command while the terminal is inside the folder containing `app.py`. Streamlit should print a local address, usually `http://localhost:8501`, and may open a browser automatically. If it does not, copy the local address from the terminal into your browser. To stop the app, focus the terminal and press `Ctrl+C`.

### 5.4 Generate full-scale data (optional)

Only after the starter run works, use:

```powershell
python src/data_generator.py --scale full --seed 20261022 --output data
python src/validation.py
python -m streamlit run app.py
```

The full configuration is intended to generate a larger synthetic workforce dataset. It replaces the files in `data/`; back up starter outputs first if you need to keep them.

## 6. How to verify core behaviour

1. Confirm the data-generation command finishes without a traceback.
2. Confirm the `data/` folder contains generated CSV files, `ground_truth.json`, `source_manifest.json`, and `validation_summary.json`.
3. Open `data/validation_summary.json` and review the reported checks and any failures.
4. Start the dashboard and check that the page loads and its tabs/summary metrics/charts render.
5. Change the generated seed and regenerate if you want to compare different synthetic data. Reusing the same scale and seed is intended to produce reproducible data under the same dependency environment.
6. Optional test command, if you want to run the included tests:

   ```powershell
   python -m pytest -q
   ```

   Automated tests are supplementary; a passing test run does not prove the business logic is production-ready.

## 7. Project structure

```text
workforce_planning_project/
├── app.py                         # Streamlit dashboard
├── requirements.txt               # Python dependencies
├── README.md                      # Setup, run, verification and limitations
├── AI_USAGE.md                    # AI use disclosure and review notes
├── AI_PROMPT_HISTORY.md           # Prompt record available for this submission
├── docs/
│   └── DESIGN_AND_VALIDATION.md   # Assumptions, checks and next steps
├── data/                          # Generated synthetic CSV/JSON artefacts
├── schema/
│   └── data_dictionary.csv        # Field-level data dictionary
├── src/
│   ├── data_generator.py          # Deterministic synthetic-data generator
│   ├── validation.py              # Data validation checks
│   └── schema.sql                 # Relational schema reference
└── tests/
    └── test_project.py            # Starter generator/reproducibility tests
```

Generated data files are reproducible outputs, not source-of-truth real business records. Keep the generator, seed, manifest and validation report together when sharing results.

## 8. Data, assumptions, and design choices

- Data is synthetic and uses placeholder employee/project names; it is not real employee information.
- The seed `20261022` is used for reproducibility.
- The data represents a demonstration planning scenario, not a live company workforce.
- Capacity and leave are simplified; a real implementation should use an agreed work calendar, holidays, FTE rules and leave policy.
- Skill verification/expiry and demand-skill matching are demonstrative. Real hiring/training decisions require reviewed role requirements, location, cost, availability, employee preferences and business constraints.
- `ground_truth.json` contains labels for injected demonstration cases. It should be treated as evaluation/reference data, not an input feature for a predictive model.
- The demand data is generated synthetically. It is **not** a trained forecasting model and no real-world forecast accuracy is claimed.

## 9. AI use and prompt transparency

This project was developed with assistance from ChatGPT for project setup, implementation guidance, debugging, documentation and explaining commands. See:

- [`AI_USAGE.md`](AI_USAGE.md) for how AI was used and what needs human review;
- [`AI_PROMPT_HISTORY.md`](AI_PROMPT_HISTORY.md) for the prompt record available from this ChatGPT work.

The prompt history must be checked and supplemented by the author with any prompts submitted to other AI tools or conversations not represented in the supplied record. Do not claim prompts from other tools are included unless they have actually been added. The author should personally run the project, inspect the generated outputs, and be able to explain every submitted component.

## 10. Public GitHub repository and work history

The submission guidelines request a public GitHub repository and meaningful commits. This local project package does **not** create or publish a GitHub repository automatically. Before submission:

1. Create a public repository on GitHub.
2. Add these project files (do not add `.venv/`, credentials, or unrelated personal files).
3. Make meaningful commits that describe real changes, for example `Add deterministic data generator`, `Add validation and schema documentation`, and `Document setup and AI use` — only use commit messages that match work actually performed.
4. Verify the repository URL opens in a private/incognito browser window.

## 11. Limitations and known gaps

- This is a focused prototype, not a complete workforce management platform.
- Demand is synthetic and not statistically forecast from historical actuals; no MAE/RMSE forecast evaluation is available.
- Gap and exception views are demonstration-oriented and should not be treated as authoritative HR decisions. Validate the specific detector logic against the generated labels before describing any anomaly type as fully detected.
- SQL DDL is provided as a schema reference; the app does not require a database server for the basic CSV workflow.
- Authentication, authorisation, audit trails, privacy controls, real HR integrations, deployment and production monitoring are outside the current scope.
- Synthetic sample sizes and rules may need adjustment to match the exact business specification.

## 12. Next steps

1. Run the starter workflow from a clean environment and capture evidence of successful generation, validation and dashboard launch.
2. Review every validation result and manually inspect sample rows and injected labels.
3. Improve anomaly detectors and add explicit tests for each anomaly type.
4. If real historical demand becomes available and approved for use, create time-based train/validation/test splits and evaluate a forecasting baseline with suitable metrics.
5. Add reviewed role-to-skill mappings, work calendars, allocation conflict logic, hiring/training costs and scenario comparisons.
6. Publish to GitHub and complete the prompt history with all other AI tools actually used.
   ## 13. deployment link (OUTPUT) : https://workforcedemandforecasting-b3dbqbcf9wtdyzvjbnmwyu.streamlit.app/
