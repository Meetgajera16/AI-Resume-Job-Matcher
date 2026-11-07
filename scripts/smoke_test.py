"""Small deployed/local API smoke test."""

import argparse

import requests


RESUME = """
Data scientist with 4 years of professional experience. Built Python and SQL
machine-learning services on AWS, deployed REST APIs, and improved accuracy by 18%.
Bachelor of Science in Computer Science.
"""
JOB = """
We require 3+ years of experience with Python, SQL, machine learning, and REST APIs.
A bachelor's degree is required. AWS and Kubernetes are preferred qualifications.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    health = requests.get(f"{args.url.rstrip('/')}/health", timeout=10)
    health.raise_for_status()
    analysis = requests.post(
        f"{args.url.rstrip('/')}/analyze/text",
        json={"resume_text": RESUME, "job_description": JOB},
        timeout=30,
    )
    analysis.raise_for_status()
    payload = analysis.json()
    assert 0 <= payload["overall_score"] <= 100
    assert payload["algorithm_version"] == "hybrid-explainable-v1"
    print(f"Smoke test passed: {payload['overall_score']}% ({payload['verdict_label']})")


if __name__ == "__main__":
    main()
