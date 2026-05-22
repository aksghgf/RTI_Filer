import os
import asyncio
from groq import AsyncGroq
from google import genai
from dotenv import load_dotenv
from core.validator import validate_rti_output

# Load API keys from the .env file
load_dotenv(encoding="utf-8-sig")

# Initialize API Clients
# We use AsyncGroq so our backend doesn't freeze while waiting for the AI
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# The Master Instruction for the AI
# --- PURANA SYSTEM PROMPT BADAL KAR YE LIKHO ---
SYSTEM_PROMPT = """You are an expert Indian Legal AI Assistant specializing in drafting comprehensive RTI (Right to Information) applications.
Strict Rules:
1. ALWAYS start the draft with "Subject: Request for Information under RTI Act, 2005."
2. Keep it factual, objective, structured, and elaborate on the core points.
3. NEVER include personal emotions, opinions, or ask "Why" questions. Ask for specific facts, logs, records, or status reports.
4. Keep the total length strictly under 1500 characters to ensure all necessary points are covered.
5. Output ONLY the drafted application text. No conversational text, no greetings, no "Here is your draft".
"""

# 👑 DIRECT FIX: Function variables badlo aur user context prompt mein dalo
async def call_groq(prompt: str, user_name: str, user_location: str) -> str:
    """Primary Engine: Fast & Cheap Llama 3.1 8B via Groq."""
    response = await groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user", 
                "content": f"Draft a detailed RTI application.\nIssue: {prompt}\nApplicant Name: {user_name}\nApplicant Location/Jurisdiction: {user_location}\n\nCRITICAL: Do not use placeholders like [Your Name]. Put '{user_name}' at the end under 'Sincerely,'."
            }
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


async def call_gemini(prompt: str, user_name: str, user_location: str) -> str:
    """Secondary Engine: Reliable Fallback via Gemini 1.5 Flash."""
    # Context jodh kar full prompt banaya
    user_context = f"Issue: {prompt}\nApplicant Name: {user_name}\nApplicant Location: {user_location}\n\nCRITICAL: Do not leave placeholders. Put '{user_name}' in the signature block."
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_context}"
    
    response = await asyncio.to_thread(
        gemini_client.models.generate_content,
        model='gemini-1.5-flash',
        contents=full_prompt
    )
    return response.text

# 👑 DIRECT FIX: Fallback template ko f-string se dynamic banao
def call_static_template(prompt: str, user_name: str, user_location: str) -> str:
    """Tertiary Engine: Hardcoded system failure template."""
    return (
        f"Subject: Application under RTI Act 2005.\n\n"
        f"Dear Public Information Officer,\n"
        f"Jurisdiction: Office of {user_location}\n\n"
        f"Please provide certified copies of records, budget allocations, and execution timelines regarding the following issue:\n"
        f"\"{prompt}\"\n\n"
        f"Please provide the information within 30 days as mandated by the Act.\n\n"
        f"Sincerely,\n"
        f"Name: {user_name}\n"
        f"Location: {user_location}"
    )
async def draft_with_retry_loop(prompt: str, user_name: str, user_location: str, provider_func) -> str:
    """
    The Agentic Loop: Draft -> Critic -> Rewrite
    Maximum 3 attempts to pass the quality check.
    """
    current_prompt = prompt
    
    for attempt in range(3):
        # 1. Draft
        draft = await provider_func(current_prompt, user_name, user_location)
        
        # 2. Critic Node Evaluation
        validation_result = validate_rti_output(draft)
        
        # 3. Decision
        if validation_result.passed:
            return draft # Perfect draft, exit the loop
            
        # If failed, create a feedback loop for the LLM
        issues_text = ", ".join(validation_result.issues)
        current_prompt = f"Your previous draft was rejected for these reasons: {issues_text}. Rewrite it to fix these errors. Original problem: {prompt}"
        
    # If it fails 3 times, return the best effort rather than crashing
    return draft

async def generate_rti_pipeline(user_query: str, user_name: str, user_location: str):
    """The Orchestrator: Routes traffic and handles complete failures."""
    providers = [
        ("Groq", call_groq),
        ("Gemini", call_gemini),
    ]

    for name, provider_func in providers:
        try:
            # 15-second fuse. If the API hangs, it cuts off and moves to the next.
            result = await asyncio.wait_for(
            draft_with_retry_loop(user_query, user_name, user_location, provider_func), 
            timeout=15.0
        )
            return result
        except Exception as e:
            print(f"[{name}] Engine failed or timed out: {e}. Switching to fallback...")
            continue
            
    # If all AI providers crash, lose internet, or run out of credits
    print("[System] All AI engines failed. Deploying static template.")
    return call_static_template(user_query, user_name, user_location)