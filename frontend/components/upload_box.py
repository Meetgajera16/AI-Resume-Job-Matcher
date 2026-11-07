import streamlit as st


def render_inputs():
    resume = st.file_uploader("Resume PDF", type=["pdf"], help="Use a text-based PDF under 10 MB.")
    job_description = st.text_area(
        "Job description",
        height=280,
        placeholder="Paste the complete responsibilities and qualifications…",
    )
    return resume, job_description
