"""Prepare the second-version notebooks for international-journal submission.

The script edits notebooks structurally with nbformat:

1. split the prior bilingual explanation blocks into two separate cells
   (Chinese first, English second);
2. keep original data/parameter column names unchanged;
3. convert figure labels, legends, and printed results to English;
4. fix Step 1 debug-mode execution so a reproducible smoke-test dataset is
   generated when EnergyPlus is not launched;
5. fix the EnergyPlus SQLite field name used in the parser.
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

import nbformat
from nbformat.v4 import new_markdown_cell


TARGET = Path(r"C:\Users\xiaol\1论文修改第二版")

NOTEBOOKS = [
    "01_Parametric_Simulation_Database_Construction.ipynb",
    "02_SRC_Sensitivity_and_Variable_Selection.ipynb",
    "03_ML_Model_Training_and_Evaluation.ipynb",
    "04_EUI_OCEI_Coupling_and_Carbon_Analysis.ipynb",
]

OLD_START = "<!-- CODEx bilingual cell explanation: start -->"
OLD_END = "<!-- CODEx bilingual cell explanation: end -->"
ZH_START = "<!-- CODEx Chinese cell explanation: start -->"
ZH_END = "<!-- CODEx Chinese cell explanation: end -->"
EN_START = "<!-- CODEx English cell explanation: start -->"
EN_END = "<!-- CODEx English cell explanation: end -->"


def between(text: str, start: str, end: str) -> str:
    if start not in text:
        return ""
    s = text.index(start) + len(start)
    if end in text[s:]:
        e = text.index(end, s)
        return text[s:e].strip()
    return text[s:].strip()


def parse_old_explanation(src: str, ordinal: int) -> dict[str, str]:
    title_match = re.search(r"^###\s*Cell\s*(\d+)\s*[—-]\s*(.+?)(?:\s*/\s*(.+))?$", src, re.M)
    cell_no = title_match.group(1) if title_match else f"{ordinal:02d}"
    zh_title = title_match.group(2).strip() if title_match else f"Cell {cell_no}"
    en_title = title_match.group(3).strip() if title_match and title_match.group(3) else zh_title

    zh_desc = between(src, "**中文说明**：", "**输入与依赖**")
    en_desc = between(src, "**English explanation**:", "**Inputs and dependencies**")
    zh_review = between(src, "**审稿意见对应**：", "**English explanation**")
    en_review = between(src, "**Reviewer-response link**:", OLD_END)

    if not zh_desc:
        zh_desc = "本 cell 执行论文代码包中的一个可复现计算步骤，并为后续分析提供数据、图表或诊断结果。"
    if not en_desc:
        en_desc = "This cell executes one reproducible computational step in the manuscript code package and provides data, figures, or diagnostics for downstream analysis."
    if not zh_review:
        zh_review = "对应审稿意见：用于支撑修订版论文的可复现性、方法透明度或结果稳健性。"
    if not en_review:
        en_review = "Reviewer-response link: supports reproducibility, methodological transparency, or result robustness in the revised manuscript."

    return {
        "cell_no": cell_no,
        "zh_title": zh_title,
        "en_title": en_title,
        "zh_desc": zh_desc.rstrip("。") + "。",
        "en_desc": en_desc.rstrip(".") + ".",
        "zh_review": zh_review.strip(),
        "en_review": en_review.strip(),
    }


def zh_cell(info: dict[str, str]) -> str:
    return textwrap.dedent(f"""
    {ZH_START}
    ### Cell {info['cell_no']} — 中文说明（提交前可删除）

    **研究目的**：{info['zh_desc']}

    **输入与依赖**：本 cell 依赖前序 cell 已定义的数据对象、配置参数、文件路径或模型对象；若它是当前 notebook 的第一个代码 cell，则依赖本地 Python/Jupyter 环境和项目目录结构。

    **输出与复现作用**：本 cell 生成内存对象、CSV 表格、图像文件、模型文件或诊断打印信息，并作为后续 notebook 步骤和论文修订证据链的一部分。

    **审稿意见对应**：{info['zh_review']}
    {ZH_END}
    """).strip()


def en_cell(info: dict[str, str]) -> str:
    return textwrap.dedent(f"""
    {EN_START}
    ### Cell {info['cell_no']} — {info['en_title']}

    **Research purpose**: {info['en_desc']}

    **Inputs and dependencies**: This cell depends on data objects, configuration values, file paths, or fitted model objects defined in previous cells; if it is the first code cell in the notebook, it depends on the local Python/Jupyter environment and the project directory structure.

    **Outputs and reproducibility role**: This cell generates in-memory objects, CSV tables, figure files, model files, or diagnostic printouts that become part of the downstream notebook workflow and the manuscript-revision evidence chain.

    **Reviewer-response link**: {info['en_review']}
    {EN_END}
    """).strip()


def split_explanation_cells(nb) -> None:
    new_cells = []
    pending = None
    code_ordinal = 0
    for cell in nb.cells:
        if cell.cell_type == "markdown" and (
            OLD_START in cell.source or ZH_START in cell.source or EN_START in cell.source
        ):
            if OLD_START in cell.source:
                pending = parse_old_explanation(cell.source, code_ordinal + 1)
            continue
        if cell.cell_type == "code":
            code_ordinal += 1
            info = pending or {
                "cell_no": f"{code_ordinal:02d}",
                "zh_title": f"Cell {code_ordinal:02d}",
                "en_title": f"Computational step {code_ordinal:02d}",
                "zh_desc": "本 cell 执行论文代码包中的一个可复现计算步骤，并为后续分析提供数据、图表或诊断结果。",
                "en_desc": "This cell executes one reproducible computational step in the manuscript code package and provides data, figures, or diagnostics for downstream analysis.",
                "zh_review": "对应审稿意见：用于支撑修订版论文的可复现性、方法透明度或结果稳健性。",
                "en_review": "Reviewer-response link: supports reproducibility, methodological transparency, or result robustness in the revised manuscript.",
            }
            new_cells.append(new_markdown_cell(zh_cell(info)))
            new_cells.append(new_markdown_cell(en_cell(info)))
            cell.outputs = []
            cell.execution_count = None
            new_cells.append(cell)
            pending = None
        else:
            new_cells.append(cell)
    nb.cells = new_cells


CODE_REPLACEMENTS = {
    '["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]': '["Arial", "Helvetica", "DejaVu Sans", "sans-serif"]',
    '"font.size": 11': '"font.size": 8',
    '"axes.titlesize": 13': '"axes.titlesize": 9',
    '"axes.labelsize": 12': '"axes.labelsize": 8',
    '"legend.fontsize": 10': '"legend.fontsize": 7',
    '"xtick.labelsize": 10': '"xtick.labelsize": 7',
    '"ytick.labelsize": 10': '"ytick.labelsize": 7',
    'Reporting频数': 'ReportingFrequency',
    "全部 LHS 样本": "All LHS samples",
    "下界": "Lower bound",
    "上界": "Upper bound",
    "可用面积/总建筑面积比": "Usable-to-gross floor area ratio",
    "样本数": "Sample count",
    "筛选前分布 | 保留率": "Pre-filter distribution | retention",
    "筛选前后分布对比（归一化）": "Pre- and post-filter distributions (normalised)",
    "筛选前": "Pre-filter",
    "筛选后": "Post-filter",
    "密度": "Density",
    "剔除样本": "Rejected samples",
    "保留样本": "Retained samples",
    "人均生活热水量（m3/(人·d)）": "dhw_per_person (m3/person/day)",
    "楼层数": "floor_num",
    "二维参数覆盖检验": "Two-dimensional parameter-space coverage",
    "可行性筛选分析 / FEASIBILITY SCREENING ANALYSIS": "FEASIBILITY SCREENING ANALYSIS",
    "筛选前样本数 / Pre-filter samples": "Pre-filter samples",
    "筛选后样本数 / Post-filter samples": "Post-filter samples",
    "剔除率 / Rejection rate": "Rejection rate",
    "筛选前面积比": "Pre-filter usable ratio",
    "筛选后面积比": "Post-filter usable ratio",
    "Pre-filter面积比": "Pre-filter usable ratio",
    "Post-filter面积比": "Post-filter usable ratio",
    "面积比两样本 KS 检验": "Two-sample KS test for usable ratio",
    "变量级分布偏移最大的前 10 项：": "Top 10 variables with the largest distribution shifts:",
    "变量分布偏移表已保存": "Variable-level distribution-shift table saved",
    "酒店建筑 EUI 分布": "EUI distribution of simulated hotel prototypes",
    "EUI（kWh/m2·a）": "EUI (kWh/m2.a)",
    "频数": "Frequency",
    "酒店建筑总能耗分布": "Site energy distribution of simulated hotel prototypes",
    "能耗（kWh）": "Site energy (kWh)",
    "平均终端能耗/负荷组成": "Mean end-use energy and load components",
    "选定变量相关矩阵": "Correlation matrix of selected variables",
    "建筑能源使用强度 EUI（kWh/(m2·a)）": "EUI (kWh/m2.a)",
    "Probability 密度": "Probability density",
    "模拟 EUI 与北京酒店实测数据对比": "Simulated EUI benchmarked against measured Beijing hotel data",
    "按 SRC 排序的前 20 个变量（线性）": "Top 20 variables ranked by SRC (linear)",
    "按 SHAP 排序的前 20 个变量（非线性）": "Top 20 variables ranked by SHAP (nonlinear)",
    "变量排序（按 |SRC|）": "Variable rank by |SRC|",
    "SRC 绝对值碎石图": "Scree plot of absolute SRC",
    "纳入变量数量": "Number of included variables",
    "累计 |SRC|（%）": "Cumulative |SRC| (%)",
    "SRC 累计贡献": "Cumulative SRC contribution",
    "预测能力随变量数量变化": "Predictive fidelity versus number of variables",
    "前 18 个标准化回归系数（SRC）": "Top 18 standardised regression coefficients (SRC)",
    "前 18 个 |SRC|（红色=符号稳定，蓝色=符号不稳定）": "Top 18 |SRC| values (red=sign-stable; blue=unstable)",
    "围护结构面积比与 EUI": "envelope_to_floor_ratio versus eui_kwh_m2",
    "楼层数与 EUI": "floor_num versus eui_kwh_m2",
    "楼层数与总能耗": "floor_num versus site_energy_kwh",
    "floor_num与 EUI": "floor_num versus eui_kwh_m2",
    "floor_num与总能耗": "floor_num versus site_energy_kwh",
    "均值": "Mean",
    "中位数": "Median",
    "模型训练样本 EUI 标签分布": "EUI label distribution for model training",
    "模型超参数报告 / MODEL HYPERPARAMETER REPORT": "MODEL HYPERPARAMETER REPORT",
    "前 5 名模型详细配置 / TOP 5 MODELS — DETAILED HYPERPARAMETERS": "TOP 5 MODELS - DETAILED HYPERPARAMETERS",
    "搜索空间 / Search space": "Search space",
    "模型测试集 R2 对比": "Test-set R2 by model",
    "模型测试集 RMSE 对比": "Test-set RMSE by model",
    "模型测试集 MAPE 对比": "Test-set MAPE by model",
    "模型 10 折 CV R2 方差对比": "Variance of 10-fold CV R2 by model",
    "CV R2 方差（越低越好）": "Variance of CV R2 (lower is better)",
    "泛化间隙（训练 R2 - 测试 R2）": "Generalisation gap (training R2 - test R2)",
    "预测 EUI 与仿真 EUI 对比（测试集）": "Predicted versus simulated EUI (test set)",
    "Simulated EUI（kWh/m2·a）": "Simulated EUI (kWh/m2.a)",
    "Predicted EUI（kWh/m2·a）": "Predicted EUI (kWh/m2.a)",
    "平均 OCEI（kgCO2e/(m2·a)）": "Mean OCEI (kgCO2e/m2.a)",
    "不同排放因子情景下的平均 OCEI": "Mean OCEI under emission-factor scenarios",
    "Top-10% 重叠率（%）": "Top-10% overlap (%)",
    "EUI-OCEI 耦合指标稳定性": "Stability of EUI-OCEI coupling metrics",
    "排放因子敏感性分析 / EMISSION FACTOR SENSITIVITY ANALYSIS": "EMISSION FACTOR SENSITIVITY ANALYSIS",
    "基准 OCEI": "Baseline OCEI",
    "EUI-OCEI 相关系数范围": "EUI-OCEI correlation range",
    "电力贡献占比范围": "Electricity share range",
    "天然气贡献占比范围": "Natural gas share range",
    "OCEI 分布": "OCEI distribution",
    "OCEI（kgCO2e/m2·a）": "OCEI (kgCO2e/m2.a)",
    "剔除 OCEI 缺失或非有限样本 / Dropping invalid OCEI rows": "Dropping rows with missing or non-finite OCEI",
    "电力": "Electricity",
    "天然气": "Natural gas",
    "区域供热": "District heating",
    "区域供冷": "District cooling",
    "各能源载体总碳排放贡献": "Total carbon-emission contribution by energy carrier",
    "年碳排放贡献（kgCO2e/a）": "Annual carbon-emission contribution (kgCO2e/a)",
    "各能源载体平均 OCEI 贡献": "Mean OCEI contribution by energy carrier",
    "OCEI 贡献（kgCO2e/(m2·a)）": "OCEI contribution (kgCO2e/m2.a)",
    "请先运行合并双视图碳贡献图 cell。": "Run the consolidated dual-view carbon-contribution cell first.",
    "归一化 OCEI 贡献已并入 carbon_contribution_dual_view.png，不再生成重复的单独图。": "The normalised OCEI contribution is included in carbon_contribution_dual_view.png; no duplicate standalone figure is generated.",
    "EUI 与 OCEI 交叉分析": "EUI-OCEI cross-analysis",
    "按 EUI 排名": "Rank by EUI",
    "按 OCEI 排名": "Rank by OCEI",
    "EUI 与 OCEI 排名偏移": "Rank shift between EUI and OCEI",
    "标准化回归系数绝对值（|SRC|）": "Absolute standardised regression coefficient (|SRC|)",
    "EUI 与 OCEI 关键因素对比": "Key-factor comparison between EUI and OCEI",
    "预测碳强度与计算碳强度对比": "Predicted versus calculated carbon intensity",
    "计算碳强度（kgCO2e/m2·a）": "Calculated carbon intensity (kgCO2e/m2.a)",
    "预测碳强度（kgCO2e/m2·a）": "Predicted carbon intensity (kgCO2e/m2.a)",
}


ENGLISH_MARKDOWN_REPLACEMENTS = {
    "可行性筛选的合理性论证": "Feasibility-screening justification",
    "EnergyPlus 模型可复现性文档": "EnergyPlus model reproducibility documentation",
    "SRC 方法的线性假设局限与补充验证": "Linear-assumption limitation of SRC and nonlinear supplementary validation",
    "模型超参数与非核心变量处理说明": "Model hyperparameters and non-core-variable handling",
    "碳排放因子数据来源与说明": "Emission-factor sources and accounting notes",
}


FORMAL_MARKDOWN = {
    "可行性筛选的合理性论证": """### Feasibility-screening justification

