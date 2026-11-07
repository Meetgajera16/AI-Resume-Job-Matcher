from fastapi import APIRouter


router = APIRouter()


@router.get("/explain", summary="Explain how advanced matching works")
def explain_methodology() -> dict:
    return {
        "algorithm_version": "hybrid-explainable-v1",
        "method": (
            "A deterministic hybrid of canonical skill coverage, stated/estimated experience, "
            "education requirements, and TF-IDF contextual alignment."
        ),
        "default_weights": {
            "required_skills": 45,
            "preferred_skills": 10,
            "experience": 15,
            "education": 10,
            "contextual_alignment": 20,
        },
        "dynamic_weighting": (
            "Components not stated in the job description are omitted and the remaining weights are normalized."
        ),
        "guardrails": [
            "Protected characteristics are not extracted or scored.",
            "A skill is counted once, limiting keyword stuffing.",
            "Evidence snippets make matches auditable.",
            "Recommendations tell users not to claim skills they do not have.",
        ],
        "limitations": [
            "The curated taxonomy may miss niche skills or equivalents.",
            "Date-range experience is an estimate and can include non-relevant roles.",
            "Contextual alignment is lexical and is not proof of proficiency.",
            "Scanned PDFs require OCR before analysis.",
        ],
    }
