# ==========================================
# STEP 1: MANDATORY IMPORTS FOR PDF CREATION
# ==========================================
import os
import re
from fpdf import FPDF

def clean_llm_text(text: str) -> str:
    """LLM text se duplicate headers aur salutations saaf karta hai."""
    lines = text.split('\n')
    cleaned_lines = []
    skip_keywords = [
        "application under", "to,", "the public information", "the central public",
        "dear sir", "respected sir", "sir/madam", "subject:", "reference:",
        "sincerely", "yours faithfully", "abhishek tiwari", "varanasi", "declarations:"
    ]
    in_queries = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r'^(\d+\.|\*|\-)', stripped) or "details of" in stripped.lower() or "request you to provide" in stripped.lower():
            in_queries = True
        should_skip = any(kw in stripped.lower() for kw in skip_keywords)
        if "1. i state that" in stripped.lower() or "2. i hereby declare" in stripped.lower():
            break
        if in_queries and not should_skip:
            cleaned_lines.append(stripped)
    if not cleaned_lines:
        return text
    return "\n\n".join(cleaned_lines)

def create_rti_pdf(rti_text: str, ministry_name: str, user_name: str, user_location: str, file_name: str = "RTI_Application.pdf") -> str:
    """Generates a legally formatted PDF with bulletproof structural alignment."""
    
    final_queries_text = clean_llm_text(rti_text)
    
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    
    # Set standard margins
    pdf.set_margins(left=20, top=20, right=20)
    pdf.set_auto_page_break(auto=True, margin=20)
    
    content_width = 170
    
    font_path = os.path.join("assets", "fonts", "NotoSansDevanagari-Regular.ttf")
    pdf.add_font("DevaFont", style="", fname=font_path, uni=True)
    
    # Header Title
    pdf.set_font("DevaFont", size=14)
    pdf.cell(w=content_width, h=10, txt="APPLICATION UNDER SECTION 6(1) OF THE RTI ACT, 2005", ln=1, align="C")
    
    pdf.set_line_width(0.5)
    pdf.line(x1=20, y1=32, x2=190, y2=32)
    pdf.ln(12)

    # 🏢 FORMAL SECTION 1: To The PIO Details (👑 FIXED HEADER ALIGNMENT)
    pdf.set_font("DevaFont", size=11)
    
    pdf.set_x(20)
    pdf.cell(w=content_width, h=6, txt="To,", ln=1)
    
    pdf.set_x(20)
    pdf.cell(w=content_width, h=6, txt="The Central Public Information Officer (CPIO),", ln=1)
    
    pdf.set_x(20)
    pdf.multi_cell(w=content_width, h=6, txt=str(ministry_name))
    
    pdf.set_x(20)
    pdf.cell(w=content_width, h=6, txt="Government of India,", ln=1)
    
    pdf.set_x(20)
    pdf.cell(w=content_width, h=6, txt=f"New Delhi (Jurisdiction Area: {user_location})", ln=1)
    pdf.ln(6)
    
    # 📋 FORMAL SECTION 2: Dynamic Subject & Reference Box
    subject_str = f"SUBJECT: Request for Information under Section 6(1) of the RTI Act, 2005 regarding public utilities at {user_location}."
    reference_str = f"REFERENCE: Core issue evaluated and matched under {ministry_name} portal guidelines."
    
    sub_lines = len(pdf.multi_cell(w=160, h=5, txt=subject_str, split_only=True))
    ref_lines = len(pdf.multi_cell(w=160, h=5, txt=reference_str, split_only=True))
    box_height = ((sub_lines + ref_lines) * 5) + 8
    
    start_box_y = pdf.get_y()
    pdf.set_draw_color(71, 85, 105)
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(x=20, y=start_box_y, w=170, h=box_height, style="DF")
    
    pdf.set_y(start_box_y + 3)
    pdf.set_x(25)
    pdf.multi_cell(w=160, h=5, txt=subject_str)
    pdf.set_x(25)
    pdf.multi_cell(w=160, h=5, txt=reference_str)
    
    pdf.set_y(start_box_y + box_height)
    pdf.ln(8)
    
    # ✍️ FORMAL SECTION 3: Standard Respectful Salutation
    pdf.set_x(20)
    pdf.cell(w=content_width, h=6, txt="Respected Sir / Madam,", ln=1)
    pdf.ln(2)
    
    pdf.set_x(20)
    intro_text = f"I, {user_name}, a bona fide citizen of India, hereby seek the following information under Section 6(1) of the Right to Information Act, 2005. The specific details of required information are structured below:"
    pdf.multi_cell(w=content_width, h=6, txt=intro_text) 
    pdf.ln(4)
    
    # 🧠 FORMAL SECTION 4: Cleaned Core Queries Section
    pdf.set_x(20)
    pdf.multi_cell(w=content_width, h=6, txt=final_queries_text) 
    pdf.ln(6)
    
    # 🤝 FORMAL SECTION 5: Declarations
    pdf.set_x(20)
    pdf.cell(w=content_width, h=6, txt="DECLARATIONS:", ln=1)
    
    pdf.set_x(20)
    pdf.multi_cell(w=content_width, h=6, txt="1. I state that the information demanded above pertains to your esteemed office and falls within your functional jurisdiction.")
    pdf.ln(1)
    
    pdf.set_x(20)
    pdf.multi_cell(w=content_width, h=6, txt="2. I hereby declare that I am a bona fide citizen of India and eligible to seek information under the RTI Act, 2005.")
    pdf.ln(10) 
    
    # ✒️ FORMAL SECTION 6: Signature Block (👑 FIXED RIGHT ALIGNMENT LOOP)
    box_x = 110
    box_width = 80
    
    
    # ✒️ FORMAL SECTION 6: Signature Block (👑 CRASH-FIXED TO PERFECT LEFT ALIGNMENT)
    pdf.set_x(20) # 👑 Standard extreme left margin par lock kiya
    pdf.cell(w=content_width, h=6, txt="Yours faithfully,", ln=1)
    
    # Custom vertical line spacing without breaking X-axis cursor
    pdf.set_y(pdf.get_y() + 12) 
    
    # Saari details ko standard content_width ke sath left-aligned print kiya
    # pdf.set_x(20)
    # pdf.cell(w=content_width, h=6, txt="Signature: ___________________", ln=1)
    
    pdf.set_x(20)
    pdf.cell(w=content_width, h=6, txt=f"Name: {user_name}", ln=1)
    
    pdf.set_x(20)
    pdf.cell(w=content_width, h=6, txt=f"Address: {user_location}", ln=1)
    
    pdf.set_x(20)
    pdf.cell(w=content_width, h=6, txt="Date: May 21, 2026", ln=1)
    
    # 7. Output Management
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
        
    output_path = os.path.join("outputs", file_name)
    pdf.output(output_path)
    
    return output_path