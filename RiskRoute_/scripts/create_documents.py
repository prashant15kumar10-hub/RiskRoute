from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
METRICS = json.loads((ROOT / "artifacts" / "metrics.json").read_text())
CF = json.loads((ROOT / "artifacts" / "counterfactual_summary.json").read_text())

BLUE = RGBColor(39, 131, 222)
INK = RGBColor(44, 44, 43)
MUTED = RGBColor(100, 100, 100)


def setup(document: Document) -> None:
    section = document.sections[0]
    section.top_margin = Inches(0.72)
    section.bottom_margin = Inches(0.72)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)
    styles = document.styles
    styles["Normal"].font.name = "Arial"
    styles["Normal"].font.size = Pt(10.5)
    styles["Normal"].font.color.rgb = INK
    styles["Normal"].paragraph_format.space_after = Pt(6)
    styles["Normal"].paragraph_format.line_spacing = 1.15
    for name, size in [("Title", 24), ("Heading 1", 16), ("Heading 2", 13)]:
        styles[name].font.name = "Arial"
        styles[name].font.size = Pt(size)
        styles[name].font.color.rgb = INK


def add_title(document: Document, title: str, subtitle: str) -> None:
    p = document.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(72)
    r = p.add_run(title)
    r.bold = True
    r.font.size = Pt(24)
    r.font.color.rgb = INK
    p2 = document.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p2.add_run(subtitle)
    r.font.size = Pt(13)
    r.font.color.rgb = BLUE
    for text in [
        "Prashant Kumar",
        "Second-Year Student Project",
        "Institution / Department: ____________________",
        "Faculty Guide: ____________________",
        "Academic Year: 2026–27",
    ]:
        p = document.add_paragraph(text)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    note = document.add_paragraph()
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    note.paragraph_format.space_before = Pt(30)
    run = note.add_run(
        "Research draft based on a reproducible synthetic logistics benchmark. "
        "Replace placeholders and complete real-data validation before submission."
    )
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = MUTED
    document.add_page_break()


def add_table(document: Document, headers: list[str], rows: list[list[str]]) -> None:
    table = document.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Light Shading Accent 1"
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for run in cell.paragraphs[0].runs:
            run.bold = True
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = str(value)
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    document.add_paragraph()


def add_bullets(document: Document, items: list[str]) -> None:
    for item in items:
        document.add_paragraph(item, style="List Bullet")


