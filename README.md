# 🏛️ Automated Civic Filing Suite (RTI Filer)

## 📌 About the Project
An asynchronous, fault-tolerant automated legal lifecycle suite designed to eliminate bureaucratic friction. I researched official data from the Central Information Commission (CIC) and independent legal studies, confirming that while thousands of applications are filed monthly, a massive chunk gets trapped in bureaucratic loops, facing rejection or infinite delays simply due to wrong ministry routing and structural formatting errors. 

To eliminate this bureaucratic friction, this automated filing suite allows users to describe their civic issue in plain, conversational language (Hindi/Hinglish). The system completely automates the legal lifecycle—dynamically routing the grievance to the correct central ministry, structuring the legal text, and compiling a pixel-perfect, compliance-ready PDF petition in real-time.

---

## 🗺️ System Architecture & Workflow

The platform handles unpredictable human language data by separating the data intake, routing logic, content generation, and document compilation into isolated layers.

```text
               +-------------------------------------------+
               |        Angular 17 Responsive UI          |
               +---------------------+---------------------+
                                     | (Async Data Stream)
                                     v
               +-------------------------------------------+
               |  FastAPI Perimeter + Pydantic Type-Safety |
               +---------------------+---------------------+
                                     |
                                     v
               +-------------------------------------------+
               | Intent Routing Subsystem (Regex Registry) |
               +---------------------+---------------------+
                                     |
                  +------------------+------------------+
                  | (Primary API Up)                    | (Upstream Exception / Timeout)
                  v                                     v
+-----------------------------------+   +-----------------------------------+
|  LLM Generation (Gemini / Groq)   |   |   Resilient Fallback Engine       |
|  Strict Structural Constraints     |   |   (Local Cached Template Maps)    |
+-----------------+-----------------+   +-----------------+-----------------+
                  |                                     |
                  +------------------+------------------+
                                     |
                                     v
               +-------------------------------------------+
               |  Layout Synthesis Layer (FPDF Document)   |
               +---------------------+---------------------+
                                     | (PDF Written / State Sync)
                                     v
               +-------------------------------------------+
               |    Angular Viewports (Live UI Re-render)  |
               +-------------------------------------------+


⚙️ Local Installation & Environment Setup🐍
 1. Backend Engine Setup & Run (FastAPI)Navigate directly to the service subfolder from your terminal root:Bashcd RTI_Filer/RTI_Filer
Instantiate and activate the virtual sandbox environment:Bash# On Windows Systems:

venv\Scripts\activate

# On macOS or Linux Systems:

source venv/bin/activate

Install the required production dependencies:Bashpython -m pip install --upgrade pip

python -m pip install -r requirements.txt

Create a .env deployment configuration file in the RTI_Filer/RTI_Filer root folder:Code snippetGEMINI_API_KEY=your_production_gemini_token_here
GROQ_API_KEY=your_production_groq_token_here
DATABASE_URL=postgresql://db_user:db_password@localhost:5432/rti_db
Launch the high-concurrency development ASGI server:Bash# Fixes potential 'charmap' string decoding failures on Windows devices
set PYTHONUTF8=1

uvicorn main:app --reload
Default Backend URL: http://127.0.0.1:8000Interactive API Playground (Swagger Spec): http://127.0.0.1:8000/docs🌐 2. Client Application Setup & Run (Angular 17)Open a parallel bash interface terminal window and route to the view segment directory:Bashcd rti-frontend
Trigger node package fetching to pull client-side tracking scripts:Bashnpm install
Configure the application context to point to your live local FastAPI pipeline instance inside src/environments/environment.ts:TypeScriptexport const environment = {
  production: false,
  apiUrl: '[http://127.0.0.1:8000](http://127.0.0.1:8000)'
};
Boot up the Angular compilation server to stream responsive views:Bashng serve
Local Web Interface Server Endpoint: http://localhost:4200/🛡️ Production Hardening & Failover EngineeringPlaintext[User Request] ---> [FastAPI] ---> [LLM API Request] ---X (Timeout/Rate-Limit)
                                         |
                                         v (Catch Exception)
                               [fallback.py Engine]
                                         |
                                         v
                         [Local Token Injection Matrix]
                                         |
                                         v
                       [Pristine PDF Document Synthesized]

📥 1. Sample Input Payload (POST /api/v1/generate-rti)
Copy this JSON block directly into your frontend client tool or Swagger UI (/docs):

JSON
{
  "user_name": "Aman Kumar",
  "user_location": "Noida, Uttar Pradesh",
  "problem_statement": "Mere area me pichle 3 mahine se naya 5G tower install hone ki wajah se broadband cables baar-baar cut ho rhi hain. Iski wajah se internet connectivity zero ho chuki hai aur online education completely disrupted hai. Local workers call ignore kar rahe hain, please help."
}

🎯 2. Expected System Processing Behavior
Language Detection: langdetect flags the string as mixed Hindi/English (Hinglish).

Intent Routing Match: The classifier.py token matcher extracts keywords like 5G tower, broadband, internet connectivity and dynamically routes the complaint to:
👉 Ministry of Communications (Department of Telecommunications)

📤 3. Expected Structured JSON Response

JSON
{
  "status": "success",
  "meta": {
    "routed_ministry": "Ministry of Communications",
    "department": "Department of Telecommunications",
    "execution_mode": "PRIMARY_LLM_PIPELINE"
  },
  "legal_draft": {
    "subject": "Urgent intervention required regarding persistent broadband infrastructure damage due to unauthorized 5G tower construction coordinates in Noida.",
    "body_paragraphs": [
      "The applicant, Aman Kumar, residing at Noida, Uttar Pradesh, brings to your immediate notice the continuous disruptions of telecom services due to ongoing installation workflows.",
      "Key telemetry indicators suggest local field operatives are bypassing safety guidelines, leading to extensive cable fractures."
    ]
  },
  "pdf_url": "/outputs/RTI_Petition_Aman_Kumar_171655.pdf"
}


The application adheres strictly to a Zero-Trust Third-Party API Strategy. If network drops occur or upstream server limits expire mid-flight during text compilation:main.py intercepts the standard HTTP connection exception block safely.The pipeline execution hands state control parameters cleanly over to core/fallback.py.The offline template engine processes variables natively using predefined legal structures matching the routed ministry target.A verified compliant document is compiled and downloaded, guaranteeing no service disruption to the citizen.📝 LicenseDistributed under the MIT License. See LICENSE for more structural information.