**Response to reviewer concerns about the 77% rejection rate and possible selection bias.** The usable-to-gross floor area ratio bounds of 0.55-0.95 are used as geometric feasibility constraints rather than output-based filters. The lower bound avoids implausible hotel layouts in which service/core/structural space dominates the building, while the upper bound preserves a minimum allowance for circulation, service shafts, plant rooms, and vertical cores. The screening is therefore applied before EnergyPlus outputs are available and cannot directly select for lower or higher EUI.

The notebook reports pre- and post-filter distributions, a two-dimensional coverage check, the Kolmogorov-Smirnov statistic, and the Jensen-Shannon distance for each input variable. These diagnostics quantify how much the retained sample differs from the initial LHS design while preserving a transparent record of the filtering decision.""",
    "EnergyPlus 模型可复现性文档": """### EnergyPlus model reproducibility documentation

**Response to the reviewer request for reproducible simulation details.** The baseline hotel prototype is represented as a simplified rectangular-prism model whose geometry is generated from the sampled `building_length`, `aspect_ratio`, `floor_num`, and related variables. The HVAC representation uses the EnergyPlus ideal-loads framework for cooling/heating-load extraction, while lighting, equipment, fan electricity, and domestic hot-water energy are calculated through explicit engineering equations in the post-processing stage.

