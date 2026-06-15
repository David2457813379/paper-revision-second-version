# Second Revision Audit Summary

Date: 2026-06-15

## Scope

This audit covers the four-notebook computational workflow for the revised manuscript on EUI prediction and EUI-OCEI coupling analysis for Beijing hotel buildings.

## Main Fixes

| Area | Revision |
|---|---|
| Notebook execution | Notebook 01 now generates a deterministic smoke-test dataset when EnergyPlus is not launched, preventing the workflow from stopping after IDF generation. |
| EnergyPlus parser | The SQLite field name was corrected from the corrupted `Reporting频数` string to `ReportingFrequency`. |
| Cell explanations | Chinese and English explanations are now separated into two Markdown cells before each code cell. |
| International-journal figures | Figure titles, axis labels, legends, and printed results are in English. |
| Parameter naming | Original manuscript/code parameter names are preserved, including `wwr`, `u_wall`, `u_roof`, `room_count`, `eui_kwh_m2`, and `OCEI_kgco2e_m2`. |
| Feasibility screening | KS statistics and Jensen-Shannon distances are exported for pre/post screening distribution diagnostics. |
| Nonlinear sensitivity | XGBoost-SHAP ranking is added as a nonlinear robustness check for SRC. |
| Variable selection | The 18-variable cutoff is supported by cumulative SRC contribution and cross-validation plateau evidence. |
| ML transparency | Model hyperparameters and search spaces are exported to CSV. |
| Carbon accounting | Emission-factor sensitivity and decarbonisation scenarios are included. |

## Validation

Validation command settings:

```text
EUI_FAST_MODE=1
EUI_N_SAMPLES=500
EUI_RUN_ENERGYPLUS=0
```

Execution status:

| Notebook | Status |
|---|---|
| 01_Parametric_Simulation_Database_Construction.ipynb | Passed |
| 02_SRC_Sensitivity_and_Variable_Selection.ipynb | Passed |
| 03_ML_Model_Training_and_Evaluation.ipynb | Passed |
| 04_EUI_OCEI_Coupling_and_Carbon_Analysis.ipynb | Passed |

Final language audit:

| Notebook | Code cells | Chinese explanation cells | English explanation cells | Chinese text in code/output |
|---|---:|---:|---:|---:|
| Notebook 01 | 12 | 12 | 12 | 0 |
| Notebook 02 | 15 | 15 | 15 | 0 |
| Notebook 03 | 13 | 13 | 13 | 0 |
| Notebook 04 | 17 | 17 | 17 | 0 |

## Remaining Boundary

The smoke-test dataset is for workflow validation only. Formal manuscript results should be regenerated with:

```text
EUI_FAST_MODE=0
EUI_N_SAMPLES=20000
EUI_RUN_ENERGYPLUS=1
```

The reported machine-learning performance must be framed as surrogate fidelity on EnergyPlus-derived data, not as verified real-building prediction accuracy.
