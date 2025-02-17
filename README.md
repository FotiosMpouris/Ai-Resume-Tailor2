# AI Resume Tailor 2

AI Resume Tailor is a Streamlit-based web application that helps users customize their resumes and generate cover letters for specific job applications using OpenAI's GPT-4.

## Features

- Resume analysis and customization based on job descriptions
- Automatic generation of tailored summaries and work experience descriptions
- Cover letter generation
- PDF export functionality for both resume and cover letter
- User-friendly interface with real-time updates

## Prerequisites

- Python 3.7+
- OpenAI API key
- Streamlit account (for deployment)

## Required Python Packages

```bash
streamlit
openai
Pillow
fpdf
```

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd ai-resume-tailor
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
   - Create a `.streamlit/secrets.toml` file with your OpenAI API key:
   ```toml
   OPENAI_API_KEY = "your-api-key-here"
   ```

4. Ensure required fonts are present in the project directory:
   - `DejaVuSansCondensed.ttf`
   - `DejaVuSansCondensed-Bold.ttf`

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Access the application through your web browser (typically at `http://localhost:8501`)

3. Use the application:
   - Paste your existing resume in the left text area
   - Paste the job description in the right text area
   - Click "Analyze and Tailor Resume"
   - Review and edit the generated content
   - Download the tailored resume and cover letter as PDFs

## Project Structure

```
ai-resume-tailor/
├── app.py                      # Main Streamlit application
├── main_functions.py           # Core functionality and GPT integration
├── logo.png                    # Application logo
├── DejaVuSansCondensed.ttf    # Font files for PDF generation
├── DejaVuSansCondensed-Bold.ttf
└── .streamlit/
    └── secrets.toml           # Configuration secrets
```

## Development

The application consists of two main Python files:

- `app.py`: Contains the Streamlit interface and user interaction logic
- `main_functions.py`: Handles the core functionality including:
  - Resume and job description analysis
  - OpenAI GPT-4 integration
  - PDF generation
  - Text processing and formatting

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Your chosen license]

## Acknowledgments

- Built with Streamlit and OpenAI GPT-4
- Uses FPDF for PDF generation
- DejaVu fonts for PDF formatting
