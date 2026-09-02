from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, ListFlowable, ListItem
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "TrajectoryLock_Whitepaper_v0.1.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

NAVY = colors.HexColor("#08141C")
PANEL = colors.HexColor("#10232D")
TEAL = colors.HexColor("#18A889")
LIGHT_TEAL = colors.HexColor("#DDF5EF")
INK = colors.HexColor("#15232D")
MUTED = colors.HexColor("#536876")
LINE = colors.HexColor("#B8C8D1")
AMBER = colors.HexColor("#C67A00")
PALE = colors.HexColor("#F3F7F8")


def page(canvas, doc):
    canvas.saveState()
    if doc.page == 1:
        canvas.setFillColor(NAVY)
        canvas.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
    else:
        canvas.setFillColor(NAVY)
        canvas.rect(0, letter[1] - 38, letter[0], 38, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(54, letter[1] - 24, "TRAJECTORYLOCK / TECHNICAL WHITEPAPER")
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(letter[0] - 54, 28, f"v0.1 / Page {doc.page}")
        canvas.setStrokeColor(LINE)
        canvas.line(54, 38, letter[0] - 54, 38)
    canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverKicker", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=TEAL, spaceAfter=18, tracking=1.5))
styles.add(ParagraphStyle(name="CoverTitle", fontName="Helvetica-Bold", fontSize=34, leading=38, textColor=colors.white, spaceAfter=14))
styles.add(ParagraphStyle(name="CoverSub", fontName="Helvetica", fontSize=15, leading=22, textColor=colors.HexColor("#BBD1DB"), spaceAfter=28))
styles.add(ParagraphStyle(name="H1x", fontName="Helvetica-Bold", fontSize=22, leading=27, textColor=NAVY, spaceBefore=6, spaceAfter=14))
styles.add(ParagraphStyle(name="H2x", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=TEAL, spaceBefore=12, spaceAfter=7))
styles.add(ParagraphStyle(name="Bodyx", fontName="Helvetica", fontSize=9.4, leading=14.2, textColor=INK, spaceAfter=8))
styles.add(ParagraphStyle(name="Smallx", fontName="Helvetica", fontSize=7.7, leading=11, textColor=MUTED))
styles.add(ParagraphStyle(name="Callout", fontName="Helvetica-Bold", fontSize=10, leading=15, textColor=NAVY, leftIndent=10, rightIndent=10, spaceBefore=8, spaceAfter=8))
styles.add(ParagraphStyle(name="Eq", fontName="Courier", fontSize=8.5, leading=13, textColor=INK, backColor=PALE, borderPadding=9, spaceBefore=6, spaceAfter=10))
styles.add(ParagraphStyle(name="TableHead", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=colors.white))
styles.add(ParagraphStyle(name="TableBody", fontName="Helvetica", fontSize=7.5, leading=10, textColor=INK))


def p(text, style="Bodyx"):
    return Paragraph(text, styles[style])


def bullets(items):
    return ListFlowable([ListItem(p(item), leftIndent=10) for item in items], bulletType="bullet", start="circle", leftIndent=18, bulletFontName="Helvetica", bulletFontSize=6, spaceAfter=8)


def table(headers, rows, widths):
    data = [[p(h, "TableHead") for h in headers]] + [[p(str(c), "TableBody") for c in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PANEL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("BACKGROUND", (0, 2), (-1, -1), PALE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


story = []
story += [Spacer(1, 1.3*inch), p("AUDITABLE FORENSIC GEOMETRY", "CoverKicker"), p("TrajectoryLock", "CoverTitle"), p("A multi-source system for reconstructing projectile trajectories and testing their geometric compatibility with official accounts", "CoverSub")]
cover_box = Table([[p("WHITEPAPER + WORKING REFERENCE IMPLEMENTATION", "TableHead")], [p("Concept architecture, uncertainty model, chain-of-custody design, source-independence controls, API contract, validation plan, and deployable Python MVP.", "Bodyx")]], colWidths=[6.2*inch])
cover_box.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), TEAL), ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#E8F4F3")), ("BOX", (0,0), (-1,-1), 0.8, TEAL), ("LEFTPADDING", (0,0), (-1,-1), 14), ("RIGHTPADDING", (0,0), (-1,-1), 14), ("TOPPADDING", (0,0), (-1,-1), 12), ("BOTTOMPADDING", (0,0), (-1,-1), 12)]))
story += [cover_box, Spacer(1, .65*inch), p("Version 0.1 / September 2026", "CoverSub"), Spacer(1, .45*inch), p("Research prototype. Not a certified forensic instrument and not a substitute for qualified scene reconstruction, medical findings, or laboratory examination.", "Smallx"), PageBreak()]

story += [p("1. Executive summary", "H1x"), p("TrajectoryLock is designed to answer one bounded question: <b>given the available geometry and its uncertainty, how compatible is a reconstructed trajectory with a declared official trajectory?</b> It accepts multiple videos, photographs, surveyed points, direct trajectory measurements, witness bearings, and an official narrative expressed as a testable 3D line with tolerances."), p("The system does not assign a single magical confidence number. It separates three quantities that are routinely conflated:"), bullets([
    "<b>Compatibility score:</b> continuous geometric closeness between reconstructed and declared lines.",
    "<b>Threshold match probability:</b> Monte Carlo probability that angle and offset fall within declared tolerances.",
    "<b>Reconstruction confidence:</b> strength, calibration, and independence of the evidence supporting the estimated line."
]), p("A high match probability with low reconstruction confidence is weak evidence. A high-confidence reconstruction with a low match probability is evidence of geometric inconsistency. Intermediate values remain indeterminate."), p("Core design principle", "H2x"), p("More files improve precision only when they contribute independent constraints. Re-encodes, reposts, shared camera origins, copied witness accounts, and derivative edits are grouped and down-weighted. This prevents a hundred copies of one clip from masquerading as a hundred independent viewpoints."), PageBreak()]

story += [p("2. Problem definition and scope", "H1x"), p("Public incident review is often trapped between two weak extremes: qualitative visual argument and opaque model output. TrajectoryLock creates a reproducible middle layer. Every conclusion is conditional on declared coordinate systems, calibrations, annotations, source relationships, and uncertainty assumptions."), table(["In scope", "Out of scope"], [
    ["Bullets, arrows, fragments, thrown objects, or other approximately linear flight/impact segments", "Identifying a shooter, intent, guilt, institutional honesty, or a complete event narrative"],
    ["3D line reconstruction from calibrated rays, scene survey points, and direct measurements", "Unvalidated automatic detection of invisible or motion-blurred projectiles"],
    ["Geometric agreement testing with transparent uncertainty and tolerances", "Replacing firearm/toolmark, autopsy, wound-path, acoustic, or materials experts"],
    ["Witness direction as labeled corroboration", "Treating memory as equal to surveyed physical evidence"]
], [3.15*inch, 3.15*inch]), p("Threat model", "H2x"), bullets([
    "Accidental coordinate-frame mismatch, unit mismatch, or camera-calibration error.",
    "Duplicate/correlated sources that falsely inflate certainty.",
    "Selection bias: only favorable frames, witnesses, or official parameters are entered.",
    "Edited media, missing provenance, synthetic content, and timestamp drift.",
    "Analyst tuning of tolerances after seeing the result."
]), p("The production design counters these risks with schema validation, file hashing, immutable revision history, blinded annotations, frozen tolerance declarations, independence groups, sensitivity analysis, and signed result manifests."), PageBreak()]

story += [p("3. Evidence and coordinate model", "H1x"), p("All physical geometry is represented in a right-handed Cartesian world coordinate system measured in metres. Camera calibration converts a marked pixel into a world-space sight ray. Multiple separated sight rays that refer to the same physical feature are intersected by weighted least squares."), table(["Evidence type", "Required fields", "Role"], [
    ["Visual ray", "feature ID, camera origin, direction, angular sigma, range hint", "Triangulates a physical point from calibrated video/photo annotations"],
    ["Survey point", "feature ID, XYZ point, positional sigma", "Directly constrains entry, exit, strike, or projectile position"],
    ["Direct line", "XYZ point, direction, angular sigma, offset sigma", "Represents a validated photogrammetric or scene-reconstruction line"],
    ["Witness bearing", "origin, direction, angular sigma, reliability", "Corroboration only; does not silently control physical reconstruction"],
    ["Official hypothesis", "point, direction, uncertainty, frozen angle/offset tolerances", "The testable claim being compared"]
], [1.15*inch, 2.8*inch, 2.35*inch]), p("A visual file is not itself a trajectory measurement. It becomes one only after calibration, feature identification, frame selection, annotation, and uncertainty assignment. Each transformation should retain its operator, algorithm version, timestamp, and parent artifact hash."), p("Feature examples", "H2x"), p("Entry and exit points are common, but the schema also supports named positions such as <font name='Courier'>projectile_t0</font>, <font name='Courier'>projectile_t1</font>, ricochet points, embedded fragments, arrow shaft endpoints, or line-of-damage marks. At least two reconstructed points or one qualified direct line are required."), PageBreak()]

story += [p("4. Reconstruction mathematics", "H1x"), p("For sight ray <i>i</i> with origin <b>o_i</b>, unit direction <b>d_i</b>, and weight <b>w_i</b>, the matrix <b>P_i = I - d_i d_i^T</b> projects displacement into the plane perpendicular to the ray. The weighted least-squares point is:"), p("A = sum_i w_i P_i     b = sum_i w_i P_i o_i     x_hat = A^-1 b", "Eq"), p("Angular uncertainty is converted to a transverse uncertainty using a declared range hint. Surveyed points add isotropic constraints. The solver rejects ill-conditioned geometry, including parallel views that cannot determine depth."), p("Line fit", "H2x"), p("With at least two reconstructed features, weighted principal-component analysis estimates the dominant line direction. Feature uncertainty supplies weights. Direct-line estimates are sign-aligned and blended by inverse angular variance. Because a geometric line has no intrinsic polarity, comparison uses the acute angle between directions."), p("Line-to-line offset", "H2x"), p("For lines (p1, d1) and (p2, d2), the shortest skew-line distance is the absolute projection of (p2 - p1) onto the normalized cross product of d1 and d2. A stable perpendicular-distance form is used when lines are nearly parallel."), p("Uncertainty propagation", "H2x"), p("Monte Carlo trials perturb reconstructed and official directions by their angular standard deviations and line origins by positional standard deviations. Every trial records angular difference and line offset. The output includes 95% empirical intervals and the proportion satisfying both frozen thresholds."), p("P(match | declared model) = count(angle <= T_angle AND offset <= T_offset) / N", "Eq"), p("This is conditional model agreement, not the probability that the official account is true."), PageBreak()]

story += [p("5. Confidence and source independence", "H1x"), p("TrajectoryLock prevents file count from becoming confidence by using independence groups. Each group contributes its strongest source fully; additional correlated items in the same group add only a small capped increment."), p("effective_group = best_quality + 0.2 * (1 - exp(-sum(copy_qualities)))", "Eq"), p("The prototype reconstruction-confidence score combines effective source strength (55%), number of reconstructed features (30%), and calibration completeness (15%). It is bounded below 100% to avoid representing model confidence as certainty."), table(["Situation", "Expected effect"], [
    ["Second calibrated camera at a separated position", "Material gain: adds depth geometry and an independent constraint"],
    ["A repost or re-encode of camera A", "Minimal gain: same independence group"],
    ["Independent scene survey of entry and exit points", "Large gain: different measurement modality"],
    ["Multiple witnesses who discussed the event together", "Grouped or correlation-adjusted; not independent by default"],
    ["Many frames from one fixed camera", "Can reduce annotation noise, but does not create new viewpoint geometry"]
], [2.6*inch, 3.7*inch]), p("Calibration is scoreable only when the calibration artifact is preserved and linked. A boolean flag is sufficient for the MVP; production should evaluate reprojection error, control-point coverage, lens model, rolling-shutter behavior, and temporal synchronization."), PageBreak()]

story += [p("6. System architecture", "H1x"), p("The reference implementation is intentionally dependency-light. A NumPy computational core is wrapped by a command-line interface and a local HTTP workbench. The repository includes a browser UI, example case, hashing utilities, Dockerfile, and unit tests."), table(["Layer", "Responsibility", "Reference module"], [
    ["Integrity", "SHA-256 media hashes and canonical JSON fingerprints", "integrity.py"],
    ["Geometry", "Vector validation, ray triangulation, PCA line fitting, offsets", "geometry.py"],
    ["Scoring", "Monte Carlo comparison, independence score, witness agreement", "scoring.py"],
    ["Pipeline", "Schema checks, feature assembly, result manifest", "pipeline.py"],
    ["Interfaces", "CLI, JSON HTTP API, local browser workbench", "cli.py / server.py"],
    ["Verification", "Synthetic consistent/inconsistent cases and edge tests", "tests/"],
], [1.0*inch, 3.25*inch, 2.05*inch]), p("Data flow", "H2x"), p("Original media -> immutable hash -> calibration -> frame/feature annotation -> world-space observation -> feature triangulation -> 3D trajectory -> Monte Carlo comparison -> signed result manifest", "Eq"), p("Production components", "H2x"), bullets([
    "Encrypted object storage for originals and derivatives; write-once audit event store.",
    "PostgreSQL case/evidence database with row-level authorization and revision history.",
    "Worker queue for frame extraction, calibration, photogrammetry, and simulation.",
    "Role separation for evidence custodian, annotator, reviewer, and report signer.",
    "Reproducible containers pinned by digest; deterministic seeds and dependency lockfiles."
]), PageBreak()]

story += [p("7. API and case contract", "H1x"), p("The MVP exposes a small JSON API. <font name='Courier'>POST /api/analyze</font> accepts the same object used by the CLI and returns a complete result manifest. <font name='Courier'>GET /api/example</font> supplies a synthetic case. <font name='Courier'>POST /api/hash</font> hashes local paths when the server is explicitly run in a trusted local environment."), p("Minimal case skeleton", "H2x"), p('{<br/>  "case_id": "CASE-001",<br/>  "sources": [{"id":"survey-a", "quality":0.95,<br/>    "calibrated":true, "independence_group":"survey-a"}],<br/>  "observations": [{"type":"direct_line", "source_id":"survey-a",<br/>    "point":[0,0,1.2], "direction":[1,0.1,0.02],<br/>    "angular_sigma_deg":0.5, "offset_sigma_m":0.02}],<br/>  "official_hypothesis": {"point":[0,0,1.2], "direction":[1,0.1,0.02],<br/>    "angular_sigma_deg":0.7, "offset_sigma_m":0.04,<br/>    "angle_tolerance_deg":3.0, "offset_tolerance_m":0.25}<br/>}', "Eq"), p("Result contract", "H2x"), bullets([
    "Input and result SHA-256 fingerprints for reproducibility.",
    "Reconstructed line point, unit direction, angular/offset uncertainty, and residual.",
    "Per-feature position, uncertainty, ray residual, condition number, and observation count.",
    "Compatibility, threshold probability, conclusion class, confidence, and witness corroboration.",
    "Warnings and a mandatory interpretive guardrail."
]), PageBreak()]

story += [p("8. Workflow and human controls", "H1x"), table(["Stage", "Required control", "Failure response"], [
    ["Acquire", "Preserve original bytes, metadata, custody event, and hash", "Quarantine unexplained modifications"],
    ["Synchronize", "Estimate clock offsets and rolling-shutter/timing uncertainty", "Widen uncertainty or exclude timing claim"],
    ["Calibrate", "Lens model and surveyed control points; retain reprojection residuals", "Reject or downgrade bad calibration"],
    ["Annotate", "Blind or dual annotation; label visibility and ambiguity", "Adjudicate; keep both originals"],
    ["Declare", "Freeze official line and tolerances before computing comparison", "Mark post-hoc changes as new hypothesis revision"],
    ["Analyze", "Pinned code, seed, source groups, and sensitivity runs", "Block result if validation fails"],
    ["Review", "Independent technical reviewer and signed interpretation", "Return for correction without erasing history"]
], [0.8*inch, 3.2*inch, 2.3*inch]), p("Witness handling", "H2x"), p("Witness accounts are encoded as distributions, not exact rays. Interview timing, opportunity to observe, contamination, confidence, and directional ambiguity should be retained. Witness agreement is reported separately from physical-line reconstruction so a crowd cannot numerically overrule calibrated geometry."), p("Official narrative handling", "H2x"), p("An official account must be decomposed into a falsifiable geometric hypothesis. Vague prose such as 'from the north' should not be converted into a precise line without documenting the conversion. If several official versions exist, they become separately versioned hypotheses and are never merged into a moving target."), PageBreak()]

story += [p("9. Validation plan", "H1x"), p("The included tests verify the mathematics and major score guardrails, but a forensic claim requires empirical validation on controlled physical scenes."), table(["Validation tier", "Dataset", "Pass criteria"], [
    ["Unit", "Synthetic exact and noisy geometry", "Known intersections, distances, angles, deterministic results"],
    ["Bench", "Instrumented indoor paths with surveyed ground truth", "Bias and 95% coverage within declared tolerances"],
    ["Field", "Multiple cameras, real lenses, lighting, occlusion, rolling shutter", "Error curves stratified by range, baseline, frame rate, and visibility"],
    ["Inter-analyst", "Blinded repeated annotations by independent operators", "Reported repeatability and adjudication rate"],
    ["Adversarial", "Edited, duplicated, synthetic, mislabeled, and coordinate-swapped inputs", "Correct quarantine or uncertainty inflation"],
    ["External", "Independent laboratory executes frozen protocol and code", "Reproducible estimates and calibrated confidence intervals"]
], [1.0*inch, 2.75*inch, 2.55*inch]), p("Required performance reporting", "H2x"), bullets([
    "Angular and lateral error distributions, not only mean error.",
    "Interval coverage: whether nominal 95% intervals contain ground truth about 95% of the time.",
    "False-consistency and false-inconsistency rates across pre-registered tolerances.",
    "Sensitivity to camera baseline, calibration residual, range, annotation error, and source correlation.",
    "Failure rate and explicit abstention rate; a trustworthy system must be able to return indeterminate."
]), PageBreak()]

story += [p("10. Security, ethics, and evidentiary limits", "H1x"), p("Trajectory analysis may involve deaths, injuries, criminal investigations, private locations, and identifiable people. Production use requires strict minimization, access control, retention limits, and legal authority. Public transparency is not a license to expose victims, witnesses, or raw location data."), p("Required safeguards", "H2x"), bullets([
    "Encryption in transit and at rest; case-scoped least privilege and multi-factor authentication.",
    "Immutable event log for ingest, access, export, annotation, model run, and hypothesis revision.",
    "Cryptographic hashes for every original and derivative; explicit parent-child provenance.",
    "No face recognition or identity inference in the core trajectory workflow.",
    "Human-readable export containing assumptions, exclusions, uncertainty, version, and reviewer sign-off.",
    "No automated legal conclusion, accusation, or credibility classification."
]), p("Admissibility", "H2x"), p("The software alone does not establish admissibility or scientific acceptance. A competent expert must be able to explain the method, its validation, error rate, calibration, chain of custody, and case-specific limitations. Jurisdiction-specific rules and disclosure duties must be evaluated independently."), p("Interpretation matrix", "H2x"), table(["Reconstruction confidence", "Match probability", "Permitted statement"], [
    ["High", "High", "Geometry is consistent within declared tolerances"],
    ["High", "Low", "Geometry is inconsistent within declared tolerances"],
    ["Low", "Any", "Evidence is insufficient for a strong geometric conclusion"],
    ["Any", "Middle band", "Indeterminate; acquire better constraints or retain ambiguity"]
], [1.75*inch, 1.5*inch, 3.05*inch]), PageBreak()]

story += [p("11. Development roadmap", "H1x"), table(["Phase", "Deliverable", "Exit criterion"], [
    ["0 - Reference MVP", "Auditable JSON core, web workbench, CLI, hashing, tests, Docker", "Delivered with this whitepaper"],
    ["1 - Evidence workstation", "Media ingest, frame extraction, calibration UI, point/ray annotation, project database", "End-to-end controlled case without manual JSON"],
    ["2 - Photogrammetry", "Bundle adjustment, surveyed scene model, camera pose solver, synchronization", "Validated against instrumented ground truth"],
    ["3 - Review and reporting", "Dual annotation, revision ledger, sensitivity dashboard, signed PDF/JSON report", "Independent reviewer can reproduce result"],
    ["4 - Forensic validation", "Pre-registered study, external replication, published error model", "Defined intended-use claims are empirically supported"],
    ["5 - Operational hardening", "RBAC, encrypted storage, deployment monitoring, retention/export controls", "Security and legal readiness review passed"]
], [1.15*inch, 3.0*inch, 2.15*inch]), p("Near-term engineering priorities", "H2x"), bullets([
    "Add OpenCV-based intrinsic/extrinsic calibration and lens-distortion models as an optional worker.",
    "Create an annotation UI with epipolar guides and blind duplicate labeling.",
    "Represent full covariance matrices rather than scalar angular/offset sigmas.",
    "Add robust estimators (RANSAC/M-estimators), outlier reports, and leave-one-source-out analysis.",
    "Add coordinate-frame transformations, unit registry, temporal alignment, and projectile physics only when supported by case data.",
    "Pre-register confidence calibration on controlled datasets before changing score semantics."
]), PageBreak()]

story += [p("12. Reproducibility and operation", "H1x"), p("The accompanying source bundle runs on Python 3.10+ with NumPy. It can be executed directly, installed as a package, or started in Docker."), p("Commands", "H2x"), p("python -m trajectorylock.cli demo -o result.json<br/>python -m trajectorylock.cli analyze examples/example_case.json -o result.json<br/>python -m trajectorylock.cli hash-media video.mp4 photo.jpg<br/>python -m trajectorylock.server --port 8080<br/>python -m unittest discover -s tests -v", "Eq"), p("Reproducibility checklist", "H2x"), bullets([
    "Preserve the exact case JSON and every media/calibration hash.",
    "Record code version, environment, random seed, and Monte Carlo sample count.",
    "Do not alter official tolerances after reviewing the output without creating a new hypothesis revision.",
    "Repeat with leave-one-source-out and plausible uncertainty ranges.",
    "Report warnings, excluded evidence, degenerate geometry, and indeterminate outcomes."
]), p("Conclusion", "H2x"), p("TrajectoryLock converts a potentially rhetorical dispute into an inspectable geometric test. Its value lies less in producing a percentage than in forcing every percentage to reveal what generated it: independent sources, calibrated geometry, declared uncertainty, frozen thresholds, code version, and reproducible calculations."), HRFlowable(width="100%", thickness=1, color=TEAL, spaceBefore=18, spaceAfter=12), p("Reference implementation: TrajectoryLock v0.1. Synthetic example results must never be represented as real-case findings.", "Smallx")]

doc = BaseDocTemplate(str(OUT), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=48, title="TrajectoryLock Whitepaper v0.1", author="TrajectoryLock")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
doc.addPageTemplates(PageTemplate(id="main", frames=frame, onPage=page))
doc.build(story)
print(OUT)

