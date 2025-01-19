import streamlit as st
import openai
from PIL import Image
from main_functions import analyze_resume_and_job, generate_full_resume, generate_cover_letter, create_pdf
import os
import io

# Set up OpenAI API key before importing main_functions.py
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

# File uploaders for Resume and Job Description
uploaded_resume = st.file_uploader("Upload your Resume (PDF or TXT)", type=["pdf", "txt"], key="resume_upload")
uploaded_job = st.file_uploader("Upload the Job Description (PDF or TXT)", type=["pdf", "txt"], key="job_upload")

def read_file(file):
    if file is None:
        return ""
    try:
        if file.type == "application/pdf":
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        elif file.type == "text/plain":
            return file.read().decode("utf-8")
        else:
            st.warning("Unsupported file type. Please upload a PDF or TXT file.")
            return ""
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return ""

resume = read_file(uploaded_resume)
job_description = read_file(uploaded_job)

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
    st.write(data['work_experience'])
    
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
            # Create PDFs in memory to avoid filesystem issues on Streamlit Cloud
            resume_pdf_buffer = io.BytesIO()
            cover_letter_pdf_buffer = io.BytesIO()
            
            # Generate Resume PDF
            create_pdf(sanitize_for_pdf(data['full_resume']), resume_pdf_buffer)
            resume_pdf_buffer.seek(0)
            
            # Generate Cover Letter PDF
            create_pdf(sanitize_for_pdf(data['cover_letter']), cover_letter_pdf_buffer)
            cover_letter_pdf_buffer.seek(0)

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download Resume as PDF",
                    data=resume_pdf_buffer,
                    file_name="tailored_resume.pdf",
                    mime='application/pdf'
                )
            
            with col2:
                st.download_button(
                    label="Download Cover Letter as PDF",
                    data=cover_letter_pdf_buffer,
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
