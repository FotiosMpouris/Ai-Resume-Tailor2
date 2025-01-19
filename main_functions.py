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
        # Cover letter specific formatting
        left_margin = 25.4  # 1 inch
        right_margin = 25.4  # 1 inch
        top_margin = 25.4  # 1 inch
        pdf.set_margins(left_margin, top_margin, right_margin)

        pdf.set_auto_page_break(auto=True, margin=25.4)  # 1 inch bottom margin

        # Calculate effective page width (accounting for margins)
        effective_page_width = pdf.w - left_margin - right_margin

        # Set font for body text
        pdf.set_font("DejaVu", '', 11)

        # Split cover letter into paragraphs
        paragraphs = content.split('\n\n')

        # Process contact information
        contact_info = paragraphs[0].split('\n')
        for line in contact_info:
            pdf.set_x(left_margin)  # Ensure consistent left alignment
            pdf.cell(0, 5, line.strip(), ln=True, align='L')
        pdf.ln(5)

        # Process date and salutation
        if len(paragraphs) > 1:
            date_salutation = paragraphs[1].split('\n')
            if len(date_salutation) >= 2:
                # Date on the right
                pdf.cell(effective_page_width, 5, date_salutation[0].strip(), align='R', ln=True)
                pdf.ln(5)
                # Salutation on the left
                pdf.cell(0, 5, date_salutation[1].strip(), ln=True)
            pdf.ln(5)

        # Process the body of the letter
        for paragraph in paragraphs[2:]:
            pdf.multi_cell(effective_page_width, 5, paragraph.strip(), align='J')
            pdf.ln(5)

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

        # Process the header section (name, telephone, address, email)
        pdf.set_font("DejaVu", 'B', 12)  # Set to bold, slightly larger than body text
        header_lines = main_sections[0].split('\n')
        header_info = "  ".join([line.split(": ", 1)[-1] for line in header_lines])

        # Center the header between left and right margins
        header_width = pdf.get_string_width(header_info)
        if header_width > effective_page_width:
            # If header is too wide, reduce font size
            font_size = 12
            while header_width > effective_page_width and font_size > 9:
                font_size -= 0.5
                pdf.set_font("DejaVu", 'B', font_size)  # Keep bold
                header_width = pdf.get_string_width(header_info)

        # Calculate the center position and shift it slightly to the left
        x_position = (pdf.w - header_width) / 2 - pdf.get_string_width("  ")
        pdf.set_x(x_position)

        pdf.cell(header_width, 6, header_info, align='C', ln=True)

        # Add extra spacing after the header
        pdf.ln(10)

        # Add a line after the header
        pdf.line(left_margin, pdf.get_y(), pdf.w - right_margin, pdf.get_y())
        pdf.ln(3)

        # Process the rest of the sections
        pdf.set_font("DejaVu", 'B', 11)  # Set to bold for section headers
        for i, section in enumerate(main_sections[1:], 1):
            if section.startswith("SUMMARY"):
                pdf.set_font("DejaVu", 'B', 11)  # Bold for section header
                pdf.cell(0, 5, "SUMMARY", ln=True)
                pdf.set_font("DejaVu", '', 11)  # Regular font for content
                pdf.multi_cell(effective_page_width, 5, section.split('\n', 1)[1].strip(), align='J')
            elif section.startswith("EDUCATION"):
                pdf.set_font("DejaVu", 'B', 11)  # Bold for section header
                pdf.cell(0, 5, "EDUCATION", ln=True)
                pdf.set_font("DejaVu", '', 11)  # Regular font for content
                pdf.multi_cell(effective_page_width, 5, section.split('\n', 1)[1].strip(), align='J')
            elif section.startswith("RELEVANT WORK EXPERIENCE"):
                pdf.set_font("DejaVu", 'B', 11)  # Bold for section header
                pdf.cell(0, 5, "RELEVANT WORK EXPERIENCE", ln=True)
                pdf.set_font("DejaVu", '', 11)  # Regular font for content
                pdf.multi_cell(effective_page_width, 5, section.split('\n', 1)[1].strip(), align='J')

            if i < len(main_sections) - 1:
                pdf.ln(3)
                pdf.line(left_margin, pdf.get_y(), pdf.w - right_margin, pdf.get_y())
                pdf.ln(3)

    # Handle PDF Output
    if filename_or_buffer is not None:
        if isinstance(filename_or_buffer, io.BytesIO):
            # Output as string and encode to bytes
            pdf_str = pdf.output(dest='S').encode('latin1')
            filename_or_buffer.write(pdf_str)
        else:
            # Assume it's a filename
            pdf.output(filename_or_buffer)
