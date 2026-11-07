import streamlit as st


def _display_value(value, suffix: str = "") -> str:
    return "Not stated" if value is None else f"{value:g}{suffix}" if isinstance(value, float) else str(value)


def render_explanation(result: dict) -> None:
    experience = result["experience"]
    education = result["education"]
    left, right = st.columns(2)
    with left:
        st.subheader("Experience")
        st.write(f"Job requirement: **{_display_value(experience['required_years'], '+ years')}**")
        st.write(f"Resume estimate: **{_display_value(experience['candidate_years'], ' years')}**")
        if experience["resume_evidence"]:
            st.caption(experience["resume_evidence"])
    with right:
        st.subheader("Education")
        st.write(f"Job requirement: **{education['required_level'] or 'Not stated'}**")
        st.write(f"Resume: **{education['candidate_level'] or 'Not detected'}**")
        if education["resume_evidence"]:
            st.caption(education["resume_evidence"])

    st.subheader("Score weights used")
    st.json(result["weights_used"])
