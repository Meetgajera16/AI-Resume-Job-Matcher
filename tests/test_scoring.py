import unittest

from app.scoring.match_score import (
    assess_education,
    assess_experience,
    calculate_match,
    contextual_alignment,
)
from app.scoring.skills_gap import analyze_skill_gap, extract_skills
from app.scoring.suggestions import build_recommendations


RESUME = """
Alex Doe
Data Scientist

Skills: Python, SQL, pandas, scikit-learn, FastAPI, Docker, and AWS.

Experience
Data Scientist | January 2022 - Present
Built machine learning models in Python and deployed REST APIs with FastAPI.
Improved model accuracy by 18% and partnered with product teams.

Education
Master of Science in Data Science
"""

JOB = """
Senior Data Scientist

Requirements:
- 3+ years of professional experience
- Strong Python and SQL skills
- Machine learning and REST API development
- Bachelor's degree in Computer Science or a related field

Preferred qualifications:
- AWS
- Kubernetes
- Power BI

Build production models and collaborate with product teams to deliver measurable outcomes.
"""


class SkillGapTests(unittest.TestCase):
    def test_required_and_preferred_skills_are_separated(self):
        result = analyze_skill_gap(RESUME, JOB)
        required = {item["skill"] for item in result["required"]}
        preferred = {item["skill"] for item in result["preferred"]}

        self.assertTrue({"Python", "SQL", "Machine Learning", "REST APIs"} <= required)
        self.assertEqual({"AWS", "Kubernetes", "Power BI"}, preferred)
        self.assertEqual(["Kubernetes", "Power BI"], result["missing_preferred_skills"])
        self.assertEqual([], result["missing_required_skills"])

    def test_aliases_and_word_boundaries(self):
        skills = extract_skills("Built JS services with PySpark and PostgreSQL; no other languages listed.")
        self.assertIn("JavaScript", skills)
        self.assertIn("Apache Spark", skills)
        self.assertIn("PostgreSQL", skills)
        self.assertNotIn("Java", skills)
        self.assertNotIn("SQL", skills)

    def test_duplicate_keywords_do_not_inflate_coverage(self):
        result = analyze_skill_gap("Python Python Python", "Required: Python and SQL")
        self.assertEqual(50.0, result["required_coverage"])


class MatchScoreTests(unittest.TestCase):
    def test_experience_date_ranges_and_education_are_assessed(self):
        experience = assess_experience(RESUME, JOB)
        education = assess_education(RESUME, JOB)

        self.assertEqual(3.0, experience["required_years"])
        self.assertTrue(experience["matched"])
        self.assertEqual("date_range_estimate", experience["estimation_method"])
        self.assertEqual("Bachelor's degree", education["required_level"])
        self.assertEqual("Master's degree", education["candidate_level"])
        self.assertTrue(education["matched"])

    def test_full_analysis_is_bounded_and_weights_normalize(self):
        result = calculate_match(RESUME, JOB)

        self.assertGreaterEqual(result["overall_score"], 0)
        self.assertLessEqual(result["overall_score"], 100)
        self.assertAlmostEqual(100.0, sum(result["weights_used"].values()), places=1)
        self.assertEqual([], result["must_have_gaps"])

    def test_dynamic_weights_omit_unstated_requirements(self):
        result = calculate_match(
            "Python developer who built payment APIs and improved response latency by 40 percent.",
            "We need a Python developer to build reliable payment APIs and improve response latency.",
        )
        self.assertNotIn("experience", result["weights_used"])
        self.assertNotIn("education", result["weights_used"])
        self.assertIn("required_skills", result["weights_used"])

    def test_contextual_alignment_rewards_shared_responsibilities(self):
        aligned = contextual_alignment(
            "Built fraud detection models and deployed fraud APIs.",
            "Build fraud detection models and deploy fraud APIs.",
        )
        unrelated = contextual_alignment(
            "Managed retail inventory and supplier contracts.",
            "Build fraud detection models and deploy fraud APIs.",
        )
        self.assertGreater(aligned, unrelated)

    def test_gap_recommendation_does_not_encourage_false_claims(self):
        result = calculate_match("Python developer with API projects.", "Required: Python, SQL, and AWS for data APIs.")
        recommendations = build_recommendations(result)
        combined = " ".join(item["action"] for item in recommendations).lower()
        self.assertIn("do not claim it", combined)


if __name__ == "__main__":
    unittest.main()
