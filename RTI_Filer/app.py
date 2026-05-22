from dotenv import load_dotenv
import os

# Yeh line project root se .env file ko dhoondh kar system me load kar degi
load_dotenv(encoding="utf-8-sig")


import streamlit as st
import asyncio
import psycopg2
from core.validator import validate_rti_input
from core.fallback import generate_rti_pipeline
from core.classifier import classify_issue
from core.pdf_gen import create_rti_pdf


def save_to_database(user_query, detected_ministry, legal_draft):
    """PostgreSQL database mein data insert karne ka core logic"""
    conn = None
    try:
        # pg_hba.conf mein 'trust' set kiya tha, isiliye bina password ke connect hoga
        conn = psycopg2.connect(
            host="localhost",
            database="rti_db",
            user="postgres",
            port="5432"
        )
        cursor = conn.cursor()
        
        # SQL Injection se bachne ke liye %s placeholders use kiye hain
        insert_query = """
        INSERT INTO rti_applications (raw_problem, detected_ministry, final_draft) 
        VALUES (%s, %s, %s);
        """
        cursor.execute(insert_query, (user_query, detected_ministry, legal_draft))
        
        conn.commit()  # Data ko disk par permanently save karne ke liye
        cursor.close()
        return True
    except Exception as e:
        st.warning(f"⚠️ DB Logging Failed: {str(e)}")
        return False
    finally:
        if conn is not None:
            conn.close() # Connection open mat chhorna, resources leak ho jaate hain


# 1. UI Configuration
st.set_page_config(page_title="RTI Auto-Filer MVP", page_icon="⚖️")
st.title("⚖️ Agentic RTI Auto-Filer (MVP)")
st.subheader("Enter your issue, and the AI will draft a legal RTI application.")

# 2. THE ORIGIN OF THE PROMPT
# Here is where the "prompt" comes from. The user types it into this text box.
user_input = st.text_area(
    "Describe your problem in detail (Min 20 characters):", 
    placeholder="Example: The road construction in my village was abandoned 6 months ago..."
)


# --- NAYE PROFILE INPUTS ---
col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input("Your Full Name:", placeholder="e.g., Amit Kumar")
with col2:
    user_location = st.text_input("Your District & State:", placeholder="e.g., Surat, Gujarat")

# 3. The Execution Trigger
if st.button("Generate RTI PDF"):
    
    # Step A: Pass the user input to Checkpost 1 (Ingress Validator)
    input_check = validate_rti_input(user_input)
    
    if not input_check.valid:
        # If input is garbage, stop and show the error hint to the user
        st.error(input_check.hint)
    else:
        # Step B: If input is valid, proceed to the Agentic Engine
        with st.spinner("Agentic AI processing... (Drafting -> Validating -> Retrying if needed)"):
            try:

                detected_dept = classify_issue(input_check.sanitized_text)

                # Screen par user ko dikhao ki system ne kaun si ministry dhoondhi
                st.info(f"Target Ministry Detected: {detected_dept['ministry']}")


                # THIS IS THE CONNECTION POINT
                # We pass the clean, sanitized text into our fallback.py engine
                final_draft = asyncio.run(generate_rti_pipeline(input_check.sanitized_text, user_name, user_location))
                
                st.success("RTI Draft Generated Successfully!")
                

                # Show the final generated text on the screen
                st.text_area("Final Legal Draft:", value=final_draft, height=300)
                
                pdf_file_path = create_rti_pdf(
                    rti_text=final_draft, 
                    ministry_name=detected_dept['ministry'],
                    user_name=user_name,
                    user_location=user_location,
                    file_name="RTI_Application.pdf"
                )
                
                db_status = save_to_database(
                    user_query=input_check.sanitized_text,
                    detected_ministry=detected_dept['ministry'],
                    legal_draft=final_draft
                )

                if db_status:
                    st.caption("💾 Record successfully backed up in PostgreSQL Database.")

                # Provide a button to download the raw text (PDF generation comes next)
                with open(pdf_file_path, "rb") as pdf_file:
                    st.download_button(
                        label="📥 Download Official RTI PDF",
                        data=pdf_file,
                        file_name="RTI_Application.pdf",
                        mime="application/pdf"
                    )
                
            except Exception as e:
                st.error(f"System Error: {str(e)}")