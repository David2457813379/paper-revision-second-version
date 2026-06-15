# Second Revision Code Package / 论文修改第二版

This repository contains the second-revision computational package for the manuscript:

**EUI Prediction and Energy-Carbon Coupling Analysis for Beijing Hotel Buildings Using Parametric Simulation and Machine Learning**

The package is organised as a four-step reproducible Jupyter workflow:

1. `01_Parametric_Simulation_Database_Construction.ipynb`
   - Latin Hypercube Sampling (LHS)
   - geometry/function feasibility screening
   - EnergyPlus IDF generation
   - EnergyPlus result parsing or deterministic smoke-test data generation
   - Step 1 diagnostic and benchmark figures

2. `02_SRC_Sensitivity_and_Variable_Selection.ipynb`
   - VIF screening
   - standardised regression coefficients (SRC)
   - bootstrap confidence intervals
   - XGBoost-SHAP nonlinear robustness check
   - 18-variable cutoff evidence

3. `03_ML_Model_Training_and_Evaluation.ipynb`
   - model training and comparison
   - leakage-safe `Pipeline` objects
   - hyperparameter search reporting
   - non-core-variable impact analysis
   - predicted-versus-simulated EUI figures

4. `04_EUI_OCEI_Coupling_and_Carbon_Analysis.ipynb`
   - carrier-specific carbon accounting
   - OCEI calculation
   - emission-factor sensitivity analysis
   - EUI-OCEI ranking and coupling analysis
   - carbon-intensity surrogate modelling

## Revision Principles

This second version follows four strict rules requested for international-journal submission:

- Original code parameter and column names are preserved, for example `wwr`, `u_wall`, `room_count`, `eui_kwh_m2`, and `OCEI_kgco2e_m2`.
- All figure labels, legends, axis titles, printed outputs, and result tables are in English.
- Chinese and English cell explanations are separated into two Markdown cells before each code cell.
- The Chinese explanation cells are for author-side checking only and can be deleted before submission without affecting the code.

Each code cell has the following structure:

```text
Chinese explanation cell
English explanation cell
Code cell
```

Final audit after execution:

| Notebook | Code cells | Chinese explanation cells | English explanation cells | Chinese text in code/output |
|---|---:|---:|---:|---|
| Notebook 01 | 12 | 12 | 12 | 0 |
| Notebook 02 | 15 | 15 | 15 | 0 |
| Notebook 03 | 13 | 13 | 13 | 0 |
| Notebook 04 | 17 | 17 | 17 | 0 |

## Environment

The workflow was validated locally with:

- Python 3.11.5
- NumPy 2.4.3
- pandas 3.0.1
- SciPy 1.17.1
- scikit-learn 1.8.0
- statsmodels 0.14.6
- Matplotlib 3.10.8
- seaborn 0.13.2
- SHAP 0.51.0
- XGBoost 3.2.0
- LightGBM 4.6.0
- EnergyPlus 25.2.0 for formal simulation runs

Install the Python dependencies with:

```powershell
pip install -r requirements.txt
```

## Quick Validation Mode

The notebooks support a smoke-test mode that does not launch EnergyPlus. It is intended for code review, local debugging, and reviewer-side workflow verification.

```powershell
$env:EUI_FAST_MODE = "1"
$env:EUI_N_SAMPLES = "500"
$env:EUI_RUN_ENERGYPLUS = "0"
jupyter notebook
```

In this mode, Notebook 01 generates a deterministic dataset with `simulation_mode = engineering_smoke_test`. This dataset is not a substitute for formal EnergyPlus simulation results in the manuscript. It only keeps the four-step pipeline executable on machines where a long EnergyPlus batch is not being launched.

The final local smoke-test validation used:

```text
EUI_FAST_MODE=1
EUI_N_SAMPLES=500
EUI_RUN_ENERGYPLUS=0
```

All four notebooks completed successfully in sequence.

## Formal EnergyPlus Mode

Formal manuscript results should be regenerated with EnergyPlus enabled:

```powershell
$env:EUI_FAST_MODE = "0"
$env:EUI_N_SAMPLES = "20000"
$env:EUI_RUN_ENERGYPLUS = "1"
jupyter notebook
```

Expected workflow:

1. Run Notebook 01 and generate the full EnergyPlus simulation dataset.
2. Confirm `data/step1_simulation_dataset.csv` contains the formal simulation records.
3. Run Notebooks 02, 03, and 04 in order.
4. Replace smoke-test outputs with formal EnergyPlus-based outputs before final manuscript submission.

The full simulation is expected to retain approximately 4,640 feasible samples from 20,000 LHS candidates and may require 16-24 hours depending on hardware and EnergyPlus configuration.

## Key Outputs

Important reviewer-response outputs include:

- `outputs_step1/feasibility_screening_variable_distribution_shift.csv`
- `outputs_step1/figures/feasibility_screening_analysis.png`
- `outputs_step1/figures/eui_measured_comparison.png`
- `outputs_step2/src_shap_ranking_comparison.csv`
- `outputs_step2/figures/src_vs_shap_comparison.png`
- `outputs_step2/figures/variable_selection_analysis.png`
- `outputs_step3/model_hyperparameters.csv`
- `outputs_step3/noncore_variable_impact.csv`
- `outputs_step4/emission_factor_sensitivity.csv`
- `outputs_step4/figures/emission_factor_sensitivity.png`
- `outputs_step4/figures/carbon_contribution_dual_view.png`

The repository includes the key CSV tables and publication-check figures needed to document the second-revision workflow. The full local output folder can be regenerated by running the four notebooks in sequence.

## Reviewer-Response Coverage

The second revision addresses the major code-level reviewer concerns:

- Sim-to-real transfer gap: simulated EUI is benchmarked against measured Beijing hotel EUI statistics.
- Feasibility-screening bias: pre/post distributions, KS statistics, and Jensen-Shannon distances are reported.
- SRC linearity limitation: SHAP-based nonlinear ranking is added.
- Variable cutoff justification: the 18-variable threshold is supported by cumulative SRC contribution and cross-validation plateau evidence.
- Hyperparameter reproducibility: final model parameters and search spaces are exported.
- Information leakage risk: preprocessing is handled inside scikit-learn pipelines.
- Non-core-variable fixation: full-variable and 18-variable models are compared.
- Carbon-factor uncertainty: emission-factor sources and grid-decarbonisation sensitivity scenarios are reported.

## Important Limitation

High model performance in this package indicates surrogate fidelity on EnergyPlus-derived simulation data. It must not be described as direct prediction accuracy for real hotel buildings unless an external measured-building validation dataset is added.
