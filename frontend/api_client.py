from __future__ import annotations

import requests


class MatcherAPIError(RuntimeError):
    pass


def analyze_resume(api_url: str, resume_file, job_description: str, timeout: int = 90) -> dict:
    api_url = api_url.strip().rstrip("/")
    if not api_url.startswith(("http://", "https://")):
        api_url = f"http://{api_url}"
    try:
        response = requests.post(
            f"{api_url}/analyze",
            files={
                "resume": (
                    resume_file.name,
                    resume_file.getvalue(),
                    "application/pdf",
                )
            },
            data={"job_description": job_description},
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise MatcherAPIError(f"Could not reach the API: {exc}") from exc

    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise MatcherAPIError(str(detail))
    return response.json()
