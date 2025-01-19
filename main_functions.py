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
    
    # Add Unicode fonts
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)

    # Determine if this is a cover letter or resume
    if isinstance(filename_or_buffer, str):
        is_cover_letter = "cover_letter" in filename_or_buffer.lower()
    else:
        is_cover_letter = False

    if is_cover_letter:
        # Cover letter formatting
        margin = 25.4  # 1 inch margins
        pdf.set_margins(margin, margin, margin)
        pdf.set_auto_page_break(auto=True, margin=margin)
        
        # Set default font
        pdf.set_font("DejaVu", '', 11)
        
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        
        # Process header (contact info)
        header_lines = paragraphs[0].split('\n')
        for line in header_lines:
            pdf.cell(0, 6, line.strip(), ln=True, align='L')
        pdf.ln(5)
        
        # Process date and salutation
        if len(paragraphs) > 1:
            date_salutation = paragraphs[1].split('\n')
            pdf.cell(0, 6, date_salutation[0], ln=True, align='L')
            pdf.ln(3)
            if len(date_salutation) > 1:
                pdf.cell(0, 6, date_salutation[1], ln=True, align='L')
        pdf.ln(5)
        
        # Process body paragraphs with proper word wrap
        effective_width = pdf.w - 2*margin
        for paragraph in paragraphs[2:-1]:  # Exclude signature
            words = paragraph.split()
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                if pdf.get_string_width(test_line) < effective_width:
                    line = test_line
                else:
                    pdf.multi_cell(0, 6, line, align='J')
                    line = word
            if line:
                pdf.multi_cell(0, 6, line, align='J')
            pdf.ln(3)
        
        # Add signature
        if len(paragraphs) > 2:
            signature = paragraphs[-1].split('\n')
            pdf.ln(10)
            for line in signature:
                pdf.cell(0, 6, line.strip(), ln=True, align='L')
    
    else:
        # Resume formatting
        margin = 20
        pdf.set_margins(margin, margin, margin)
        pdf.set_auto_page_break(auto=True, margin=margin)
        
        sections = content.split('\n\n')
        
        # Process header
        pdf.set_font("DejaVu", 'B', 12)
        header = sections[0].replace(" | ", "  |  ")
        pdf.cell(0, 8, header, ln=True, align='C')
        pdf.ln(2)
        
        # Add line under header
        pdf.line(margin, pdf.get_y(), pdf.w - margin, pdf.get_y())
        pdf.ln(5)
        
        # Process other sections
        for section in sections[1:]:
            if not section.strip():
                continue
                
            # Extract section title and content
            parts = section.split('\n', 1)
            if len(parts) < 2:
                continue
                
            title, content = parts
            
            # Add section title
            pdf.set_font("DejaVu", 'B', 11)
            pdf.cell(0, 8, title, ln=True)
            pdf.ln(2)
            
            # Add section content
            pdf.set_font("DejaVu", '', 11)
            
            # Handle bullet points
            if "• " in content:
                for line in content.split('\n'):
                    if line.strip().startswith('• '):
                        # Add proper bullet point
                        pdf.cell(5, 6, '•', align='R')
                        indented_text = line.replace('• ', '', 1)
                        pdf.multi_cell(0, 6, indented_text, align='L')
                    else:
                        pdf.multi_cell(0, 6, line, align='L')
            else:
                pdf.multi_cell(0, 6, content, align='L')
            
            pdf.ln(5)
            
            # Add separator line between sections
            if section != sections[-1]:
                pdf.line(margin, pdf.get_y()-2, pdf.w - margin, pdf.get_y()-2)
                pdf.ln(5)

    # Handle output
    if isinstance(filename_or_buffer, io.BytesIO):
        pdf_str = pdf.output(dest='S').encode('latin1')
        filename_or_buffer.write(pdf_str)
    else:
        pdf.output(filename_or_buffer)
