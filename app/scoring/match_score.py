"""Explainable, deterministic resume-to-job scoring.

This module deliberately keeps the score reproducible and inspectable.  It is
not a hiring decision system and does not use protected personal attributes.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from datetime import date

from app.scoring.skills_gap import analyze_skill_gap, extract_skills


STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "have", "in", "is", "it", "of", "on", "or", "our", "that", "the", "their",
    "this", "to", "we", "will", "with", "you", "your", "who", "work", "role",
    "job", "team", "using", "including", "responsible", "responsibilities",
}

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7,
    "july": 7, "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12,
    "december": 12,
}
MONTH_PATTERN = "|".join(MONTHS)
PRESENT_PATTERN = r"present|current|now"

DEGREE_LEVELS = {
    "high_school": 0,
    "associate": 1,
    "bachelor": 2,
    "master": 3,
    "doctorate": 4,
}
DEGREE_LABELS = {
    "high_school": "High school diploma",
    "associate": "Associate degree",
    "bachelor": "Bachelor's degree",
    "master": "Master's degree",
    "doctorate": "Doctorate",
}
DEGREE_PATTERNS = {
    "high_school": re.compile(r"\b(high school diploma|ged)\b", re.IGNORECASE),
    "associate": re.compile(r"\b(associate(?:'s)? degree|a\.?a\.?s?\.? degree)\b", re.IGNORECASE),
    "bachelor": re.compile(r"\b(bachelor(?:'s)?(?: degree)?|b\.?s\.?|b\.?a\.?|btech|b\.tech)\b", re.IGNORECASE),
    "master": re.compile(r"\b(master(?:'s)?(?: degree)?|m\.?s\.?|m\.?a\.?|mba|mtech|m\.tech)\b", re.IGNORECASE),
    "doctorate": re.compile(r"\b(doctorate|doctoral|ph\.?d\.?)\b", re.IGNORECASE),
}


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def _extract_required_years(job_text: str) -> tuple[float | None, str | None]:
    pattern = re.compile(
        r"\b(\d{1,2})(?:\s*(?:\+|plus))?(?:\s*(?:-|–|—|to)\s*\d{1,2})?\s+years?\b",
        re.IGNORECASE,
    )
    candidates: list[tuple[float, str]] = []
    for match in pattern.finditer(job_text):
        context = job_text[max(0, match.start() - 90): min(len(job_text), match.end() + 100)]
        if re.search(r"experience|professional|industry|hands-on|working", context, re.IGNORECASE):
            candidates.append((float(match.group(1)), re.sub(r"\s+", " ", context).strip()))
    if not candidates:
        return None, None
    years, evidence = max(candidates, key=lambda item: item[0])
    return years, evidence[:220]


def _month_number(value: str | None, default: int) -> int:
    return MONTHS.get((value or "").lower(), default)


def _resume_date_intervals(resume_text: str) -> list[tuple[int, int]]:
    today = date.today()
    intervals: list[tuple[int, int]] = []
    month_range = re.compile(
        rf"\b({MONTH_PATTERN})\.?\s+((?:19|20)\d{{2}})\s*(?:-|–|—|to)\s*"
        rf"(?:({MONTH_PATTERN})\.?\s+((?:19|20)\d{{2}})|({PRESENT_PATTERN}))\b",
        re.IGNORECASE,
    )
    for match in month_range.finditer(resume_text):
        start = int(match.group(2)) * 12 + _month_number(match.group(1), 1) - 1
        if match.group(5):
            end = today.year * 12 + today.month
        else:
            end = int(match.group(4)) * 12 + _month_number(match.group(3), 12)
        if start < end and end - start <= 600:
            intervals.append((start, end))

    year_range = re.compile(
        rf"\b((?:19|20)\d{{2}})\s*(?:-|–|—|to)\s*({PRESENT_PATTERN}|(?:19|20)\d{{2}})\b",
        re.IGNORECASE,
    )
    for match in year_range.finditer(resume_text):
        start = int(match.group(1)) * 12
        if re.fullmatch(PRESENT_PATTERN, match.group(2), re.IGNORECASE):
            end = today.year * 12 + today.month
        else:
            end = (int(match.group(2)) + 1) * 12
        if start < end and end - start <= 600:
            intervals.append((start, end))
    return sorted(set(intervals))


def _merged_years(intervals: list[tuple[int, int]]) -> float | None:
    if not intervals:
        return None
    intervals.sort()
    merged: list[list[int]] = []
    for start, end in intervals:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    months = sum(end - start for start, end in merged)
    return round(min(months / 12, 40.0), 1)


def _extract_candidate_years(resume_text: str) -> tuple[float | None, str | None, str | None]:
    explicit_pattern = re.compile(
        r"\b(\d{1,2})(?:\s*(?:\+|plus))?\s+years?(?:\s+of)?\s+(?:professional\s+)?experience\b",
        re.IGNORECASE,
    )
    explicit = list(explicit_pattern.finditer(resume_text))
    if explicit:
        match = max(explicit, key=lambda item: int(item.group(1)))
        evidence = resume_text[max(0, match.start() - 70): min(len(resume_text), match.end() + 90)]
        return float(match.group(1)), re.sub(r"\s+", " ", evidence).strip()[:220], "explicit_statement"

    intervals = _resume_date_intervals(resume_text)
    years = _merged_years(intervals)
    if years is not None:
        return years, f"Estimated from {len(intervals)} employment date range(s) in the resume.", "date_range_estimate"
    return None, None, None


def assess_experience(resume_text: str, job_text: str) -> dict:
    required, job_evidence = _extract_required_years(job_text)
    candidate, resume_evidence, method = _extract_candidate_years(resume_text)
    if required is None:
        score = 100.0
        matched = None
    elif candidate is None:
        score = 50.0
        matched = None
    else:
        score = round(_clamp(100 * candidate / required), 1)
        matched = candidate >= required
    return {
        "required_years": required,
        "candidate_years": candidate,
        "matched": matched,
        "score": score,
        "estimation_method": method,
        "job_evidence": job_evidence,
        "resume_evidence": resume_evidence,
    }


def _degree_mentions(text: str) -> list[tuple[str, int, str, bool]]:
    mentions: list[tuple[str, int, str, bool]] = []
    for key, pattern in DEGREE_PATTERNS.items():
        for match in pattern.finditer(text):
            before_positions = [text.rfind(mark, 0, match.start()) for mark in ".;\n•"]
            segment_start = max(before_positions) + 1
            after_positions = [
                position for mark in ".;\n•"
                if (position := text.find(mark, match.end())) != -1
            ]
            segment_end = min(after_positions) if after_positions else min(len(text), match.end() + 180)
            segment = re.sub(r"\s+", " ", text[segment_start:segment_end]).strip()[:220]
            preferred = bool(re.search(r"\b(preferred|desired|nice[ -]to[ -]have|bonus)\b", segment, re.IGNORECASE))
            mentions.append((key, DEGREE_LEVELS[key], segment, preferred))
    return mentions


def assess_education(resume_text: str, job_text: str) -> dict:
    job_mentions = _degree_mentions(job_text)
    resume_mentions = _degree_mentions(resume_text)
    required_mentions = [item for item in job_mentions if not item[3]]
    preferred_mentions = [item for item in job_mentions if item[3]]
    required = max(required_mentions, key=lambda item: item[1], default=None)
    preferred = max(preferred_mentions, key=lambda item: item[1], default=None)
    candidate = max(resume_mentions, key=lambda item: item[1], default=None)

    if required is None:
        score = 100.0
        matched = None
    elif candidate is None:
        score = 50.0
        matched = None
    else:
        score = 100.0 if candidate[1] >= required[1] else round(100 * (candidate[1] + 1) / (required[1] + 1), 1)
        matched = candidate[1] >= required[1]

    return {
        "required_level": DEGREE_LABELS[required[0]] if required else None,
        "preferred_level": DEGREE_LABELS[preferred[0]] if preferred else None,
        "candidate_level": DEGREE_LABELS[candidate[0]] if candidate else None,
        "matched": matched,
        "score": score,
        "job_evidence": required[2] if required else (preferred[2] if preferred else None),
        "resume_evidence": candidate[2] if candidate else None,
    }


def _features(text: str) -> Counter[str]:
    tokens = [
        token for token in re.findall(r"[a-z][a-z0-9+#.-]{1,}", text.lower())
        if token not in STOP_WORDS and not token.isdigit()
    ]
    counts: Counter[str] = Counter(tokens)
    counts.update(f"{left}_{right}" for left, right in zip(tokens, tokens[1:]))
    # Canonical skills improve alias-aware alignment while retaining surrounding
    # responsibility terms in the lexical vectors.
    counts.update({f"skill:{name.lower()}": 3 for name in extract_skills(text)})
    return counts


def contextual_alignment(resume_text: str, job_text: str) -> float:
    resume = _features(resume_text)
    job = _features(job_text)
    if not resume or not job:
        return 0.0
    all_terms = set(resume) | set(job)
    resume_vector: dict[str, float] = {}
    job_vector: dict[str, float] = {}
    for term in all_terms:
        document_frequency = int(term in resume) + int(term in job)
        inverse_document_frequency = math.log(3 / (1 + document_frequency)) + 1
        resume_vector[term] = (1 + math.log(resume[term])) * inverse_document_frequency if resume[term] else 0.0
        job_vector[term] = (1 + math.log(job[term])) * inverse_document_frequency if job[term] else 0.0
    dot = sum(resume_vector[term] * job_vector[term] for term in all_terms)
    resume_norm = math.sqrt(sum(value * value for value in resume_vector.values()))
    job_norm = math.sqrt(sum(value * value for value in job_vector.values()))
    if not resume_norm or not job_norm:
        return 0.0
    return round(_clamp(100 * dot / (resume_norm * job_norm)), 1)


def _confidence(resume_text: str, job_text: str, skill_count: int, has_years: bool, has_degree: bool) -> dict:
    score = 0.42
    score += min(skill_count, 10) * 0.025
    score += 0.08 if has_years else 0.0
    score += 0.05 if has_degree else 0.0
    score += 0.08 if len(resume_text) >= 800 else 0.0
    score += 0.08 if len(job_text) >= 500 else 0.0
    score = round(min(score, 0.95), 2)
    label = "high" if score >= 0.8 else "medium" if score >= 0.6 else "low"
    return {"score": score, "label": label}


def _verdict(score: float, missing_required_count: int) -> tuple[str, str]:
    if score >= 85 and missing_required_count == 0:
        return "strong_match", "Strong match"
    if score >= 70 and missing_required_count <= 1:
        return "good_match", "Good match"
    if score >= 55:
        return "possible_match", "Possible match"
    return "weak_match", "Weak match"


def calculate_match(resume_text: str, job_text: str) -> dict:
    skills = analyze_skill_gap(resume_text, job_text)
    experience = assess_experience(resume_text, job_text)
    education = assess_education(resume_text, job_text)
    alignment = contextual_alignment(resume_text, job_text)

    components: list[tuple[str, float, float, bool]] = [
        ("required_skills", skills["required_coverage"], 45.0, bool(skills["required"])),
        ("preferred_skills", skills["preferred_coverage"], 10.0, bool(skills["preferred"])),
        ("experience", experience["score"], 15.0, experience["required_years"] is not None),
        ("education", education["score"], 10.0, education["required_level"] is not None),
        ("contextual_alignment", alignment, 20.0, True),
    ]
    active = [item for item in components if item[3]]
    total_weight = sum(item[2] for item in active)
    overall = round(sum(score * weight for _, score, weight, _ in active) / total_weight, 1)
    normalized_weights = {name: round(100 * weight / total_weight, 1) for name, _, weight, _ in active}
    subscores = {name: score for name, score, _, _ in components}

    verdict_code, verdict_label = _verdict(overall, len(skills["missing_required_skills"]))
    confidence = _confidence(
        resume_text,
        job_text,
        len(skills["required"]) + len(skills["preferred"]),
        experience["required_years"] is not None,
        education["required_level"] is not None,
    )
    return {
        "overall_score": overall,
        "verdict": verdict_code,
        "verdict_label": verdict_label,
        "confidence": confidence,
        "subscores": subscores,
        "weights_used": normalized_weights,
        "skills": skills,
        "experience": experience,
        "education": education,
        "must_have_gaps": skills["missing_required_skills"],
    }
