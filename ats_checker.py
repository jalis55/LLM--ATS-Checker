
from hashlib import sha256
from io import BytesIO
from time import perf_counter
import os

import streamlit as st

from services.ats_pipeline_service import create_ats_pipeline
from services.scoring_service import calculate_skill_score

from utils.report_generator import generate_ats_report
from utils.pdf_extractor import extract_text_from_pdf


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="SkillMatch AI | Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -1.5px;
        margin-bottom: 0.3rem;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }

    .score-card {
        background: linear-gradient(
            135deg, #172554, #1e3a8a
        );
        border: 1px solid #3b82f6;
        border-radius: 18px;
        padding: 28px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }

    .score-number {
        font-size: 3.5rem;
        font-weight: 800;
        line-height: 1.2;
    }

    .score-label {
        font-size: 1rem;
        color: #bfdbfe;
        margin-top: 6px;
    }

    .skill-badge {
        display: inline-block;
        padding: 7px 13px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 4px;
    }

    .matched-badge {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #86efac;
    }

    .unmatched-badge {
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #fca5a5;
    }

    .skill-container {
        padding: 20px;
        border: 1px solid #334155;
        border-radius: 14px;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    div.stButton > button[kind="primary"] {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.7rem 1rem;
    }

    div[data-testid="stMetric"] {
        padding: 18px;
        border: 1px solid #334155;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# SESSION STATE
# ==========================================

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "analysis_score" not in st.session_state:
    st.session_state.analysis_score = None


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.title("🎯 SkillMatch AI")

    st.caption("AI-Powered Resume Analysis")

    st.divider()

    st.subheader("⚙️ AI Configuration")

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.1,
        help="Lower values generally produce more consistent responses."
    )

    max_retries = st.number_input(
        "Maximum Retries",
        min_value=0,
        max_value=10,
        value=3,
        step=1
    )

    timeout = st.number_input(
        "Request Timeout (seconds)",
        min_value=10,
        max_value=120,
        value=60,
        step=10
    )

    st.divider()

    st.subheader("ℹ️ About")

    st.caption(
        "SkillMatch AI extracts skills from your resume "
        "and job description, compares them, and "
        "calculates a skill-based compatibility score."
    )

    st.info(
        "The score measures skill coverage, "
        "not overall hiring eligibility."
    )


# ==========================================
# HEADER
# ==========================================

st.markdown(
    '<div class="main-title">AI Resume Skill Matcher</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Discover how well your skills match a job description.'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# INPUT SECTION
# ==========================================

st.markdown(
    '<div class="section-title">📄 Resume Analysis</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2, gap="large")

def render_document_input(title: str, input_key: str, placeholder: str) -> str:
    st.markdown(f"#### {title}")
    method = st.radio(
        f"{title} input method",
        ["Paste Text", "Upload PDF"],
        horizontal=True,
        key=f"{input_key}_method",
    )
    text = ""
    if method == "Paste Text":
        text = st.text_area(
            f"{title} Content",
            placeholder=placeholder,
            height=280,
            key=f"{input_key}_text",
            label_visibility="collapsed",
        )
    else:
        uploaded_file = st.file_uploader(
            f"Upload {title.lower()} PDF",
            type=["pdf"],
            key=f"{input_key}_upload",
            help="Choose a PDF with selectable text. Scanned PDFs require OCR first.",
        )
        if uploaded_file is not None:
            try:
                data = uploaded_file.getvalue()
                digest = sha256(data).hexdigest()
                cached_pdf = st.session_state.get(f"{input_key}_pdf_cache")
                if cached_pdf is None or cached_pdf[0] != digest:
                    text = extract_text_from_pdf(BytesIO(data))
                    st.session_state[f"{input_key}_pdf_cache"] = (digest, text)
                else:
                    text = cached_pdf[1]
            except ValueError as error:
                st.error(str(error))
            else:
                st.success("PDF text extracted successfully.")
                with st.expander("Preview extracted text"):
                    st.text(text)
    st.caption(f"{len(text):,} characters")
    return text


with col1:
    cv = render_document_input(
        "Your Resume", "cv", "Paste your resume here..."
    )

with col2:
    jd = render_document_input(
        "Job Description", "jd", "Paste the job description here..."
    )


# ==========================================
# ANALYSIS BUTTON
# ==========================================

analyze_clicked = st.button(
    "🚀 Analyze Resume",
    type="primary",
    use_container_width=True
)

if analyze_clicked:

    if not cv.strip() or not jd.strip():
        st.warning(
            "Please provide both your resume and job description."
        )

    else:
        # Clear previous results before starting a new analysis
        st.session_state.analysis_result = None
        st.session_state.analysis_score = None

        try:
            with st.spinner(
                "Extracting and matching skills..."
            ):

                started = perf_counter()
                # PDF layout whitespace adds tokens without adding skill information.
                documents = {"cv": " ".join(cv.split()), "jd": " ".join(jd.split())}
                analysis_key = (
                    sha256(documents["cv"].encode()).hexdigest(),
                    sha256(documents["jd"].encode()).hexdigest(),
                    temperature, int(max_retries), float(timeout),
                    os.getenv("AI_MODEL", "openai/gpt-oss-120b"),
                )
                cached_analysis = st.session_state.get("cached_analysis")
                reused = cached_analysis is not None and cached_analysis[0] == analysis_key
                if reused:
                    result = cached_analysis[1]
                else:
                    pipeline = create_ats_pipeline(
                        temperature=temperature,
                        max_retries=int(max_retries),
                        timeout=float(timeout)
                    )
                    result = pipeline.invoke(documents)
                    st.session_state.cached_analysis = (analysis_key, result)
                st.session_state.analysis_duration = perf_counter() - started
                st.session_state.analysis_reused = reused

                score = calculate_skill_score(result)

                st.session_state.analysis_result = result
                st.session_state.analysis_score = score

        except Exception as e:
            st.error(f"Analysis failed: {e}")


# ==========================================
# RESULTS DASHBOARD
# ==========================================

result = st.session_state.analysis_result
score = st.session_state.analysis_score

if result is not None and score is not None:

    if st.session_state.get("analysis_reused"):
        st.caption("Reused the completed analysis for these documents and settings.")
    elif "analysis_duration" in st.session_state:
        st.caption(f"AI analysis completed in {st.session_state.analysis_duration:.1f} seconds.")

    st.divider()

    st.success("Resume analysis completed successfully!")

    st.markdown(
        '<div class="section-title">📊 Analysis Dashboard</div>',
        unsafe_allow_html=True
    )

    matched_count = len(result.matched)
    unmatched_count = len(result.unmatched)

    total_skills = matched_count + unmatched_count

    # --------------------------------------
    # SCORE CARD
    # --------------------------------------

    st.markdown(
        f"""
        <div class="score-card">
            <div class="score-number">{score:.1f}%</div>
            <div class="score-label">Skill Match Score</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.progress(
        min(max(float(score) / 100, 0.0), 1.0)
    )

    st.caption(
        "Score = Matched JD Skills / Total JD Skills × 100"
    )

    st.write("")

    # --------------------------------------
    # METRICS
    # --------------------------------------

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.metric(
            label="✅ Matched Skills",
            value=matched_count
        )

    with metric_col2:
        st.metric(
            label="❌ Unmatched Skills",
            value=unmatched_count
        )

    with metric_col3:
        st.metric(
            label="📋 Total Required Skills",
            value=total_skills
        )

    st.write("")

    # --------------------------------------
    # SKILL DETAILS
    # --------------------------------------

    st.markdown(
        '<div class="section-title">🔍 Skill Breakdown</div>',
        unsafe_allow_html=True
    )

    # Matched Skills
    st.markdown(f"#### ✅ Matched Skills ({matched_count})")

    if result.matched:
        st.pills(
            "Matched Skills",
            options=result.matched,
            selection_mode="multi",
            label_visibility="collapsed",
            key="matched_skill_pills"
        )
    else:
        st.info("No matching skills were identified.")

    st.write("")

    # Unmatched Skills
    st.markdown(f"#### ❌ Missing Skills ({unmatched_count})")

    if result.unmatched:
        st.pills(
            "Missing Skills",
            options=result.unmatched,
            selection_mode="multi",
            label_visibility="collapsed",
            key="missing_skill_pills"
        )
    else:
        st.success("No missing skills were identified.")

    st.divider()

    # --------------------------------------
    # SUMMARY
    # --------------------------------------

    st.markdown("### 📝 Analysis Summary")

    if total_skills == 0:
        st.info(
            "No job skills were identified. "
            "The score is not meaningful for this analysis."
        )

    elif score >= 80:
        st.success(
            "Strong skill alignment with the job description."
        )

    elif score >= 60:
        st.info(
            "Moderate skill alignment. "
            "Some required skills are missing."
        )

    else:
        st.warning(
            "Low skill alignment. "
            "Several job requirements are not reflected in your resume."
        )

    # --------------------------------------
    # TEXT SUMMARY
    # --------------------------------------

    with st.expander("View Detailed Skill Lists"):

        st.markdown("**Matched Skills**")

        st.write(
            ", ".join(result.matched)
            if result.matched
            else "None"
        )

        st.markdown("**Missing Skills**")

        st.write(
            ", ".join(result.unmatched)
            if result.unmatched
            else "None"
        )

    # --------------------------------------
    # DOWNLOAD RESULTS
    # --------------------------------------

    report = f"""
SKILLMATCH AI - RESUME ANALYSIS
================================

Skill Match Score: {score:.1f}%

Matched Skills: {matched_count}
Missing Skills: {unmatched_count}
Total Required Skills: {total_skills}

MATCHED SKILLS
--------------
{", ".join(result.matched) if result.matched else "None"}

MISSING SKILLS
--------------
{", ".join(result.unmatched) if result.unmatched else "None"}

Note: This is a skill-based match score,
not a comprehensive ATS evaluation.
"""

if result is not None and score is not None:
    # ... existing dashboard code (lines 305-485) ...

    # --------------------------------------
    # DOWNLOAD RESULTS (text)
    # --------------------------------------
    report = f"""
    ...
    """

    # ==========================================
    # PDF REPORT DOWNLOAD (moved inside block)
    # ==========================================
    st.subheader("📄 Download Report")
    pdf_report = generate_ats_report(result=result, score=score)
    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_report,
        file_name="skillmatch_ats_report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
