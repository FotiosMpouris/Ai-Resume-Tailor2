import openai
import re
from fpdf import FPDF
from datetime import date
import io  # Ensure io is imported

def analyze_resume_and_job(resume, job_description):
    # ... existing code ...

def process_gpt_output(output):
    # ... existing code ...

def generate_full_resume(header, summary, education, work_experience, company_name):
    # ... existing code ...

def generate_cover_letter(resume, job_description, cover_letter_info):
    # ... existing code ...

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

def create_pdf(content, filename_or_buffer, pdf_type='resume'):
    pdf = PDF(format='Letter')
    pdf.add_page()

    # Add Unicode fonts (regular and bold)
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)

    if isinstance(filename_or_buffer, str) and filename_or_buffer.endswith(".pdf"):
        # Saving to a file
        if pdf_type == "cover_letter":
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

    elif isinstance(filename_or_buffer, io.BytesIO):
        # Saving to a buffer
        # Determine the PDF type based on content or additional parameter if implemented
        # Here, we use a simple heuristic
        if "Dear " in content:
            pdf_type = "cover_letter"
        else:
            pdf_type = "resume"

        if pdf_type == "cover_letter":
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

    if isinstance(filename_or_buffer, io.BytesIO):
        # Output PDF as string and write to buffer
        pdf_content = pdf.output(dest='S').encode('latin1')  # 'S' returns a string, encode to bytes
        filename_or_buffer.write(pdf_content)
    else:
        # Output to file
        pdf.output(filename_or_buffer)
