import os
import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from google import genai
from google.genai import types

from schemas import AnalysisResponse

app = typer.Typer(help="Structured Resume-to-Job Profile Matcher CLI")
console = Console()


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        console.print(f"[bold red]Error: File not found -> {file_path}[/bold red]")
        raise typer.Exit(1)

    if path.suffix.lower() == ".pdf":
        try:
            import pypdf

            reader = pypdf.PdfReader(path)
            text = "\n".join(
                [page.extract_text() for page in reader.pages if page.extract_text()]
            )
            return text
        except Exception as e:
            console.print(f"[bold red]Failed to parse PDF: {e}[/bold red]")
            raise typer.Exit(1)
    else:
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            console.print(f"[bold red]Failed to read file: {e}[/bold red]")
            raise typer.Exit(1)


@app.command()
def match(
    resume: str = typer.Argument(
        ..., help="Path to resume file (PDF, Markdown, or Text)"
    ),
    job_desc: str = typer.Argument(
        ..., help="Path to job description file or raw text string"
    ),
):
    """Analyze a resume against a job description and generate a structured match report."""

    # Check API key
    if not os.environ.get("GEMINI_API_KEY"):
        console.print(
            "[bold red]Error: GEMINI_API_KEY environment variable is not set.[/bold red]"
        )
        raise typer.Exit(1)

    resume_text = extract_text(resume)

    # Handle job description being a file path or inline text
    if Path(job_desc).exists():
        jd_text = extract_text(job_desc)
    else:
        jd_text = job_desc

    client = genai.Client()

    prompt = f"""
You are an expert technical recruiter and ATS (Applicant Tracking System) optimization engine. 
Analyze the candidate's resume against the provided job description. Perform a rigorous, objective gap analysis and compute accurate match metrics.

=== CANDIDATE RESUME ===
{resume_text}

=== JOB DESCRIPTION ===
{jd_text}
"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(
            description="Analyzing resume & job description with Gemini...", total=None
        )

        try:
            # Temporarily suppress stderr to block SDK warning prints
            original_stderr = sys.stderr
            sys.stderr = open(os.devnull, "w")
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AnalysisResponse,
                        temperature=0.1,
                    ),
                )
            finally:
                sys.stderr.close()
                sys.stderr = original_stderr

            # Parse the structured JSON response into our Pydantic model
            result = AnalysisResponse.model_validate_json(response.text)
        except Exception as e:
            console.print(f"[bold red]Analysis failed: {e}[/bold red]")
            raise typer.Exit(1)

    # Render Output using Rich
    console.print("\n")
    console.print(
        Panel.fit(
            f"[bold cyan]🎯 Match Report: {result.candidate.full_name}[/bold cyan]\n"
            f"Role Target: [bold green]{result.job.job_title}[/bold green]",
            title="Resume-Job Matcher",
            border_style="cyan",
        )
    )

    # Score Card Table
    score_table = Table(show_header=True, header_style="bold magenta")
    score_table.add_column("Metric", style="dim")
    score_table.add_column("Score / Status", justify="right")

    score_color = (
        "green"
        if result.match.match_score >= 75
        else ("yellow" if result.match.match_score >= 50 else "red")
    )
    score_table.add_row(
        "Overall Match Score",
        f"[{score_color} bold]{result.match.match_score}/100[/{score_color} bold]",
    )
    score_table.add_row(
        "Skill Match Percentage", f"{result.match.skill_match_percentage}%"
    )
    score_table.add_row("Experience Assessment", result.match.experience_fit)
    console.print(score_table)

    # Skills Breakdown Table
    skills_table = Table(show_header=True, header_style="bold blue")
    skills_table.add_column("Category", style="bold")
    skills_table.add_column("Skills")

    skills_table.add_row(
        "Matching Skills",
        ", ".join([f"[green]{s}[/green]" for s in result.match.matching_skills])
        or "None",
    )
    skills_table.add_row(
        "Missing Critical Skills",
        ", ".join([f"[red]{s}[/red]" for s in result.match.missing_critical_skills])
        or "None",
    )
    console.print(skills_table)

    # Gap Analysis Panel
    console.print(
        Panel(
            result.match.gap_analysis,
            title="[bold yellow]🔍 Gap Analysis[/bold yellow]",
            border_style="yellow",
        )
    )

    # Recommendations Panel
    recs_text = "\n".join([f"• {rec}" for rec in result.match.recommendations])
    console.print(
        Panel(
            recs_text,
            title="[bold green]💡 Actionable Recommendations[/bold green]",
            border_style="green",
        )
    )
    console.print("\n")


if __name__ == "__main__":
    app()
