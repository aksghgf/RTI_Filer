import re
from langdetect import detect
from pydantic import BaseModel

class ValidationResult(BaseModel):
    valid: bool
    hint: str = ""
    sanitized_text: str = ""
    language: str = "en"

class QualityResult(BaseModel):
    passed: bool
    issues: list[str]

def validate_rti_input(problem: str) -> ValidationResult:
    """Sanitizes and validates the raw user input."""
    if len(problem.strip()) < 20:
        return ValidationResult(
            valid=False,
            hint="Please provide more specific details about the issue. (Min 20 characters required)"
        )
    try:
        detected_lang = detect(problem)
    except Exception:
        detected_lang = "en"

    blocked_patterns = [
        "why is", "why not", "your opinion", "future plans", "corrupt", "wrong info",
        "क्यों", "क्यूँ", "गलत है", "भ्रष्टाचार", "राय क्या है", "भविष्य की योजना",
        "kyun", "kyu nahi", "galat hai", "bhrashtachar", "opinion kya hai", "kaisa lagta"
    ]

    for word in blocked_patterns:
        if word in problem.lower():
            return ValidationResult(
                valid=False,
                hint="RTI is strictly for requesting existing records. 'Why' questions or opinions are not allowed."
            )

    sanitized = re.sub(r'[<>]', '', problem)
    return ValidationResult(valid=True, sanitized_text=sanitized, hint="", language=detected_lang)


def validate_rti_output(rti_text: str) -> QualityResult:
    """Lightweight quality check — formal headers are added by the PDF layer."""
    issues = []

    if len(rti_text) > 1500:
        issues.append("Exceeded the 1500-character limit.")

    opinion_words = ["corruption", "action against"]
    for word in opinion_words:
        if word in rti_text.lower():
            issues.append(f"Invalid opinion word detected: '{word}'")

    return QualityResult(passed=len(issues) == 0, issues=issues)