The weather file is `input/Beijing.epw`, and the intended EnergyPlus executable is EnergyPlus 25.2.0. All parameter names in the code are kept consistent with the manuscript variables and downstream CSV outputs, so the four-notebook pipeline remains traceable from sampling to EUI, machine-learning, and OCEI analyses.""",
    "SRC 方法的线性假设局限与补充验证": """### Linear-assumption limitation of SRC and nonlinear supplementary validation

Standardised regression coefficients (SRCs) are interpretable first-order sensitivity indicators, but they rely on a linear approximation of the response surface. Because the simulated EUI response can contain nonlinear effects and interactions, this notebook supplements SRC with an XGBoost-SHAP analysis. The SRC-SHAP rank comparison, Spearman correlation, and top-18 overlap quantify whether the linear screening misses influential nonlinear variables.

The appropriate manuscript framing is therefore: SRC is used as a transparent first-stage screening tool, while SHAP provides a nonlinear robustness check rather than a replacement for a full variance-based global sensitivity analysis.""",
    "模型超参数与非核心变量处理说明": """### Model hyperparameters and non-core-variable handling

This notebook records the search strategy, selected hyperparameters, and model-evaluation metrics for all candidate regressors. Pipeline objects are used so that imputation and scaling are fitted within the training data or cross-validation folds rather than on the full dataset, reducing information-leakage risk.

