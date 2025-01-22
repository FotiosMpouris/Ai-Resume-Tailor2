# main_functions.py

import openai
import re
from fpdf import FPDF
from datetime import date
import io
import os

def analyze_resume_and_job(resume, job_description):
    system_message = """
    You are an esteemed resume analyst and career advisor with decades of experience in HR and recruitment across various industries. Your expertise rivals that of a Pulitzer Prize-winning journalist, ensuring that all written content is of the highest professional standard. Your task is to analyze the provided resume and job description, then provide:
    1. A meticulously crafted header for the resume, including the candidate's name and key contact information.
    2. A compelling custom summary (3-4 sentences) that eloquently highlights the candidate's most relevant skills and experiences for this specific job.
    3. A concise and well-structured summary of the candidate's education information.
    4. Detailed summaries of at least three relevant work experiences for this job, focusing on the most recent or most applicable positions. Each experience should be described with precision and professionalism.
    5. Extraction of the full name, address, email, and phone number for use in a cover letter.
    6. Extraction of the company name from the job description for use in the cover letter greeting.
    7. Special attention to the "Applications and Games" section in the resume:
       - Briefly mention the listed applications and games in the resume.
       - Provide more in-depth coverage of these items in the cover letter.
    8. Ensure all summaries and descriptions are written in the first person with impeccable grammar and style.
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

    APPLICATIONS AND GAMES:
    [Brief mention of applications and games]

    COVER LETTER INFO:
    Full Name: [Extracted full name]
    Address: [Extracted address]
    Email: [Extracted email]
    Phone: [Extracted phone number]
    Company Name: [Extracted company name]
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,  # Lower temperature for more deterministic output
            max_tokens=2000
        )
    except Exception as e:
        print(f"OpenAI API request failed: {e}")
        return None

    output = response.choices[0].message.content
    return process_gpt_output(output)

def process_gpt_output(output):
    # Define section headers
    section_headers = [
        'HEADER:',
        'SUMMARY:',
        'EDUCATION:',
        'RELEVANT WORK EXPERIENCE:',
        'APPLICATIONS AND GAMES:',
        'COVER LETTER INFO:'
    ]
    
    # Initialize a dictionary to hold sections
    sections = {header[:-1]: "" for header in section_headers}
    
    # Split the output by lines
    lines = output.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if any(line.startswith(header) for header in section_headers):
            for header in section_headers:
                if line.startswith(header):
                    current_section = header[:-1]
                    sections[current_section] = ""
                    break
        elif current_section:
            sections[current_section] += line + '\n'
    
    # Process cover letter info into a dictionary
    cover_letter_info = {}
    if sections.get('COVER LETTER INFO'):
        cover_lines = sections['COVER LETTER INFO'].strip().split('\n')
        for item in cover_lines:
            if ':' in item:
                key, value = item.split(':', 1)
                cover_letter_info[key.strip()] = value.strip()
    
    return (
        sections.get('HEADER', '').strip(),
        sections.get('SUMMARY', '').strip(),
        sections.get('EDUCATION', '').strip(),
        sections.get('RELEVANT WORK EXPERIENCE', '').strip(),
        sections.get('APPLICATIONS AND GAMES', '').strip(),
        cover_letter_info
    )

def generate_full_resume(header, summary, education, work_experience, applications_and_games):
    full_resume = f"""
{header}

SUMMARY
{summary}

EDUCATION
{education}

RELEVANT WORK EXPERIENCE
{work_experience}

