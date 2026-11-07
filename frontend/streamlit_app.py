import sys
from pathlib import Path

# Make the project root accessible to Python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from fastapi import HTTPException
from pypdf.errors import PdfReadError

from app.core.config import settings
from app.ingestion.pdf_parser import PDFParser
from app.services.analysis_service import AnalysisService
from app.utils.file_utils import validate_pdf_bytes

from frontend.components.explanation_panel import render_explanation
from frontend.components.score_card import render_score_card
from frontend.components.skills_table import render_skills
from frontend.components.upload_box import render_inputs

st.set_page_config(
    page_title="AI Resume Job Matcher",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 AI Resume Job Matcher")
st.caption("Compare your resume with a job description.")

resume, job_description = render_inputs()

if st.button("Analyze match", type="primary", use_container_width=True):
    st.session_state.pop("analysis", None)

    if resume is None:
        st.error("Upload a resume PDF.")
    elif len(job_description.strip()) < 50:
        st.error("Enter a job description of at least 50 characters.")
    else:
        try:
            with st.spinner("Analyzing resume..."):
                pdf_bytes = resume.getvalue()
                validate_pdf_bytes(pdf_bytes, settings.max_file_size_mb)

                resume_text = PDFParser().extract_text_from_bytes(
                    pdf_bytes
                )

                result = AnalysisService().analyze_text(
                    resume_text,
                    job_description,
                    resume_filename=resume.name,
                )

                st.session_state["analysis"] = result

        except HTTPException as exc:
            st.error(str(exc.detail))
        except (PdfReadError, ValueError, OSError):
            st.error("Unable to read the PDF. Use a text-based PDF.")

result = st.session_state.get("analysis")

if result:
    st.divider()
    render_score_card(result)

    overview, skills, recommendations, methodology = st.tabs(
        ["Overview", "Skills", "Recommendations", "Methodology"]
    )

    with overview:
        render_explanation(result)
        if result["must_have_gaps"]:
            st.warning(
                "Required skill gaps: "
                + ", ".join(result["must_have_gaps"])
            )

    with skills:
        render_skills(result)

    with recommendations:
        for item in result["recommendations"]:
            with st.expander(item["title"]):
                st.write(item["action"])

    with methodology:
        st.write(f"Algorithm: {result['algorithm_version']}")
        st.write(result["disclaimer"])
