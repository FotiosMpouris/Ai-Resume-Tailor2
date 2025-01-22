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

# Handle PDF Output
if filename_or_buffer is not None:
    if isinstance(filename_or_buffer, io.BytesIO):
        # Output as string and encode to bytes
        pdf_str = pdf.output(dest='S').encode('latin1')
        filename_or_buffer.write(pdf_str)
    else:
        # Assume it's a filename
        pdf.output(filename_or_buffer)
