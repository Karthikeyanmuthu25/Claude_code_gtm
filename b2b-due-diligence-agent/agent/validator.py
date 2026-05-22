"""
Input Validation Module — Pre-flight checks before pipeline execution.
"""

import re
from typing import Tuple, List
from urllib.parse import urlparse


REQUIRED_FIELDS = ["company_name", "decision_maker_name"]
RECOMMENDED_FIELDS = [
    "company_website",
    "company_location",
    "decision_maker_job_title",
    "decision_maker_linkedin_url",
    "decision_maker_email",
]


def validate_url(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


def validate_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def validate_linkedin_url(url: str) -> bool:
    return "linkedin.com/in/" in url.lower()


def extract_domain(url: str) -> str:
    try:
        p = urlparse(url if url.startswith("http") else f"https://{url}")
        return p.netloc.replace("www.", "").lower()
    except Exception:
        return ""


def extract_email_domain(email: str) -> str:
    try:
        return email.split("@")[1].lower()
    except Exception:
        return ""


def validate_input(data: dict) -> Tuple[bool, List[str], List[str]]:
    """
    Validate input data before pipeline execution.
    Returns (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    # Required fields
    for field in REQUIRED_FIELDS:
        if not data.get(field, "").strip():
            errors.append(f"Missing required field: {field}")

    # Recommended fields
    for field in RECOMMENDED_FIELDS:
        if not data.get(field, "").strip():
            warnings.append(f"Missing recommended field: {field} — analysis coverage reduced")

    # URL validation
    website = data.get("company_website", "")
    if website and not validate_url(website):
        warnings.append(f"Company website URL may be malformed: {website}")

    # Email validation
    email = data.get("decision_maker_email", "")
    if email and not validate_email(email):
        warnings.append(f"Email format looks invalid: {email}")

    # LinkedIn validation
    linkedin = data.get("decision_maker_linkedin_url", "")
    if linkedin and not validate_linkedin_url(linkedin):
        warnings.append(f"LinkedIn URL does not look like a profile URL: {linkedin}")

    # Domain alignment check
    if website and email:
        web_domain = extract_domain(website)
        email_domain = extract_email_domain(email)
        if web_domain and email_domain and web_domain != email_domain:
            warnings.append(
                f"Email domain ({email_domain}) does not match company website domain ({web_domain}) — potential mismatch"
            )

    is_valid = len(errors) == 0
    return is_valid, errors, warnings
