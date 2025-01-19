import streamlit as st
import openai
from main_functions import analyze_resume_and_job, generate_full_resume, generate_cover_letter, create_pdf
from PIL import Image
import os
import tempfile

# Set up OpenAI API key before importing main_functions.py
openai.api_key = st.secrets.get("openai_api_key")

# Verify API key is set
if not openai.api_key:
    st.error("OpenAI API key is missing. Please set it in Streamlit secrets.")
    st.stop()

st.set_page_config(page_title="AI Resume Tailor 2", page_icon="📄", layout="wide")

# Initialize session state
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None

def sanitize_for_pdf(text):
    return ''.join(char for char in text if ord(char) < 128)

# Header Section
st.title("AI Resume Tailor 2")

st.markdown("Optimize your resume and cover letter to pass Applicant Tracking Systems (ATS) with ease.")

# File Uploads for Resume and Job Description
st.subheader("Upload Your Documents")
col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader("Upload Your Resume (PDF or TXT)", type=["pdf", "txt"], key="resume_upload")
    
with col2:
    job_desc_file = st.file_uploader("Upload Job Description (PDF or TXT)", type=["pdf", "txt"], key="jobdesc_upload")

def read_file(file):
    if file is not None:
        if file.type == "application/pdf":
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        else:
            return file.getvalue().decode("utf-8")
    return ""

def generate_resume():
    resume_text = read_file(resume_file)
    job_description_text = read_file(job_desc_file)
    
    if resume_text and job_description_text:
        try:
            with st.spinner("Analyzing and tailoring your resume..."):
                header, summary, education, work_experience, cover_letter_info = analyze_resume_and_job(resume_text, job_description_text)
                company_name = cover_letter_info.get('Company Name', 'Company')
                full_resume = generate_full_resume(header, summary, education, work_experience, company_name)
                cover_letter = generate_cover_letter(resume_text, job_description_text, cover_letter_info)
                
                st.session_state.resume_data = {
                    'header': header,
                    'summary': summary,
                    'education': education,
                    'work_experience': work_experience,
                    'full_resume': full_resume,
                    'cover_letter': cover_letter
                }
                st.session_state.generated = True
        except Exception as e:
            st.error(f"An error occurred during generation: {str(e)}")
    else:
        st.warning("Please upload both your resume and the job description.")

if st.button("Analyze and Tailor Resume"):
    generate_resume()

if st.session_state.generated:
    data = st.session_state.resume_data
    
    st.markdown("---")
    st.subheader("Tailored Header")
    st.info(data['header'])
    
    st.subheader("Custom Summary")
    st.success(data['summary'])
    
    st.subheader("Education")
    st.write(data['education'])
    
    st.subheader("Relevant Work Experience")
    for exp in data['work_experience']:
        st.write(exp)
    
    st.subheader("Complete Tailored Resume")
    st.text_area("Copy and edit your tailored resume:", data['full_resume'], height=400)
    st.info("Please review and edit the generated resume to ensure all information is accurate and fits on one page. You may need to adjust the work experience and education sections.")
    
    st.subheader("Cover Letter")
    st.text_area("Copy your cover letter:", data['cover_letter'], height=300)

    # Generate PDF downloads
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            resume_pdf_path = os.path.join(tmpdirname, "tailored_resume.pdf")
            cover_letter_pdf_path = os.path.join(tmpdirname, "cover_letter.pdf")
            
            create_pdf(sanitize_for_pdf(data['full_resume']), resume_pdf_path)
            create_pdf(sanitize_for_pdf(data['cover_letter']), cover_letter_pdf_path)

            # Read the PDF files
            with open(resume_pdf_path, "rb") as pdf_file:
                resume_pdf = pdf_file.read()
            with open(cover_letter_pdf_path, "rb") as pdf_file:
                cover_letter_pdf = pdf_file.read()

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download Resume as PDF",
                    data=resume_pdf,
                    file_name="tailored_resume.pdf",
                    mime='application/pdf'
                )
            
            with col2:
                st.download_button(
                    label="Download Cover Letter as PDF",
                    data=cover_letter_pdf,
                    file_name="cover_letter.pdf",
                    mime='application/pdf'
                )
    except Exception as e:
        st.error(f"An error occurred while creating PDFs: {str(e)}")

if st.button("Start Over"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and OpenAI GPT-4")
