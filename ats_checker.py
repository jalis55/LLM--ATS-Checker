# app.py
import os, streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from pydantic import BaseModel, Field

load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY is not set")

# ---------- Pydantic model ----------
class AtsScore(BaseModel):
    score: int = Field(0, description="CV Score")
    matched_requirements: list = Field(default_factory=list, description="Matched Requirements")
    unmatched_requirements: list = Field(default_factory=list, description="Unmatched Requirements")
    recommendation: str = Field("", description="Recommendation to increase CV score")

# ---------- Agent ----------
model = "groq:qwen/qwen3-32b"
agent = create_agent(model=model, response_format=AtsScore)

def check_ats(jd: str, cv: str) -> AtsScore:
    messages = [
        {"role": "system", "content": "You are an ATS assistant. Compare the CV against the job description."},
        {"role": "user", "content": f"CV:\n{cv}\n\nJob Description:\n{jd}"}
    ]
    return agent.invoke({"messages": messages})["structured_response"]

# ---------- Streamlit UI ----------
st.set_page_config(page_title="ATS Checker", layout="wide")
st.markdown("""
<style>
    .stButton>button{
        background-color:#00c896;
        color:white;
        border-radius:8px;
        border:none;
        padding:0.5rem 2rem;
        font-size:1.1rem;
    }
    .score-card{
        background:#1e1e1e;
        padding:1.5rem;
        border-radius:12px;
        margin-bottom:1rem;
    }
    .matched   {color:#00c896;}
    .unmatched {color:#ff6b6b;}
</style>
""", unsafe_allow_html=True)

st.title("🔍 ATS Checker")
st.markdown("Compare your CV against any job description and get instant feedback.")

c1, c2 = st.columns(2)
with c1:
    jd = st.text_area("📄 Job Description", height=300, placeholder="Paste the full job description here…")
with c2:
    cv = st.text_area("📑 CV / Résumé",   height=300, placeholder="Paste your CV text here…")

if st.button("Analyze"):
    if not jd.strip() or not cv.strip():
        st.error("Both fields are required.")
        st.stop()

    with st.spinner("Analyzing…"):
        result: AtsScore = check_ats(jd, cv)

    # ---- Score card ----
    st.markdown("---")
    st.subheader("Result")
    col_score, col_bar = st.columns([1, 3])
    with col_score:
        st.markdown(
            f'<div class="score-card"><h2 style="margin:0;">{result.score}<span style="font-size:1rem;">/100</span></h2>'
            f'<small>Overall Match</small></div>', unsafe_allow_html=True
        )
    with col_bar:
        st.progress(result.score / 100)

    # ---- Requirements ----
    col_m, col_u = st.columns(2)
    with col_m:
        st.markdown("✅ **Matched Requirements**")
        for item in result.matched_requirements:
            st.markdown(f'<span class="matched">• {item}</span>', unsafe_allow_html=True)
    with col_u:
        st.markdown("❌ **Missing Requirements**")
        for item in result.unmatched_requirements:
            st.markdown(f'<span class="unmatched">• {item}</span>', unsafe_allow_html=True)

    # ---- Recommendation ----
    if result.recommendation:
        st.info("💡 **Recommendation**")
        st.write(result.recommendation)