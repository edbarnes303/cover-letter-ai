# Cover Letter AI

Generate polished cover letters as PDFs using OpenAI, based on your resume, a job description, and example cover letters for tone/style matching.

## Setup

```bash
pip install -r requirements.txt
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-key-here"
```

## Context Files

Place the following files in the `context/` directory:

| File | Description |
|---|---|
| `resume.md` | Your resume in Markdown format |
| `job_description.txt` | Default job description (used when no URL is provided) |
| `example_*.md` | Example application packages (job description + cover letter) used for tone and format matching |

## Usage

Generate a cover letter from a job posting URL:

```bash
python generate_cover.py https://example.com/job-posting
```

Or use the default job description in `context/job_description.txt`:

```bash
python generate_cover.py
```

### Options

| Flag | Description |
|---|---|
| `-o`, `--output-dir` | Directory to save the PDF (default: current directory) |
| `-p`, `--custom-prompt` | Custom instruction to append to the generation prompt |

### Examples

```bash
# Save to a specific directory
python generate_cover.py https://example.com/job -o ~/Documents

# Add a custom instruction
python generate_cover.py https://example.com/job -p "Emphasize my leadership experience"
```

The output PDF is saved as `cl_<timestamp>.pdf`.
