import pandas as pd
import streamlit as st


def render_skills(result: dict) -> None:
    skills = result["skills"]
    items = skills["required"] + skills["preferred"]
    if not items:
        st.info("No skills from the current taxonomy were detected in the job description.")
        return

    table = pd.DataFrame([
        {
            "Skill": item["skill"],
            "Category": item["category"],
            "Importance": item["importance"].title(),
            "Status": "Matched" if item["matched"] else "Gap",
            "Resume evidence": item["resume_evidence"] or "—",
            "Job evidence": item["job_evidence"],
        }
        for item in items
    ])
    st.dataframe(table, hide_index=True, use_container_width=True)

    if skills["additional_resume_skills"]:
        st.caption("Additional resume skills: " + ", ".join(skills["additional_resume_skills"]))