The non-core-variable analysis compares the 18-variable feature set against the wider feature set to test whether fixing non-core variables artificially inflates model performance. This result should be reported as evidence for feature-set parsimony, not as proof of real-building predictive accuracy.""",
    "碳排放因子数据来源与说明": """### Emission-factor sources and accounting notes

**Response to the reviewer request for emission-factor provenance and sensitivity testing.** The OCEI calculation uses carrier-specific factors for electricity, natural gas, district heating, and district cooling. Electricity is treated as the most influential and policy-sensitive factor, so the notebook evaluates low-grid, high-grid, and decarbonisation scenarios in addition to the baseline case.

The sensitivity analysis distinguishes two claims: absolute OCEI values change with emission-factor assumptions, whereas the EUI-OCEI correlation and top-rank overlap are used to assess whether the coupling structure remains robust under plausible factor changes.""",
}


SMOKE_DATASET_CELL = r'''
energyplus_exe = Path(CONFIG["energyplus_exe"])
weather_path = Path(CONFIG["weather_epw"])
expandobjects_exe = Path(CONFIG["expandobjects_exe"])


def estimate_smoke_energyplus_outputs(row: pd.Series) -> Dict[str, float]:
    """Create deterministic load estimates for local smoke testing.

    This function is only used when CONFIG["run_energyplus"] is False. It is
    not a substitute for EnergyPlus results in the manuscript; it simply keeps
    the four-notebook pipeline executable on machines where a long simulation
    batch is not being launched.
    """
    area = float(row["gross_floor_area_m2"])
    wwr = float(row["wwr"])
    fresh_air_ach = float(row["fresh_air_ach"])
    u_wall = float(row["u_wall"])
    u_roof = float(row["u_roof"])
    u_win = np.mean([
        float(row["u_win_n"]),
        float(row["u_win_s"]),
        float(row["u_win_e"]),
        float(row["u_win_w"]),
    ])
    light_power = float(row["light_power"])
    equip_power = float(row["equip_power"])
    cool_set = float(row["cool_set"])
    heat_set = float(row["heat_set"])
    floor_num = float(row["floor_num"])
    aspect_ratio = float(row["aspect_ratio"])

    envelope_term = 2.6 * u_wall + 1.8 * u_roof + 0.9 * u_win * wwr
    internal_gain_term = 0.42 * light_power + 0.55 * equip_power
    ventilation_term = 6.5 * fresh_air_ach
    geometry_term = 0.35 * floor_num + 1.8 * abs(aspect_ratio - 1.8)

    cooling_intensity = (
        18.0
        + 52.0 * wwr
        + internal_gain_term
        + ventilation_term
        + 2.0 * max(0.0, 26.0 - cool_set)
        + 0.25 * geometry_term
    )
    heating_intensity = (
        10.0
        + 3.2 * envelope_term
        + 4.8 * fresh_air_ach
        + 2.4 * max(0.0, heat_set - 20.0)
        + 0.18 * geometry_term
    )

    return {
        "ideal_cooling_supply_kwh": max(0.0, cooling_intensity * area),
        "ideal_heating_supply_kwh": max(0.0, heating_intensity * area),
        "ideal_cooling_zone_kwh": max(0.0, cooling_intensity * area),
        "ideal_heating_zone_kwh": max(0.0, heating_intensity * area),
        "smoke_test_load_model": 1.0,
    }


simulation_logs = []
dataset_rows = []

if CONFIG["run_energyplus"]:
    assert energyplus_exe.exists(), f"EnergyPlus executable not found: {energyplus_exe}"
    assert weather_path.exists(), f"EPW weather file not found: {weather_path}"
    assert expandobjects_exe.exists(), f"ExpandObjects executable not found: {expandobjects_exe}"

    for i, (_, row) in enumerate(samples.iterrows(), start=1):
        idf_path = IDF_DIR / f"{row['sample_id']}.idf"

        log = run_single_simulation(
            idf_path=idf_path,
            weather_path=weather_path,
            energyplus_exe=energyplus_exe,
            run_root=RUN_DIR,
            timeout_seconds=CONFIG["timeout_seconds"],
            expandobjects_exe=expandobjects_exe,
        )
        simulation_logs.append(log)

        if log["success"]:
            sim = parse_sqlite_result(Path(log["run_dir"]))
            post = engineering_postprocess(row, sim)
            dataset_rows.append({**row.to_dict(), **sim, **post, "simulation_mode": "EnergyPlus"})

        print(f"[{i}/{len(samples)}] {row['sample_id']} success={log['success']}")
else:
    print("CONFIG['run_energyplus'] is False; generating a deterministic smoke-test dataset.")
    print("Use EUI_RUN_ENERGYPLUS=1 for the formal EnergyPlus simulation dataset.")
    for i, (_, row) in enumerate(samples.iterrows(), start=1):
        sim = estimate_smoke_energyplus_outputs(row)
        post = engineering_postprocess(row, sim)
        dataset_rows.append({**row.to_dict(), **sim, **post, "simulation_mode": "engineering_smoke_test"})
        simulation_logs.append({
            "sample_id": row["sample_id"],
            "success": True,
            "returncode": 0,
            "has_severe_error": False,
            "run_dir": "",
            "mode": "engineering_smoke_test",
        })

logs_df = pd.DataFrame(simulation_logs)
logs_df.to_csv(OUTPUT_DIR / "simulation_log.csv", index=False, encoding="utf-8-sig")

dataset = pd.DataFrame(dataset_rows)
dataset.to_csv(DATA_DIR / "step1_simulation_dataset.csv", index=False, encoding="utf-8-sig")

if not dataset.empty and {"sample_id", "site_energy_kwh", "eui_kwh_m2"}.issubset(dataset.columns):
    print(dataset[["sample_id", "simulation_mode", "site_energy_kwh", "eui_kwh_m2"]].head())
    print(f"Dataset written to: {DATA_DIR / 'step1_simulation_dataset.csv'}")
    print(f"Rows: {len(dataset):,}; columns: {len(dataset.columns):,}")
else:
    raise RuntimeError(
        "No dataset was generated. Check simulation_log.csv and, in EnergyPlus mode, the eplusout.err files."
    )
'''


def patch_code(nb, filename: str) -> None:
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        src = cell.source
        for old, new in CODE_REPLACEMENTS.items():
            src = src.replace(old, new)

        if filename.startswith("01_") and "plt.rcParams.update({" in src and "CONFIG = {" in src:
            if "from cycler import cycler" not in src:
                src = src.replace("import matplotlib.pyplot as plt\n", "import matplotlib.pyplot as plt\nfrom cycler import cycler\n")
            if '"axes.prop_cycle"' not in src:
                src = src.replace(
                    '"axes.grid": True,\n',
                    '"axes.grid": True,\n    "axes.prop_cycle": cycler(color=["#4C78A8", "#F58518", "#54A24B", "#E45756", "#72B7B2", "#B279A2"]),\n',
                )

        if filename.startswith("01_") and "energyplus_exe = Path(CONFIG" in src and "run_single_simulation(" in src:
            src = SMOKE_DATASET_CELL.strip()

        cell.source = src


def patch_formal_markdown(nb) -> None:
    for cell in nb.cells:
        if cell.cell_type != "markdown":
            continue
        if ZH_START in cell.source or EN_START in cell.source:
            continue
        for key, replacement in FORMAL_MARKDOWN.items():
            if key in cell.source:
                cell.source = replacement
                break


def audit_no_chinese_in_code(nb, filename: str) -> list[str]:
    chinese = re.compile(r"[\u4e00-\u9fff]")
    issues = []
    for idx, cell in enumerate(nb.cells):
        if cell.cell_type == "code" and chinese.search(cell.source):
            lines = []
            for line_no, line in enumerate(cell.source.splitlines(), start=1):
                if chinese.search(line):
                    lines.append(f"{line_no}: {line[:140]}")
            issues.append(f"{filename} code cell {idx}: " + " | ".join(lines[:6]))
    return issues


def main() -> None:
    all_issues = []
    for name in NOTEBOOKS:
        path = TARGET / name
        nb = nbformat.read(path, as_version=4)
        split_explanation_cells(nb)
        patch_formal_markdown(nb)
        patch_code(nb, name)
        all_issues.extend(audit_no_chinese_in_code(nb, name))
        nbformat.write(nb, path)
        code_count = sum(c.cell_type == "code" for c in nb.cells)
        zh_count = sum(c.cell_type == "markdown" and ZH_START in c.source for c in nb.cells)
        en_count = sum(c.cell_type == "markdown" and EN_START in c.source for c in nb.cells)
        print(f"{name}: code={code_count}, zh_explanations={zh_count}, en_explanations={en_count}")
    if all_issues:
        print("\nChinese text remains in code cells:")
        for issue in all_issues:
            print(issue)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
