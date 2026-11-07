"""Prioritized, evidence-safe recommendations for an analysis result."""

from __future__ import annotations


def build_recommendations(analysis: dict) -> list[dict]:
    recommendations: list[dict] = []
    priority = 1

    for skill in analysis["skills"]["missing_required_skills"][:5]:
        recommendations.append({
            "priority": priority,
            "type": "required_skill_gap",
            "title": f"Address the {skill} requirement",
            "action": (
                f"If you genuinely have {skill} experience, add a specific project or work bullet "
                "showing how you used it and the result. Otherwise, treat it as a learning gap; do not claim it."
            ),
        })
        priority += 1

    experience = analysis["experience"]
    if experience["required_years"] is not None and experience["candidate_years"] is None:
        recommendations.append({
            "priority": priority,
            "type": "experience_clarity",
            "title": "Make relevant experience duration explicit",
            "action": (
                f"The role asks for {experience['required_years']:g}+ years, but the resume did not provide "
                "enough reliable date evidence. Use consistent month/year ranges and summarize relevant tenure truthfully."
            ),
        })
        priority += 1
    elif experience["matched"] is False:
        recommendations.append({
            "priority": priority,
            "type": "experience_gap",
            "title": "Lead with the most relevant experience",
            "action": (
                "The stated experience requirement is above the duration detected in the resume. "
                "Emphasize directly relevant projects, scope, ownership, and measurable outcomes without overstating tenure."
            ),
        })
        priority += 1

    education = analysis["education"]
    if education["required_level"] and education["matched"] is not True:
        recommendations.append({
            "priority": priority,
            "type": "education_gap",
            "title": "Clarify education or equivalent preparation",
            "action": (
                f"The posting mentions {education['required_level']}. Clearly list an applicable degree, "
                "coursework, certification, or equivalent experience only when it is accurate."
            ),
        })
        priority += 1

    for skill in analysis["skills"]["missing_preferred_skills"][:3]:
        recommendations.append({
            "priority": priority,
            "type": "preferred_skill_gap",
            "title": f"Consider the preferred {skill} skill",
            "action": (
                f"This is labelled preferred, not required. Add truthful {skill} evidence if available; "
                "otherwise prioritize the required gaps first."
            ),
        })
        priority += 1

    if analysis["subscores"]["contextual_alignment"] < 45:
        recommendations.append({
            "priority": priority,
            "type": "alignment",
            "title": "Connect achievements to the role's responsibilities",
            "action": (
                "Rewrite relevant bullets so they name the actual problem, action, tools, and measured result. "
                "Mirror the posting's terminology only where it accurately describes your work."
            ),
        })
        priority += 1

    if not recommendations:
        recommendations.append({
            "priority": 1,
            "type": "strengthen_evidence",
            "title": "Strengthen the evidence behind the match",
            "action": (
                "Keep the strong alignment, but quantify impact in the most relevant bullets and verify that "
                "every listed skill is supported by a project or work example."
            ),
        })
    return recommendations[:8]
