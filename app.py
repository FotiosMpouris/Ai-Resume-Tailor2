# app.py

import streamlit as st
import openai
from PIL import Image
from main_functions import analyze_resume_and_job, generate_full_resume, generate_cover_letter, create_pdf
import os

# Set up OpenAI API key from Streamlit secrets
openai.api_key = st.secrets.get("openai_api_key")

# Verify API key is set
if not openai.api_key:
    st.error("OpenAI API key is missing. Please set it in Streamlit secrets.")
    st.stop()

st.set_page_config(page_title="AI Resume Tailor 2", page_icon="📄", layout="wide")

# Load and display the logo alongside the title
col1, col2 = st.columns([1, 12])
with col1:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=100)
    except FileNotFoundError:
        st.warning("Logo file not found. Please ensure 'logo.png' is in the correct directory.")
with col2:
    st.title("AI Resume Tailor 2")

# Initialize session state
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None

def sanitize_for_pdf(text):
    return ''.join(char for char in text if ord(char) < 128)

# File uploaders for resume and job description
st.subheader("Upload Your Documents")

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload your Resume (PDF or TXT)", type=["pdf", "txt"], key="resume")
with col2:
    job_desc_file = st.file_uploader("Upload Job Description (PDF or TXT)", type=["pdf", "txt"], key="job_desc")

def read_file(file):
    if file is not None:
        try:
            if file.type == "application/pdf":
                import PyPDF2
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
            else:
                return file.getvalue().decode("utf-8")
        except Exception as e:
            st.error(f"Error reading {file.name}: {str(e)}")
            return ""
    return ""

resume = read_file(resume_file)
job_description = read_file(job_desc_file)

def generate_resume():
    if resume and job_description:
        try:
            with st.spinner("Analyzing and tailoring your resume..."):
                header, summary, education, work_experience, cover_letter_info = analyze_resume_and_job(resume, job_description)
                company_name = cover_letter_info.get('Company Name', 'Company')
                full_resume = generate_full_resume(header, summary, education, work_experience, company_name)
                cover_letter = generate_cover_letter(resume, job_description, cover_letter_info)
                
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
    
    st.subheader("Tailored Header")
    st.info(data['header'])
    
    st.subheader("Custom Summary")
    st.success(data['summary'])
    
    st.subheader("Education")
    st.write(data['education'])
    
    st.subheader("Relevant Work Experience")
    for idx, exp in enumerate(data['work_experience'], 1):
        st.write(f"**{idx}.** {exp}")
    
    st.subheader("Complete Tailored Resume")
    st.text_area("Copy and edit your tailored resume:", data['full_resume'], height=400)
    st.info("Please review and edit the generated resume to ensure all information is accurate and fits on one page. You may need to adjust the work experience and education sections.")
    
    st.subheader("Cover Letter")
    st.text_area("Copy your cover letter:", data['cover_letter'], height=300)

    # Generate PDF downloads
    try:
        # Check if PDF fonts are available
        if not (os.path.exists("DejaVuSansCondensed.ttf") and os.path.exists("DejaVuSansCondensed-Bold.ttf")):
            st.warning("Font files missing. Please ensure 'DejaVuSansCondensed.ttf' and 'DejaVuSansCondensed-Bold.ttf' are present.")
        else:
            create_pdf(sanitize_for_pdf(data['full_resume']), "tailored_resume.pdf")
            create_pdf(sanitize_for_pdf(data['cover_letter']), "cover_letter.pdf")

            # Check if PDFs were created
            if os.path.exists("tailored_resume.pdf") and os.path.exists("cover_letter.pdf"):
                col1, col2 = st.columns(2)
                with col1:
                    with open("tailored_resume.pdf", "rb") as pdf_file:
                        PDFbyte = pdf_file.read()
                    st.download_button(label="Download Resume as PDF",
                                       data=PDFbyte,
                                       file_name="tailored_resume.pdf",
                                       mime='application/pdf')
                
                with col2:
                    with open("cover_letter.pdf", "rb") as pdf_file:
                        PDFbyte = pdf_file.read()
                    st.download_button(label="Download Cover Letter as PDF",
                                       data=PDFbyte,
                                       file_name="cover_letter.pdf",
                                       mime='application/pdf')
            else:
                st.error("Failed to create PDF files.")
    except Exception as e:
        st.error(f"An error occurred while creating PDFs: {str(e)}")

if st.button("Start Over"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and OpenAI GPT-4")
