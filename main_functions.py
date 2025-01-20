import openai
import re
from fpdf import FPDF
from datetime import date
import io
import os

def analyze_resume_and_job(resume, job_description):
    system_message = """
    You are an expert resume analyst and career advisor with decades of experience in HR and recruitment across various industries. Your task is to analyze the provided resume and job description, then provide:
    1. A tailored header for the resume, including the candidate's name and key contact information.
    2. A custom summary (3-4 sentences) that highlights the candidate's most relevant skills and experiences for this specific job.
    3. Extract and summarize the candidate's education information.
    4. Extract and summarize at least three relevant work experiences for this job, focusing on the most recent or most applicable positions. Each experience should be described in detail.
    5. Extract the full name, address, email, and phone number for use in a cover letter.
    6. Extract the company name from the job description for use in the cover letter greeting.
    7. Ensure all summaries and descriptions are written in the first person.
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

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,  # Lower temperature for more deterministic output
            max_tokens=1500
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
        cover_letter_info
    )

def generate_full_resume(header, summary, education, work_experience):
    full_resume = f"""
{header}

SUMMARY
{summary}

EDUCATION
{education}

RELEVANT WORK EXPERIENCE
{work_experience}
"""
    return full_resume.strip()

def generate_cover_letter(resume, job_description, cover_letter_info):
    today = date.today().strftime("%B %d, %Y")

    system_message = """
    You are an expert cover letter writer with years of experience in HR and recruitment. Your task is to create a compelling, personalized cover letter based on the candidate's resume, the job description provided, and the specific candidate information given. The cover letter should:
    1. Highlight the candidate's most relevant skills and experiences for the specific job.
    2. Show enthusiasm for the position and company.
    3. Be concise, typically not exceeding one page.
    4. Encourage the employer to review the attached resume and consider the candidate for an interview.
    5. Use a first-person narrative, referring to the candidate directly.
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
            max_tokens=1000
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
        main_sections = re.split(r'\n\n(?=SUMMARY|EDUCATION|RELEVANT WORK EXPERIENCE)', content)

        if not main_sections:
            print("No content to add to the PDF.")
            return

        # Process the header section (name, telephone, address, email)
        pdf.set_font("DejaVu", 'B', 20)  # Increased font size for the header
        header_lines = main_sections[0].split('\n')
        
        # Center the header and ensure it wraps properly
        for line in header_lines:
            line = line.strip()
            if line:
                pdf.multi_cell(0, 10, line, align='C')
        
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

    # Handle PDF Output
    if filename_or_buffer is not None:
        if isinstance(filename_or_buffer, io.BytesIO):
            # Output as string and encode to bytes
            pdf_str = pdf.output(dest='S').encode('latin1')
            filename_or_buffer.write(pdf_str)
        else:
            # Assume it's a filename
            pdf.output(filename_or_buffer)

# Example usage:
if __name__ == "__main__":
    # Sample resume and job description
    sample_resume = """
John Doe
1234 Elm Street, Anytown, USA
johndoe@example.com | (123) 456-7890

PROFESSIONAL SUMMARY
I am an experienced software developer with expertise in Python, Java, and cloud technologies. I have a proven track record of delivering high-quality software solutions on time and within budget.

EDUCATION
B.Sc. in Computer Science, University of Somewhere, 2015 - 2019

RELEVANT WORK EXPERIENCE
Software Developer at TechCorp (2019 - Present)
- I developed and maintained web applications using Python and Django.
- I collaborated with cross-functional teams to define project requirements.
- I implemented CI/CD pipelines to streamline deployment processes.

Junior Developer at WebSolutions (2017 - 2019)
- I assisted in the development of client websites using JavaScript and React.
- I participated in code reviews and provided constructive feedback.
- I managed database operations and ensured data integrity.
"""

    sample_job_description = """
We are seeking a skilled Software Developer with experience in Python and cloud platforms. The ideal candidate will have a strong background in web application development, familiarity with CI/CD practices, and the ability to work collaboratively in a fast-paced environment.

Responsibilities:
- Develop and maintain web applications using Python frameworks.
- Implement and manage CI/CD pipelines.
- Collaborate with design and product teams to deliver high-quality software.
"""

    analysis = analyze_resume_and_job(sample_resume, sample_job_description)
    if analysis:
        header, summary, education, work_experience, cover_letter_info = analysis

        # Generate Resume
        full_resume = generate_full_resume(header, summary, education, work_experience)
        
        # Create Resume PDF (Save to file)
        create_pdf(full_resume, "resume.pdf", is_cover_letter=False)
        print("Resume PDF generated successfully.")

        # Alternatively, create Resume PDF (Save to BytesIO buffer)
        resume_buffer = io.BytesIO()
        create_pdf(full_resume, resume_buffer, is_cover_letter=False)
        # You can now use resume_buffer.getvalue() to access the PDF bytes
        print("Resume PDF written to BytesIO buffer successfully.")

        # Generate Cover Letter
        cover_letter = generate_cover_letter(full_resume, sample_job_description, cover_letter_info)
        
        # Create Cover Letter PDF (Save to file)
        create_pdf(cover_letter, "cover_letter.pdf", is_cover_letter=True)
        print("Cover Letter PDF generated successfully.")

        # Alternatively, create Cover Letter PDF (Save to BytesIO buffer)
        cover_letter_buffer = io.BytesIO()
        create_pdf(cover_letter, cover_letter_buffer, is_cover_letter=True)
        # You can now use cover_letter_buffer.getvalue() to access the PDF bytes
        print("Cover Letter PDF written to BytesIO buffer successfully.")
