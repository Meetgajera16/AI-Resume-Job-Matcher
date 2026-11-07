"""Auditable skill extraction and gap analysis."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from app.scoring.taxonomy import SKILL_TAXONOMY, SkillDefinition


PREFERRED_MARKERS = re.compile(
    r"\b(preferred|nice[ -]to[ -]have|bonus|plus|desired|advantageous|optional)\b",
    re.IGNORECASE,
)
REQUIRED_MARKERS = re.compile(
    r"\b(required|requirement|requirements|must|minimum|need(?:ed)?|qualification|"
    r"qualifications|proficien(?:t|cy)|strong|expertise|experience with)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class FoundSkill:
    definition: SkillDefinition
    evidence: str
    start: int


def _alias_regex(alias: str) -> re.Pattern[str]:
    escaped = re.escape(alias)
    return re.compile(rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])", re.IGNORECASE)


def _clean_snippet(value: str, limit: int = 220) -> str:
    value = re.sub(r"\s+", " ", value).strip(" \t\r\n•-|")
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def _evidence_window(text: str, start: int, end: int) -> str:
    line_start = max(text.rfind("\n", 0, start) + 1, 0)
    line_end = text.find("\n", end)
    if line_end == -1:
        line_end = len(text)
    line = _clean_snippet(text[line_start:line_end])
    if 18 <= len(line) <= 260:
        return line

    return _clean_snippet(_local_segment(text, start, end))


def _local_segment(text: str, start: int, end: int) -> str:
    boundaries = ".;\n•"
    segment_start = max((text.rfind(mark, 0, start) for mark in boundaries), default=-1) + 1
    following = [position for mark in boundaries if (position := text.find(mark, end)) != -1]
    segment_end = min(following) if following else min(len(text), end + 180)
    return text[segment_start:segment_end]


def _find_definition(text: str, definition: SkillDefinition) -> FoundSkill | None:
    best_match: re.Match[str] | None = None
    for alias in sorted(definition.aliases, key=len, reverse=True):
        match = _alias_regex(alias).search(text)
        if match and (best_match is None or match.start() < best_match.start()):
            best_match = match
    if best_match is None:
        return None
    return FoundSkill(
        definition=definition,
        evidence=_evidence_window(text, best_match.start(), best_match.end()),
        start=best_match.start(),
    )


def extract_skills(text: str) -> dict[str, FoundSkill]:
    """Return canonical skills found in *text*, keyed by canonical name."""

    if not text.strip():
        return {}
    found: dict[str, FoundSkill] = {}
    for definition in SKILL_TAXONOMY:
        match = _find_definition(text, definition)
        if match:
            found[definition.name] = match
    return found


def _importance(text: str, skill: FoundSkill) -> str:
    line_start = max(text.rfind("\n", 0, skill.start) + 1, 0)
    previous_line_start = max(text.rfind("\n", 0, max(0, line_start - 1)) + 1, 0)
    line_end = text.find("\n", skill.start)
    if line_end == -1:
        line_end = len(text)
    context = text[previous_line_start:line_end]

    # A local preferred marker takes precedence over broad headings such as
    # "Requirements", which may still be inside the look-behind window.
    skill_end = skill.start + len(skill.definition.name)
    local_segment = _local_segment(text, skill.start, skill_end)
    if PREFERRED_MARKERS.search(local_segment):
        return "preferred"
    if REQUIRED_MARKERS.search(local_segment):
        return "required"

    # Carry forward the nearest short section heading. PDF extraction commonly
    # places "Preferred qualifications:" several bullets before a skill.
    prior_lines = text[:line_start].splitlines()[-8:]
    for prior_line in reversed(prior_lines):
        candidate = prior_line.strip(" \t•-")
        if not candidate or len(candidate) > 90:
            continue
        if PREFERRED_MARKERS.search(candidate):
            return "preferred"
        if REQUIRED_MARKERS.search(candidate):
            return "required"
    if PREFERRED_MARKERS.search(context):
        return "preferred"
    if REQUIRED_MARKERS.search(context):
        return "required"
    # Skills named by a job description are treated as required unless the
    # employer labels them as optional. This conservative rule avoids inflating
    # a candidate's match by silently downgrading unlabelled requirements.
    return "required"


def _skill_record(
    job_skill: FoundSkill,
    resume_skill: FoundSkill | None,
    importance: str,
) -> dict:
    return {
        "skill": job_skill.definition.name,
        "category": job_skill.definition.category,
        "importance": importance,
        "matched": resume_skill is not None,
        "job_evidence": job_skill.evidence,
        "resume_evidence": resume_skill.evidence if resume_skill else None,
    }


def _coverage(items: Iterable[dict]) -> float:
    values = list(items)
    if not values:
        return 100.0
    return round(100 * sum(1 for item in values if item["matched"]) / len(values), 1)


def analyze_skill_gap(resume_text: str, job_text: str) -> dict:
    """Compare canonical job skills against resume evidence."""

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)
    records = [
        _skill_record(job_skill, resume_skills.get(name), _importance(job_text, job_skill))
        for name, job_skill in job_skills.items()
    ]
    records.sort(key=lambda item: (item["importance"] != "required", not item["matched"], item["skill"]))

    required = [item for item in records if item["importance"] == "required"]
    preferred = [item for item in records if item["importance"] == "preferred"]
    resume_only = sorted(set(resume_skills) - set(job_skills))

    return {
        "required": required,
        "preferred": preferred,
        "required_coverage": _coverage(required),
        "preferred_coverage": _coverage(preferred),
        "matched_skills": [item["skill"] for item in records if item["matched"]],
        "missing_required_skills": [item["skill"] for item in required if not item["matched"]],
        "missing_preferred_skills": [item["skill"] for item in preferred if not item["matched"]],
        "additional_resume_skills": resume_only,
    }
