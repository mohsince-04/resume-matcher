This project is a **Structured Resume-to-Job Profile Matcher**. It is a command-line interface (CLI) application built using Python, Pydantic V2, Typer, Rich, and the Google GenAI SDK.

![Summary](https://github.com/user-attachments/assets/4f74eb21-789a-40a6-bd32-36c537bc251f "Note: Ignore vepython, it's just an alias.")

Its primary purpose is to solve the problem of unstructured resume evaluation. Instead of relying on crude keyword-matching Applicant Tracking Systems (ATS), this tool uses **Gemini 2.5 Flash** to perform a semantic analysis between a job description and a candidate's resume (whether in `.pdf`, `.md`, or `.txt` format).

It returns structured JSON constrained by strict Pydantic schemas and renders the analysis in a terminal UI featuring:

* **Match Score Card:** Quantified overall match (0–100), skill overlap percentage, and an experience fit evaluation.
* **Skill Categorization:** Direct comparison of matching required/preferred skills versus missing critical skills.
* **Gap Analysis:** Narrative highlighting candidate strengths alongside experience or skill discrepancies.
* **Actionable Recommendations:** Clear bullet points telling the candidate how to improve their resume or position their background to better align with the target role.

---

### Breakdown of Each File

The application consists of two core script files alongside inputs:

#### 1. `schemas.py` (The Data Contract & Output Schema)

This file defines the structured data models using **Pydantic V2**. It acts as the explicit contract enforced on the Gemini API response via structured output JSON generation (`response_schema`).

* **`CandidateProfile`**: Represents extracted information about the candidate, including `full_name`, `email`, `years_of_experience`, `technical_skills`, `core_domains`, and a brief `summary`.
* **`JobRequirements`**: Represents the parsed expectations from the job posting, such as `job_title`, `required_skills`, `preferred_skills`, `min_years_experience`, and `key_responsibilities`.
* **`MatchReport`**: Defines the score calculation and evaluation breakdown, including `match_score`, `skill_match_percentage`, `experience_fit`, `matching_skills`, `missing_critical_skills`, `gap_analysis`, and `recommendations`.
* **`AnalysisResponse`**: The root Pydantic model that wraps `CandidateProfile`, `JobRequirements`, and `MatchReport` into a single object.

---

#### 2. `matcher.py` (The Core CLI Application Engine)

This file houses the application logic, file parsing, API interaction, error handling, and terminal UI output generation.

* **Text Extraction (`extract_text`)**: Checks if the target resume/job file exists and extracts plain text. If the input is a `.pdf`, it dynamically loads `pypdf` to extract text across all pages; otherwise, it reads UTF-8 plain text/Markdown.
* **CLI Routing (`typer.Typer`)**: Configures the command-line interface, accepting file paths or inline strings for resumes and job descriptions as arguments.
* **Gemini API Integration (`google.genai.Client`)**: Constructs a prompt containing both input documents and calls `gemini-2.5-flash` with `response_mime_type="application/json"` and `response_schema=AnalysisResponse`.
* **Stderr Redirection / Warning Suppression**: Wraps the call to `client.models.generate_content` in a `sys.stderr` redirection context to prevent SDK warning messages from cluttering the terminal output.
* **Rich UI Rendering (`rich.console.Console`, `Table`, `Panel`)**: Converts the validated Pydantic object into color-coded tables, status panels, and styled scorecards for terminal display.