APPLICATIONS AND GAMES
{applications_and_games}
"""
    return full_resume.strip()

def generate_cover_letter(resume, job_description, cover_letter_info, applications_and_games):
    today = date.today().strftime("%B %d, %Y")

    system_message = """
    You are an esteemed cover letter writer with extensive experience in HR and recruitment. Your writing is of the highest professional standard, comparable to that of a Pulitzer Prize-winning journalist. Your task is to create a compelling, personalized cover letter based on the candidate's resume, the job description provided, and the specific candidate information given. The cover letter should:
    1. Highlight the candidate's most relevant skills and experiences for the specific job with eloquence and precision.
    2. Provide an in-depth discussion of the candidate's applications and games projects, demonstrating their relevance to the position.
    3. Demonstrate genuine enthusiasm for the position and the company.
    4. Be concise, typically not exceeding one page, while maintaining depth and clarity.
    5. Encourage the employer to review the attached resume and consider the candidate for an interview.
    6. Use a first-person narrative, referring to the candidate directly with impeccable grammar and style.
    """

    user_message = f"""
    Please write a cover letter based on the following information:

    Candidate Information:
    Full Name: {cover_letter_info.get('Full Name', '')}
    Company: {cover_letter_info.get('Company Name', '')}
    Address: {cover_letter_info.get('Address', '')}
    Email: {cover_letter_info.get('Email', '')}
    Phone: {cover_letter_info.get('Phone', '')}

    Resume:
    {resume}

    Job Description:
    {job_description}

    Applications and Games:
    {applications_and_games}

    Provide only the body of the cover letter, without any salutation or closing.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,  # Lower temperature for consistency
            max_tokens=1500
        )
    except Exception as e:
        print(f"OpenAI API request failed: {e}")
        return ""

    cover_letter_content = response.choices[0].message.content.strip()

    # Format the cover letter with the correct header, date, and salutation
    formatted_cover_letter = f"""\
{cover_letter_info.get('Full Name', '')}
{cover_letter_info.get('Address', '')}
{cover_letter_info.get('Phone', '')}
{cover_letter_info.get('Email', '')}

{today}

Dear {cover_letter_info.get('Company Name', '')} Hiring Team,

{cover_letter_content}

Sincerely,
{cover_letter_info.get('Full Name', '')}
"""
    return formatted_cover_letter

class PDF(FPDF):
    def header(self):
        # Overriding to remove the default header
        pass

    def footer(self):
        # Overriding to remove the default footer
        pass

    def chapter_title(self, title):
        self.set_font('DejaVu', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, title, ln=True, align='L')
        self.ln(2)

    def chapter_body(self, body, align='J'):
        self.set_font('DejaVu', '', 12)
        self.multi_cell(0, 7, body, align=align)
        self.ln()

    def add_bullet_point(self, text):
        # Save the current x and y positions
        x = self.get_x()
        y = self.get_y()
        # Draw the bullet
        self.set_xy(x, y)
        self.set_font('DejaVu', '', 12)
        self.cell(5, 7, u'\u2022', 0, 0)
        # Write the text
        self.multi_cell(0, 7, ' ' + text, 0, 'J')

