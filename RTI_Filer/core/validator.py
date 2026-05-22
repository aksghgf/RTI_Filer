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
        detected_lang = detect(problem) # 'hi' for Hindi, 'en' for English
    except:
        detected_lang = "en" # Fallback to English if it fails

    blocked_patterns = [
        # English
        "why is", "why not", "your opinion", "future plans", "corrupt", "wrong info", 
        # Pure Hindi (Devanagari)
        "क्यों", "क्यूँ", "गलत है", "भ्रष्टाचार", "राय क्या है", "भविष्य की योजना",
        # Hinglish (User variations)
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
    """Evaluates the AI-generated draft against RTI legal rules."""
    issues = []
    
    if len(rti_text) > 500:
        issues.append("Exceeded the 500-character limit.")
        
    if "Public Information Officer" not in rti_text:
        issues.append("Missing mandatory 'Public Information Officer' addressing.")
        
    opinion_words = ["why", "feel", "wrong", "corruption", "action against"]
    for w in opinion_words:
        if w in rti_text.lower():
            issues.append(f"Invalid opinion or question word detected: '{w}'")
            
    return QualityResult(passed=len(issues) == 0, issues=issues)