def build_paper() -> None:
    doc = Document()
    setup(doc)
    add_title(
        doc,
        "RiskRoute",
        "A Constraint-Aware Explainable AI Framework for Counterfactual Decision Optimization in Intelligent Logistics",
    )

    doc.add_heading("Abstract", level=1)
    doc.add_paragraph(
        "Machine-learning systems for logistics commonly predict whether a shipment will be delayed, "
        "but a probability alone does not identify a feasible intervention. This paper presents "
        "RiskRoute, a two-stage prototype that combines gradient-boosted delay prediction with "
        "a constraint-aware counterfactual search. The system distinguishes operational variables "
        "that can be changed for a shipment—vehicle load, departure time and schedule buffer—from "
        "contextual variables that must remain fixed. A reproducible synthetic dataset of 6,000 "
        f"shipments was used for method development. The classifier achieved ROC-AUC {METRICS['roc_auc']:.3f} "
        f"and F1 {METRICS['f1']:.3f} on a held-out test set. On 150 high-risk cases, the proposed "
        f"search reached the target risk for {CF['validity_rate']:.0%} of cases, satisfied all defined "
        f"constraints for {CF['constraint_satisfaction_rate']:.0%} of returned interventions, and changed "
        f"{CF['mean_action_count']:.2f} features on average. A nearest-low-risk baseline reached the target "
        "more often but violated the actionability constraints in every tested case. These results show "
        "the practical trade-off between outcome validity and operational feasibility. The study is a "
        "methodology prototype; real operational validation is required before deployment."
    )
    p = doc.add_paragraph()
    p.add_run("Keywords—").bold = True
    p.add_run(
        " counterfactual explanation, explainable AI, intelligent logistics, delivery delay, "
        "algorithmic recourse, decision support."
    )

    doc.add_heading("1. Introduction", level=1)
    doc.add_paragraph(
        "Delivery-delay prediction supports planning, customer communication and resource allocation. "
        "However, most predictive systems answer only the question “what is likely to happen?” A planner "
        "also needs to know which available action could change the predicted outcome. Counterfactual "
        "explanations address this second question by describing a nearby input that receives a desired "
        "prediction. Wachter, Mittelstadt and Russell describe counterfactuals as minimal changes that "
        "can produce a desired result without requiring the complete internal logic of a black-box model [1]."
    )
    doc.add_paragraph(
        "A counterfactual is not useful merely because it flips a prediction. In logistics it may suggest "
        "changing the weather, road distance, or a driver’s experience—changes that are impossible for a "
        "current shipment. The research problem is therefore to balance validity with feasibility, "
        "minimality, sparsity and computational cost."
    )
    doc.add_heading("1.1 Research question", level=2)
    doc.add_paragraph(
        "Can a constraint-aware counterfactual search produce valid, sparse, feasible, and computationally "
        "practical interventions for delivery-delay predictions?"
    )
    doc.add_heading("1.2 Contributions", level=2)
    add_bullets(
        doc,
        [
            "A reproducible two-stage prediction and intervention pipeline.",
            "An explicit separation between mutable actions and immutable shipment context.",
            "A bounded search that ranks scenarios by normalized intervention cost.",
            "An evaluation using validity, constraint satisfaction, sparsity, risk reduction and runtime.",
            "A working interactive demonstration suitable for method extension with real logistics data.",
        ],
    )

    doc.add_heading("2. Related Work", level=1)
    doc.add_paragraph(
        "Wachter et al. [1] motivated counterfactual explanations as action-oriented alternatives to "
        "complete model disclosure. Mothilal, Sharma and Tan introduced DiCE, which emphasizes diversity "
        "and feasibility when presenting multiple counterfactuals [2]. Guidotti’s review and benchmark "
        "shows that counterfactual methods involve trade-offs among validity, minimality, actionability, "
        "plausibility, diversity, stability and runtime; no single method guarantees all properties [3]."
    )
    doc.add_paragraph(
        "Recent delivery-delay literature commonly applies tree-based or gradient-boosted models because "
        "they can represent non-linear operational interactions. Existing logistics work is largely "
        "prediction-centred. RiskRoute does not claim a new general counterfactual theory; its specific "
        "contribution is an experimentally testable, constraint-aware search for a logistics decision context."
    )

    doc.add_heading("3. Methodology", level=1)
    doc.add_heading("3.1 Dataset", level=2)
    doc.add_paragraph(
        "The development dataset contains 6,000 synthetic shipment records generated with a fixed random "
        "seed. The target is a binary delay indicator. Feature distributions and interactions were designed "
        "to imitate plausible operational behaviour, including higher delay risk under long distance, heavy "
        "load, traffic, poor weather and limited schedule buffer. Synthetic data makes the experiment fully "
        "reproducible but does not establish external validity."
    )
    add_table(
        doc,
        ["Feature", "Role", "Range / encoding"],
        [
            ["distance_km", "Immutable context", "20–800 km"],
            ["vehicle_load_pct", "Mutable", "25–100%"],
            ["departure_hour", "Mutable", "0–23"],
            ["traffic_level", "Immutable context", "0–3"],
            ["weather_severity", "Immutable context", "0–3"],
            ["driver_experience_years", "Immutable context", "0–18"],
            ["priority_shipment", "Immutable context", "0 / 1"],
            ["buffer_minutes", "Mutable", "0–120 minutes"],
        ],
    )

    doc.add_heading("3.2 Prediction model", level=2)
    doc.add_paragraph(
        "Data were divided into 75% training and 25% test sets using stratification. Numerical features were "
        "standardized and categorical/ordinal variables were one-hot encoded. A histogram gradient boosting "
        "classifier was trained with a fixed random seed. Accuracy, precision, recall, F1 and ROC-AUC were "
        "measured on the held-out test set."
    )
    doc.add_heading("3.3 Counterfactual search", level=2)
    doc.add_paragraph(
        "For a shipment x with predicted delay probability f(x), the algorithm enumerates a bounded set of "
        "operational candidates x′. Vehicle load may only decrease, departure may move earlier, and schedule "
        "buffer may only increase. All other features remain unchanged. Candidates satisfying f(x′) ≤ τ are "
        "valid, where τ is the selected target risk."
    )
    equation = doc.add_paragraph()
    equation.alignment = WD_ALIGN_PARAGRAPH.CENTER
    equation.add_run(
        "cost(x, x′) = |Δload|/25 + |Δdeparture|/4 + |Δbuffer|/60"
    ).italic = True
    doc.add_paragraph(
        "Valid candidates are sorted by cost, predicted probability and number of changed features. "
        "The interface returns up to five scenarios with varied action combinations."
    )

    doc.add_heading("3.4 Baseline and evaluation", level=2)
    doc.add_paragraph(
        "The baseline selects the nearest low-risk test case after normalizing all feature ranges. "
        "This can find a target-class example, but it does not respect mutable/immutable boundaries. "
        "Counterfactual evaluation was performed on 150 test cases with initial risk of at least 0.60."
    )
    add_table(
        doc,
        ["Metric", "Meaning"],
        [
            ["Validity", "Fraction of cases with at least one scenario at or below the target risk"],
            ["Constraint satisfaction", "Fraction of returned scenarios that preserve all immutable features"],
            ["Sparsity", "Mean number of changed operational features"],
            ["Proximity / cost", "Normalized magnitude of operational changes"],
            ["Risk reduction", "Initial probability minus counterfactual probability"],
            ["Runtime", "Mean search time per evaluated high-risk case"],
        ],
    )

    doc.add_heading("4. Results", level=1)
    doc.add_heading("4.1 Predictive performance", level=2)
    add_table(
        doc,
        ["Metric", "Value"],
        [
            ["Accuracy", f"{METRICS['accuracy']:.3f}"],
            ["Precision", f"{METRICS['precision']:.3f}"],
            ["Recall", f"{METRICS['recall']:.3f}"],
            ["F1", f"{METRICS['f1']:.3f}"],
            ["ROC-AUC", f"{METRICS['roc_auc']:.3f}"],
            ["Positive class rate", f"{METRICS['positive_rate']:.1%}"],
        ],
    )
    doc.add_heading("4.2 Counterfactual performance", level=2)
    baseline = CF["nearest_case_baseline"]
    add_table(
        doc,
        ["Measure", "Constraint-aware search", "Nearest low-risk baseline"],
        [
            ["Validity", f"{CF['validity_rate']:.1%}", f"{baseline['validity_rate']:.1%}"],
            [
                "Constraint satisfaction",
                f"{CF['constraint_satisfaction_rate']:.1%}",
                f"{baseline['constraint_satisfaction_rate']:.1%}",
            ],
            ["Mean changed features", f"{CF['mean_action_count']:.3f}", f"{baseline['mean_changed_features']:.3f}"],
            ["Mean normalized cost", f"{CF['mean_normalized_cost']:.3f}", "Not action-aware"],
            ["Mean risk reduction", f"{CF['mean_probability_reduction']:.1%}", "Not directly comparable"],
            ["Mean runtime", f"{CF['mean_runtime_ms']:.1f} ms", "Nearest-row lookup"],
        ],
    )
    doc.add_paragraph(
        "The baseline always identified a low-risk record, but it changed an average of more than five "
        "features and never preserved all immutable context. The proposed method accepted lower coverage "
        "in exchange for complete compliance with the defined action rules. Successful interventions "
        "changed fewer than two features on average."
    )

    doc.add_heading("5. Discussion", level=1)
    doc.add_paragraph(
        "The experiment demonstrates that validity alone is an incomplete measure of counterfactual quality. "
        "A baseline can achieve perfect target validity by borrowing a different shipment, yet the result is "
        "not an intervention for the current decision. Explicit constraints make the output more defensible "
        "and easier to explain, but they also reduce the number of cases for which the target is reachable."
    )
    doc.add_paragraph(
        "The 60% validity rate should not be interpreted as a universal system limit. It depends on the target "
        "threshold, action ranges and fixed-context assumption. In operational use, an unreachable target can "
        "be informative: it indicates that load, departure and buffer alone are insufficient under the current "
        "conditions."
    )

    doc.add_heading("6. Limitations and Threats to Validity", level=1)
    add_bullets(
        doc,
        [
            "The synthetic dataset reflects designed relationships and may not match real logistics operations.",
            "The model captures associations; the recommended changes are not guaranteed causal interventions.",
            "Traffic is held fixed when departure time changes, although these variables interact in reality.",
            "Grid search discretizes actions and can miss a lower-cost continuous solution.",
            "Normalized cost weights are methodological choices, not measured financial costs.",
            "No human-subject study was conducted to measure planner trust or usefulness.",
        ],
    )

    doc.add_heading("7. Conclusion and Future Work", level=1)
    doc.add_paragraph(
        "RiskRoute shows how a student-scale ML project can move from prediction toward decision support. "
        "The prototype combines a non-linear classifier with a transparent constrained search and evaluates "
        "both predictive quality and counterfactual feasibility. Future work should repeat the experiment on "
        "real shipment data, model the relationship between departure and traffic, compare against DiCE and "
        "optimization-based methods, learn monetary intervention costs, and conduct a user study with planners."
    )

    doc.add_heading("References", level=1)
    references = [
        "[1] S. Wachter, B. Mittelstadt, and C. Russell, “Counterfactual Explanations without Opening the Black Box: Automated Decisions and the GDPR,” Harvard Journal of Law & Technology, vol. 31, no. 2, 2018. doi:10.48550/arXiv.1711.00399.",
        "[2] R. K. Mothilal, A. Sharma, and C. Tan, “Explaining Machine Learning Classifiers through Diverse Counterfactual Explanations,” Proc. FAT* ’20, pp. 607–617, 2020. doi:10.1145/3351095.3372850.",
        "[3] R. Guidotti, “Counterfactual explanations and how to find them: literature review and benchmarking,” Data Mining and Knowledge Discovery, 2022. doi:10.1007/s10618-022-00831-6.",
        "[4] S. M. Lundberg and S.-I. Lee, “A Unified Approach to Interpreting Model Predictions,” Advances in Neural Information Processing Systems, 2017.",
    ]
    for ref in references:
        doc.add_paragraph(ref)

    doc.save(DOCS / "RiskRoute_Research_Paper_Draft.docx")


