import openai
import re
from fpdf import FPDF
from datetime import date
import io  # Ensure io is imported

def analyze_resume_and_job(resume, job_description):
    system_message = """
    You are an expert resume analyst and career advisor with decades of experience in HR and recruitment across various industries. Your task is to analyze the provided resume and job description, then provide:
    1. A tailored header for the resume, including the candidate's name and key contact information.
    2. A custom summary (3-4 sentences) that highlights the candidate's most relevant skills and experiences for this specific job.
    3. Extract and summarize the candidate's education information.
    4. Extract and summarize at least three relevant work experiences for this job, focusing on the most recent or most applicable positions. Each experience should be described in detail.
    5. Extract the full name, address, email, and phone number for use in a cover letter.
    6. Extract the company name from the job description for use in the cover letter greeting.
    """

    user_message = f"""
    Please analyze the following resume and job description:

    Resume:
    {resume}

    Job Description:
    {job_description}

    Provide your analysis in the following format:
    HEADER:
    [Tailored header here]

    SUMMARY:
    [Custom summary here]

    EDUCATION:
    [Summarized education information]

    RELEVANT WORK EXPERIENCE:
    [Summarized relevant work experience 1]

    [Summarized relevant work experience 2]

    [Summarized relevant work experience 3]

    COVER LETTER INFO:
    Full Name: [Extracted full name]
    Address: [Extracted address]
    Email: [Extracted email]
    Phone: [Extracted phone number]
    Company Name: [Extracted company name]
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    output = response.choices[0].message.content
    return process_gpt_output(output)

def process_gpt_output(output):
    sections = re.split(r'\n\n(?=HEADER:|SUMMARY:|EDUCATION:|RELEVANT WORK EXPERIENCE:|COVER LETTER INFO:)', output)

    header = re.sub(r'^HEADER:\s*', '', sections[0], flags=re.MULTILINE).strip()
    summary = re.sub(r'^SUMMARY:\s*', '', sections[1], flags=re.MULTILINE).strip()

    education = re.sub(r'^EDUCATION:\s*', '', sections[2], flags=re.MULTILINE).strip()
    work_experience = re.sub(r'^RELEVANT WORK EXPERIENCE:\s*', '', sections[3], flags=re.MULTILINE).strip()

    cover_letter_info_raw = re.sub(r'^COVER LETTER INFO:\s*', '', sections[4], flags=re.MULTILINE).strip().split('\n')
    cover_letter_info = {item.split(':')[0].strip(): item.split(':')[1].strip() for item in cover_letter_info_raw}

    return header, summary, education, work_experience, cover_letter_info

def generate_full_resume(header, summary, education, work_experience, company_name):
    full_resume = f"""
{header}

SUMMARY
{summary}

EDUCATION
{education}

RELEVANT WORK EXPERIENCE
{work_experience}
"""
    return full_resume

def generate_cover_letter(resume, job_description, cover_letter_info):
    today = date.today().strftime("%B %d, %Y")

    system_message = """
    You are an expert cover letter writer with years of experience in HR and recruitment. Your task is to create a compelling, personalized cover letter based on the candidate's resume, the job description provided, and the specific candidate information given. The cover letter should:
    1. Highlight the candidate's most relevant skills and experiences for the specific job
    2. Show enthusiasm for the position and company
    3. Be concise, typically not exceeding one page
    4. Encourage the employer to review the attached resume and consider the candidate for an interview
    5. Do not include any salutation, contact information, or closing in the body of the letter
    """

    user_message = f"""
    Please write a cover letter based on the following information:

    Candidate Information:
    Full Name: {cover_letter_info['Full Name']}
    Company: {cover_letter_info['Company Name']}

    Resume:
    {resume}

    Job Description:
    {job_description}

    Provide only the body of the cover letter, without any salutation or closing.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    cover_letter_content = response.choices[0].message.content

    # Format the cover letter with the correct header, date, and salutation
    formatted_cover_letter = f"{cover_letter_info['Full Name']}\n{cover_letter_info['Address']}\n{cover_letter_info['Phone']}\n{cover_letter_info['Email']}\n\n{today}\n\nDear {cover_letter_info['Company Name']} Hiring Team,\n\n{cover_letter_content}\n\nSincerely,\n{cover_letter_info['Full Name']}"

    return formatted_cover_letter