def create_pdf(content, filename_or_buffer, is_cover_letter=False):
    pdf = PDF(format='Letter')
    pdf.add_page()

    # Ensure the DejaVu fonts are in the same directory or provide the correct path
    font_path = os.path.dirname(os.path.abspath(__file__))  # Current directory
    try:
        pdf.add_font('DejaVu', '', os.path.join(font_path, 'DejaVuSansCondensed.ttf'), uni=True)
        pdf.add_font('DejaVu', 'B', os.path.join(font_path, 'DejaVuSansCondensed-Bold.ttf'), uni=True)
    except Exception as e:
        print(f"Failed to add fonts: {e}")
        return

    if is_cover_letter:
        # Cover Letter Formatting
        # Adjust margins for cover letter
        left_margin = 25
        right_margin = 25
        top_margin = 25
        pdf.set_margins(left_margin, top_margin, right_margin)
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Split the content into lines
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Dear') or line.startswith('Sincerely'):
                pdf.set_font("DejaVu", 'B', 12)
            else:
                pdf.set_font("DejaVu", '', 12)
            pdf.multi_cell(0, 7, line, align='L')
            pdf.ln(1)
    else:
        # Resume Formatting
        left_margin = 15
        right_margin = 15
        top_margin = 20
        pdf.set_margins(left_margin, top_margin, right_margin)
        pdf.set_auto_page_break(auto=True, margin=15)

        # Split content into main sections
        main_sections = re.split(r'\n\n(?=SUMMARY|EDUCATION|RELEVANT WORK EXPERIENCE|APPLICATIONS AND GAMES)', content)

        if not main_sections:
            print("No content to add to the PDF.")
            return

        # Process the header section (name, address, phone, email)
        pdf.set_font("DejaVu", 'B', 20)  # Increased font size for the header
        header_text = main_sections[0].strip()

        # Assuming header_text contains Name, Address, Phone, Email separated by line breaks or commas
        # Split by line breaks or commas
        if '\n' in header_text:
            header_parts = [part.strip() for part in header_text.split('\n') if part.strip()]
        else:
            header_parts = [part.strip() for part in header_text.split(',') if part.strip()]

        if len(header_parts) >= 4:
            name = header_parts[0]
            address = header_parts[1]
            phone = header_parts[2]
            email = header_parts[3]

            # Combine address, phone, and email into a single line with even spacing
            contact_info = f"{address}      {phone}      {email}"
        else:
            # Fallback if not enough parts are found
            name = header_parts[0] if header_parts else ""
            contact_info = header_text.replace(name, "").strip()

        # Add the name
        pdf.multi_cell(0, 10, name, align='C')

        # Add the contact information
        pdf.set_font("DejaVu", '', 12)  # Smaller font for contact info
        pdf.multi_cell(0, 10, contact_info, align='C')

        pdf.ln(5)  # Spacing after the header

        # Process the rest of the sections
        for section in main_sections[1:]:
            if section.startswith("SUMMARY"):
                pdf.chapter_title("SUMMARY")
                summary_text = section.split('\n', 1)[1].strip()
                pdf.chapter_body(summary_text)
            elif section.startswith("EDUCATION"):
                pdf.chapter_title("EDUCATION")
                education_text = section.split('\n', 1)[1].strip()
                pdf.chapter_body(education_text)
            elif section.startswith("RELEVANT WORK EXPERIENCE"):
                pdf.chapter_title("RELEVANT WORK EXPERIENCE")
                work_experiences = section.split('\n', 1)[1].strip().split('\n\n')
                for exp in work_experiences:
                    exp = exp.strip()
                    if exp:
                        pdf.add_bullet_point(exp)
            elif section.startswith("APPLICATIONS AND GAMES"):
                pdf.chapter_title("APPLICATIONS AND GAMES")
                applications_text = section.split('\n', 1)[1].strip()
                # Briefly mention applications and games in the resume
                pdf.chapter_body(applications_text, align='L')  # Left align for brief mention

    # Handle PDF Output
    if filename_or_buffer is not None:
        if isinstance(filename_or_buffer, io.BytesIO):
            # Output as string and encode to bytes
            pdf_str = pdf.output(dest='S').encode('latin1')
            filename_or_buffer.write(pdf_str)
        else:
            # Assume it's a filename
            pdf.output(filename_or_buffer)

# Example usage (for testing purposes)
if __name__ == "__main__":
    sample_resume = """
    John Doe
    North Reading, MA
    (123) 456-7890
    johndoe@example.com

    SUMMARY
    Experienced software developer with a strong background in developing scalable applications and engaging games.

    EDUCATION
    B.S. in Computer Science, XYZ University, 2015

    RELEVANT WORK EXPERIENCE
    Senior Developer at ABC Corp (2018-2023)
    - Led a team of developers in creating enterprise-level software solutions.
    
    Software Engineer at DEF Inc (2015-2018)
    - Developed and maintained web applications, improving performance by 30%.

    APPLICATIONS AND GAMES
    - Developed "FunQuest," an interactive educational game for children.
    - Created "TaskMaster," a productivity application used by over 10,000 users.
    """

    sample_job_description = """
    We are seeking a Senior Software Developer with experience in building scalable applications and developing engaging user experiences. The ideal candidate will have a strong background in team leadership and project management.
    """

    header, summary, education, work_experience, applications_and_games, cover_info = analyze_resume_and_job(sample_resume, sample_job_description)
    full_resume = generate_full_resume(header, summary, education, work_experience, applications_and_games)
    cover_letter = generate_cover_letter(full_resume, sample_job_description, cover_info, applications_and_games)

    # Create resume PDF
    resume_buffer = io.BytesIO()
    create_pdf(full_resume, resume_buffer, is_cover_letter=False)

    # Create cover letter PDF
    cover_letter_buffer = io.BytesIO()
    create_pdf(cover_letter, cover_letter_buffer, is_cover_letter=True)

    print("PDFs generated successfully.")