def build_report() -> None:
    doc = Document()
    setup(doc)
    doc.styles["Normal"].font.size = Pt(10)
    doc.styles["Normal"].paragraph_format.space_after = Pt(4)
    doc.sections[0].top_margin = Inches(0.62)
    doc.sections[0].bottom_margin = Inches(0.62)
    add_title(
        doc,
        "RiskRoute — Technical Project Report",
        "Prediction, Explainability and Constraint-Aware What-If Simulation",
    )
    doc.add_heading("Declaration", level=1)
    doc.add_paragraph(
        "This report documents a reproducible educational prototype. The student should review, test and "
        "adapt every section before academic submission, follow institutional disclosure rules, and replace "
        "all placeholders with verified details."
    )
    doc.add_heading("Executive Summary", level=1)
    doc.add_paragraph(
        "The project predicts logistics delivery delay and generates feasible what-if actions. It uses a "
        "gradient-boosted model and a transparent grid-based counterfactual engine. A React frontend "
        "communicates with a FastAPI REST API, while SQLite stores accounts and decision history. The interface "
        "allows a user to change shipment conditions, view risk, select a target and inspect recommended interventions."
    )
    doc.add_heading("System Modules", level=1)
    add_table(
        doc,
        ["Module", "File", "Responsibility"],
        [
            ["Data generation", "src/data.py", "Creates the reproducible shipment dataset"],
            ["Model training", "src/model.py + train.py", "Preprocesses data, trains model and exports metrics"],
            ["Counterfactual engine", "src/counterfactual.py", "Searches allowed changes and ranks scenarios"],
            ["Evaluation", "evaluate_counterfactuals.py", "Compares constrained search with a baseline"],
            ["React frontend", "frontend/", "Authentication, simulator, results and history"],
            ["FastAPI backend", "backend/", "REST API, request validation and application logic"],
            ["SQLite database", "artifacts/counterfact_x.db", "Users, sessions and saved predictions"],
            ["Test", "tests/test_counterfactual.py", "Checks target validity and constraint preservation"],
        ],
    )
    doc.add_heading("System Flow", level=1)
    steps = [
        "Collect or generate shipment features.",
        "Apply preprocessing and estimate delay probability.",
        "If risk is unacceptable, define a target probability.",
        "Enumerate allowed operational actions.",
        "Reject candidates that fail the target or constraints.",
        "Rank remaining scenarios by intervention cost.",
        "Display the most useful alternatives with before/after values.",
    ]
    for i, step in enumerate(steps, 1):
        doc.add_paragraph(f"{i}. {step}")
    doc.add_heading("Implementation Notes", level=1)
    doc.add_paragraph(
        "The code is intentionally divided into small modules so that each part can be explained independently. "
        "The model pipeline prevents preprocessing mismatch between training and prediction. Fixed random seeds "
        "allow repeatable results. All generated outputs are stored in the artifacts folder."
    )
    doc.add_heading("Measured Results", level=1)
    add_table(
        doc,
        ["Category", "Result"],
        [
            ["Dataset", f"{METRICS['rows']} rows; {METRICS['positive_rate']:.1%} delayed"],
            ["Prediction", f"ROC-AUC {METRICS['roc_auc']:.3f}; F1 {METRICS['f1']:.3f}"],
            ["Counterfactual validity", f"{CF['validity_rate']:.1%} on {CF['evaluated_high_risk_cases']} high-risk cases"],
            ["Constraint satisfaction", f"{CF['constraint_satisfaction_rate']:.1%}"],
            ["Average action count", f"{CF['mean_action_count']:.2f}"],
            ["Average probability reduction", f"{CF['mean_probability_reduction']:.1%}"],
            ["Average runtime", f"{CF['mean_runtime_ms']:.1f} ms per case"],
        ],
    )
    doc.add_heading("Installation and Demonstration", level=1)
    for line in [
        "1. Install Python 3.10 or newer and Node.js LTS.",
        "2. Open a terminal in the project folder.",
        "3. On Windows run: START_PROJECT.bat",
        "4. On macOS/Linux run: ./START_PROJECT.sh",
        "5. The launcher installs dependencies and builds React.",
        "6. FastAPI starts the backend and serves the frontend.",
        "7. Open: http://localhost:8000", 
    ]:
        doc.add_paragraph(line)
    doc.add_heading("Testing Checklist", level=1)
    add_bullets(
        doc,
        [
            "The model file exists after training.",
            "The metrics JSON matches terminal output.",
            "A high-risk example returns at least one intervention when reachable.",
            "Immutable features are identical before and after intervention.",
            "Every returned probability is at or below the selected target.",
            "The interface shows an honest warning when no solution is found.",
        ],
    )
    doc.add_heading("Submission Checklist", level=1)
    add_bullets(
        doc,
        [
            "Replace institution and guide placeholders.",
            "Read and understand every module.",
            "Run the project on the presentation laptop.",
            "Keep the synthetic-data limitation in the report.",
            "Add a real dataset experiment if required for publication.",
            "Follow your college’s policy for disclosing tools and assistance.",
        ],
    )
    doc.save(DOCS / "RiskRoute_Technical_Report.docx")


if __name__ == "__main__":
    DOCS.mkdir(exist_ok=True)
    build_paper()
    build_report()
    print("Documents created.")
