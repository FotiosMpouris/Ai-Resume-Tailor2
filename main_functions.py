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
        pass

    def footer(self):
        pass

    def add_page(self, orientation=''):
        super().add_page(orientation=orientation)
        self._current_height = self.t_margin

def create_pdf(content, filename_or_buffer):
    pdf = PDF(format='Letter')
    pdf.add_page()
    
    # Add Unicode fonts
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)

    # Determine if this is a cover letter
    if isinstance(filename_or_buffer, str):
        is_cover_letter = "cover_letter" in filename_or_buffer.lower()
    else:
        is_cover_letter = False

    if is_cover_letter:
        # Cover letter formatting
        margin = 25.4  # 1 inch margins
        pdf.set_margins(margin, margin, margin)
        pdf.set_auto_page_break(auto=True, margin=margin)
        
        # Default font
        pdf.set_font("DejaVu", '', 11)
        
        # Split content into sections
        sections = content.strip().split('\n\n')
        
        # Header (contact info)
        contact_info = sections[0].split('\n')
        for line in contact_info:
            pdf.cell(0, 6, line.strip(), ln=True)
        pdf.ln(6)
        
        # Date
        if len(sections) > 1:
            date_line = sections[1].split('\n')[0]
            pdf.cell(0, 6, date_line.strip(), ln=True)
            pdf.ln(6)
        
        # Recipient/Salutation
        if len(sections) > 2:
            pdf.cell(0, 6, sections[2].strip(), ln=True)
            pdf.ln(6)
        
        # Body paragraphs
        if len(sections) > 3:
            for paragraph in sections[3:-2]:  # Exclude signature
                pdf.multi_cell(0, 6, paragraph.strip(), align='J')
                pdf.ln(6)
        
        # Closing
        if len(sections) > 1:
            pdf.ln(6)
            closing_lines = sections[-2:] if len(sections) >= 2 else [sections[-1]]
            for line in closing_lines:
                pdf.cell(0, 6, line.strip(), ln=True)

    else:
        # Resume formatting
        margin = 20
        pdf.set_margins(margin, margin, margin)
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Process sections
        sections = content.strip().split('\n\n')
        
        # Header section
        pdf.set_font("DejaVu", 'B', 12)
        header_parts = sections[0].split('\n')
        
        # Name and contact centered
        name = header_parts[0].strip()
        pdf.cell(0, 8, name, ln=True, align='C')
        
        # Address and contact info
        pdf.set_font("DejaVu", '', 11)
        for line in header_parts[1:]:
            # Clean up any special characters
            clean_line = line.strip().replace('[]', '').replace('Contact:', '')
            if '|' in clean_line:
                parts = [p.strip() for p in clean_line.split('|')]
                clean_line = ' | '.join(parts)
            pdf.cell(0, 6, clean_line, ln=True, align='C')
        
        pdf.ln(2)
        # Separator line
        pdf.line(margin, pdf.get_y(), pdf.w - margin, pdf.get_y())
        pdf.ln(6)
        
        # Process remaining sections
        for section in sections[1:]:
            if not section.strip():
                continue
                
            # Split into title and content
            parts = section.split('\n', 1)
            if len(parts) < 2:
                continue
                
            title, content = parts
            
            # Section title
            pdf.set_font("DejaVu", 'B', 11)
            pdf.cell(0, 8, title.strip(), ln=True)
            pdf.ln(2)
            
            # Section content
            pdf.set_font("DejaVu", '', 11)
            
            # Process content paragraph by paragraph
            paragraphs = content.strip().split('\n\n')
            for paragraph in paragraphs:
                # Clean up any special characters
                clean_para = paragraph.strip().replace('[]', '')
                pdf.multi_cell(0, 6, clean_para, align='J')
                pdf.ln(3)
            
            pdf.ln(4)
            # Add separator line between sections
            if section != sections[-1]:
                pdf.line(margin, pdf.get_y()-2, pdf.w - margin, pdf.get_y()-2)
                pdf.ln(6)

    # Handle output
    if isinstance(filename_or_buffer, io.BytesIO):
        pdf_str = pdf.output(dest='S').encode('latin1')
        filename_or_buffer.write(pdf_str)
    else:
        pdf.output(filename_or_buffer)