class PDF(FPDF):
    def header(self):
        # No header for resume
        pass

    def footer(self):
        # No footer for resume
        pass

    def multi_cell_aligned(self, w, h, txt, border=0, align='J', fill=False, ln=1):
        # Custom method to create a multi-cell with specified alignment
        self.multi_cell(w, h, txt, border, align, fill)
        if ln == 1:
            self.ln(h)
        elif ln == 2:
            self.ln(2*h)

def create_pdf(content, filename_or_buffer):
    pdf = PDF(format='Letter')
    pdf.add_page()

    # Add Unicode fonts (regular and bold)
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)

    if isinstance(filename_or_buffer, str) and filename_or_buffer.endswith(".pdf"):
        # Saving to a file
        filename = filename_or_buffer
        is_cover_letter = filename == "cover_letter.pdf"
    elif isinstance(filename_or_buffer, io.BytesIO):
        # Saving to a buffer
        filename = None
        is_cover_letter = False  # Assuming buffer is for resume
    else:
        filename = None
        is_cover_letter = False

    if is_cover_letter:
        # [Cover Letter Formatting Remains Unchanged]
        ...
    else:
        # Resume specific formatting
        left_margin = 20
        right_margin = 20
        top_margin = 20
        pdf.set_margins(left_margin, top_margin, right_margin)

        pdf.set_auto_page_break(auto=True, margin=15)  # Bottom margin

        # Calculate effective page width (accounting for margins)
        effective_page_width = pdf.w - left_margin - right_margin

        # Split content into main sections
        main_sections = re.split(r'\n\n(?=SUMMARY|EDUCATION|RELEVANT WORK EXPERIENCE)', content)

        # -------------------------
        # Modified Header Section
        # -------------------------
        # Set a smaller font size for the header to ensure it fits on one line
        pdf.set_font("DejaVu", 'B', 12)  # Reduced font size from 14 to 12

        # Combine all header lines into a single line separated by " | " for clarity
        header = main_sections[0].replace('\n', ' | ')

        # Remove "phone:" and "email:" if they exist (optional, based on GPT output)
        header = re.sub(r'\bphone:\b', '', header, flags=re.IGNORECASE)
        header = re.sub(r'\bemail:\b', '', header, flags=re.IGNORECASE)

        # Trim any extra whitespace around separators
        header = re.sub(r'\s*\|\s*', ' | ', header).strip()

        # Add the header as a single centered line
        pdf.cell(0, 7, header, border=0, ln=1, align='C')

        # Add a horizontal line below the header
        pdf.set_line_width(0.5)
        pdf.line(left_margin, pdf.get_y(), pdf.w - right_margin, pdf.get_y())
        pdf.ln(10)  # Spacing after the header

        # -------------------------
        # Process the rest of the sections
        # -------------------------
        pdf.set_font("DejaVu", 'B', 12)  # Consistent font size for section headers
        for section in main_sections[1:]:
            if section.startswith("SUMMARY"):
                pdf.cell(0, 10, "SUMMARY", ln=True, align='L')
                pdf.set_font("DejaVu", '', 11)
                pdf.multi_cell(effective_page_width, 7, section.split('\n', 1)[1].strip(), align='J')
                pdf.set_font("DejaVu", 'B', 12)
            elif section.startswith("EDUCATION"):
                pdf.cell(0, 10, "EDUCATION", ln=True, align='L')
                pdf.set_font("DejaVu", '', 11)
                pdf.multi_cell(effective_page_width, 7, section.split('\n', 1)[1].strip(), align='J')
                pdf.set_font("DejaVu", 'B', 12)
            elif section.startswith("RELEVANT WORK EXPERIENCE"):
                pdf.cell(0, 10, "RELEVANT WORK EXPERIENCE", ln=True, align='L')
                pdf.set_font("DejaVu", '', 11)
                # Split work experiences into individual entries
                experiences = section.split('\n', 1)[1].strip().split('\n\n')
                for exp in experiences:
                    # Add a bullet point
                    pdf.multi_cell(effective_page_width - 10, 7, f"• {exp.strip()}", align='J')
                pdf.set_font("DejaVu", 'B', 12)

            pdf.ln(5)  # Consistent spacing between sections
            pdf.set_line_width(0.2)
            pdf.line(left_margin, pdf.get_y(), pdf.w - right_margin, pdf.get_y())
            pdf.ln(5)

    # Handle PDF Output
    if filename_or_buffer is not None:
        if isinstance(filename_or_buffer, io.BytesIO):
            # Output as string and encode to bytes
            pdf_str = pdf.output(dest='S').encode('latin1')
            filename_or_buffer.write(pdf_str)
        else:
            # Assume it's a filename
            pdf.output(filename_or_buffer)
