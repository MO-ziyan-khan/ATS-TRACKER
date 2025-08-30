import os
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import google.generativeai as genai

# ------------------ CONFIG ------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("❌ GOOGLE API Key not found! Please add it to your .env file.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# ------------------ HELPERS ------------------
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        if not text.strip():
            raise ValueError("No extractable text found in PDF.")
        return text
    except Exception as e:
        st.error(f"❌ Error reading PDF: {e}")
        return None

def get_gemini_response(job_desc, resume_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content([job_desc, resume_text, prompt])
        return response.text
    except Exception as e:
        st.error(f"❌ GOOGLE API error: {e}")
        return "Error getting response from Gemini API."

# ------------------ UI ------------------
st.set_page_config(page_title="ATS Companion", page_icon=":robot_face:", layout="wide")
st.header("ATS Companion")

job_desc = st.text_area("Job Description", height=100)
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

submit1 = st.button("Tell me about the Resume")
submit2 = st.button("How Can I Improve My Resume?")
submit3 = st.button("What are the keywords missing in my Resume?")
submit4 = st.button("Percentage match")

# ------------------ PROMPTS ------------------
prompt_summary = """
You are an experienced HR with 10+ years in Data Science, AI, ML, Fullstack, Web Dev, Big Data, and DevOps.
Review the resume and provide a detailed summary of qualifications, skills, and experiences.
Highlight strengths and unique aspects.
"""

prompt_improve = """
You are an experienced HR with 10+ years in tech recruitment.
Suggest improvements to make the resume more effective.
Focus on clarity, relevance, formatting, key skills, and alignment with the job description.
Give actionable bullet points.
"""

prompt_keywords = """
You are an ATS system expert.
Analyze the resume against the job description and identify missing keywords.
Provide percentage match first, then list missing keywords in bullet points.
"""

# ------------------ ACTIONS ------------------
if uploaded_file and (submit1 or submit2 or submit3 or submit4):
    resume_text = extract_text_from_pdf(uploaded_file)
    if resume_text:
        if submit1:
            response = get_gemini_response(job_desc, resume_text, prompt_summary)
        elif submit2:
            response = get_gemini_response(job_desc, resume_text, prompt_improve)
        elif submit3 or submit4:
            response = get_gemini_response(job_desc, resume_text, prompt_keywords)
        st.markdown("### ✅ Result")
        st.write(response)
