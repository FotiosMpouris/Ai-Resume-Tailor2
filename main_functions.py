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
        # No header
        pass

    def footer(self):
        # No footer
        pass

    def chapter_title(self, title):
        # Add chapter title
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 6, title, ln=True)
        self.ln(4)

def create_pdf(content, filename_or_buffer):
    # Initialize PDF with Letter format
    pdf = PDF(format='Letter')
    pdf.add_page()

    # Add Unicode fonts
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)

    # Set margins (1 inch = 25.4 mm)
    margin = 25.4
    pdf.set_margins(margin, margin, margin)
    pdf.set_auto_page_break(auto=True, margin=margin)

    # Determine if this is a cover letter or resume
    if isinstance(filename_or_buffer, str):
        is_cover_letter = filename_or_buffer == "cover_letter.pdf"
    else:
        is_cover_letter = False

    if is_cover_letter:
        # Cover Letter Formatting
        # Contact Information
        pdf.set_font('DejaVu', '', 11)
        paragraphs = content.split('\n\n')
        
        # Header (contact info)
        contact_lines = paragraphs[0].split('\n')
        for line in contact_lines:
            pdf.cell(0, 5, line.strip(), ln=True)
        pdf.ln(10)

        # Date and Address
        date_section = paragraphs[1].split('\n')
        pdf.cell(0, 5, date_section[0], align='L', ln=True)  # Date
        pdf.ln(10)
        
        # Salutation
        if len(date_section) > 1:
            pdf.cell(0, 5, date_section[1], ln=True)  # Salutation
            pdf.ln(5)

        # Body Paragraphs
        pdf.set_font('DejaVu', '', 11)
        for paragraph in paragraphs[2:-1]:  # Exclude the last paragraph (signature)
            pdf.multi_cell(0, 5, paragraph.strip(), align='J')
            pdf.ln(5)

        # Signature
        pdf.ln(5)
        signature_lines = paragraphs[-1].split('\n')
        for line in signature_lines:
            pdf.cell(0, 5, line.strip(), ln=True)

    else:
        # Resume Formatting
        sections = content.split('\n\n')
        
        # Header Section (Name and Contact Info)
        pdf.set_font('DejaVu', 'B', 14)
        header_lines = sections[0].split('\n')
        
        # Name on first line, centered
        name = header_lines[0].split(': ')[-1]
        pdf.cell(0, 8, name, align='C', ln=True)
        
        # Contact info on second line, centered smaller
        pdf.set_font('DejaVu', '', 10)
        contact_info = []
        for line in header_lines[1:]:
            if ': ' in line:
                contact_info.append(line.split(': ')[-1])
        pdf.cell(0, 5, ' | '.join(contact_info), align='C', ln=True)
        
        pdf.ln(5)
        pdf.line(margin, pdf.get_y(), pdf.w - margin, pdf.get_y())
        pdf.ln(5)

        # Process remaining sections
        for section in sections[1:]:
            if section.startswith('SUMMARY'):
                pdf.set_font('DejaVu', 'B', 12)
                pdf.cell(0, 6, 'PROFESSIONAL SUMMARY', ln=True)
                pdf.set_font('DejaVu', '', 11)
                pdf.ln(2)
                pdf.multi_cell(0, 5, section.split('\n', 1)[1].strip(), align='J')
                pdf.ln(5)

            elif section.startswith('EDUCATION'):
                pdf.set_font('DejaVu', 'B', 12)
                pdf.cell(0, 6, 'EDUCATION', ln=True)
                pdf.set_font('DejaVu', '', 11)
                pdf.ln(2)
                education_content = section.split('\n', 1)[1].strip()
                for edu in education_content.split('\n'):
                    if edu.strip():
                        pdf.multi_cell(0, 5, edu.strip(), align='L')
                pdf.ln(5)

            elif section.startswith('RELEVANT WORK EXPERIENCE'):
                pdf.set_font('DejaVu', 'B', 12)
                pdf.cell(0, 6, 'PROFESSIONAL EXPERIENCE', ln=True)
                pdf.set_font('DejaVu', '', 11)
                pdf.ln(2)
                experiences = section.split('\n', 1)[1].strip().split('\n\n')
                for i, exp in enumerate(experiences):
                    lines = exp.strip().split('\n')
                    if lines:
                        # Title/Company line in bold
                        pdf.set_font('DejaVu', 'B', 11)
                        pdf.multi_cell(0, 5, lines[0], align='L')
                        pdf.set_font('DejaVu', '', 11)
                        
                        # Dates/Location on next line
                        if len(lines) > 1:
                            pdf.multi_cell(0, 5, lines[1], align='L')
                        
                        # Description points
                        for line in lines[2:]:
                            if line.strip():
                                pdf.set_x(margin + 5)  # Indent bullet points
                                pdf.multi_cell(0, 5, '• ' + line.strip(), align='L')
                    if i < len(experiences) - 1:
                        pdf.ln(3)

    # Handle output
    if isinstance(filename_or_buffer, io.BytesIO):
        pdf_str = pdf.output(dest='S').encode('latin1')
        filename_or_buffer.write(pdf_str)
    else:
        pdf.output(filename_or_buffer)
