import streamlit as st


def render_score_card(result: dict) -> None:
    score = float(result["overall_score"])
    confidence = result["confidence"]
    left, middle, right = st.columns(3)
    left.metric("Overall match", f"{score:.1f}%")
    middle.metric("Verdict", result["verdict_label"])
    right.metric("Confidence", f"{confidence['label'].title()} ({confidence['score']:.0%})")
    st.progress(score / 100, text="Weighted match score")

    components = {
        "Required skills": "required_skills",
        "Preferred skills": "preferred_skills",
        "Experience": "experience",
        "Education": "education",
        "Context": "contextual_alignment",
    }
    columns = st.columns(len(components))
    for column, (label, key) in zip(columns, components.items()):
        value = result["subscores"][key]
        display = f"{value:.0f}%" if key in result["weights_used"] else "N/A"
        column.metric(label, display)
