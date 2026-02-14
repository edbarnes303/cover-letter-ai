import os
import time
import glob
import argparse
from openai import OpenAI
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup

client = OpenAI()


def fetch_job_description(url: str) -> str:
    """Fetch a URL and extract the main text content as a job description."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)

    return text


def load_examples() -> str:
    """Load all example application packages from the context directory."""
    example_files = sorted(glob.glob("context/example_*.md"))
    examples = []
    for filepath in example_files:
        examples.append(open(filepath).read())
    return "\n\n---\n\n".join(examples)


def generate_cover_letter(resume_text: str, job_description: str, examples: str) -> str:
    """
    Generate a cover letter using the candidate's resume and a job description.
    """
    # Accept an optional custom_prompt argument
    custom_prompt = None
    if hasattr(generate_cover_letter, "custom_prompt"):
        custom_prompt = getattr(generate_cover_letter, "custom_prompt")

    prompt = f"""
You are an expert at writing concise, professional cover letters. Below are example application packages
that demonstrate the desired format and tone. Each example contains a job description and the resulting
cover letter. Study these examples carefully, then write a new cover letter for the provided resume and
job description.

If Python, Java, TypeScript, AWS, Lambda or Serverless are mentioned in the job description be sure to 
reference your experience with those technologies in the cover letter.

If the job description mentions "Nice to haves" or "Preferred qualifications" that are also mentioned
in the resume, be sure to reference those in the cover letter.

Important: Only treat a role as the candidate's current position if the date range ends with "Present"
(e.g. "2024 - Present"). A role with two specific years (e.g. "2025 - 2026") is a past role, even if
the end year is the current year.

Important: Do not include date ranges or years next to company or role names in the cover letter
(e.g. avoid "Company (2022–2025)" or "Role, 2022–2025"). If you need to imply recency, use phrasing
like "most recent" or "previously" without specific dates.

Important: Avoid using em dashes (—). Prefer commas, parentheses, or separate sentences instead.

Examples:
'''
{examples}
'''

Now write a cover letter for the following:

Resume:
'''
{resume_text}
'''

Job Description:
'''
{job_description}
'''

{f"Custom request: {custom_prompt}" if custom_prompt else ""}
"""

    response = client.responses.create(
        model="gpt-5.2",
        input=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_output_tokens=1000,
        temperature=0.4,
    )

    return response.output_text


def save_cover_letter_pdf(text: str, filepath: str) -> None:
    """Convert markdown cover letter text to a well-formatted PDF."""
    font_size = 12
    line_height = 0.5  # Line height multiplier (1.32x the font size)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(25, 25, 25)
    pdf.set_auto_page_break(auto=True, margin=25)

    # Use a Unicode TTF font to support smart quotes and other special characters
    font_dir = "/System/Library/Fonts/Supplemental/"
    pdf.add_font("ArialUnicode", "", os.path.join(font_dir, "Arial Unicode.ttf"))
    pdf.add_font("ArialUnicode", "B", os.path.join(font_dir, "Arial Unicode.ttf"))
    pdf.add_font("ArialUnicode", "I", os.path.join(font_dir, "Arial Unicode.ttf"))
    pdf.set_font("ArialUnicode", size=font_size)

    # Split text into paragraphs and render each with proper line height
    paragraphs = text.strip().split('\n\n')
    for i, para in enumerate(paragraphs):
        if para.strip():
            # Add spacing between paragraphs
            if i > 0:
                pdf.ln(font_size * 0.5)
            
            # Use multi_cell with max_line_height parameter for proper spacing
            pdf.multi_cell(0, h=font_size * line_height, text=para.strip(), markdown=True, align="L")
    
    pdf.output(filepath)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate a cover letter as a PDF.")
    parser.add_argument("url", nargs="?", default=None, help="URL to fetch the job description from.")
    parser.add_argument("-o", "--output-dir", default=".", help="Directory to save the PDF (default: current directory).")
    parser.add_argument("-p", "--custom-prompt", default=None, help="Custom request to add to the prompt.")
    args = parser.parse_args()

    output_dir = os.path.expanduser(args.output_dir)
    if not os.path.isdir(output_dir):
        print(f"Error: Output directory '{output_dir}' does not exist.")
        raise SystemExit(1)

    resume_text = open("context/resume.md").read()

    if args.url:
        print(f"Fetching job description from: {args.url}\n")
        job_description = fetch_job_description(args.url)
        # print("--- Parsed Job Description ---")
        # print(job_description)
        # print("--- End Job Description ---\n")
    else:
        job_description = open("context/job_description.txt").read()

    examples = load_examples()


    # Pass custom prompt to generate_cover_letter
    if args.custom_prompt:
        setattr(generate_cover_letter, "custom_prompt", args.custom_prompt)
    else:
        if hasattr(generate_cover_letter, "custom_prompt"):
            delattr(generate_cover_letter, "custom_prompt")

    cover_letter = generate_cover_letter(
        resume_text=resume_text,
        job_description=job_description,
        examples=examples,
    )

    filename = os.path.join(output_dir, f"cl_{int(time.time())}.pdf")
    save_cover_letter_pdf(cover_letter, filename)
    print(f"Cover letter saved to: {filename}")
