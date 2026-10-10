from typing import List, Optional
from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    full_name: str = Field(description="Candidate's full name")
    email: Optional[str] = Field(description="Candidate's email if available")
    years_of_experience: float = Field(
        description="Total estimated professional years of experience"
    )
    technical_skills: List[str] = Field(
        description="List of technical skills, languages, frameworks, tools"
    )
    core_domains: List[str] = Field(
        description="Core domains/roles (e.g., Backend, ML, Systems)"
    )
    summary: str = Field(description="Brief 2-sentence professional summary")


class JobRequirements(BaseModel):
    job_title: str
    required_skills: List[str] = Field(
        description="Mandatory skills, tools, and languages required"
    )
    preferred_skills: List[str] = Field(description="Nice-to-have or bonus skills")
    min_years_experience: float = Field(
        description="Minimum years of experience required"
    )
    key_responsibilities: List[str]


class MatchReport(BaseModel):
    match_score: int = Field(description="Overall fit score from 0 to 100")
    skill_match_percentage: int = Field(
        description="Percentage of required skills possessed by the candidate"
    )
    experience_fit: str = Field(
        description="Assessment of whether experience meets/exceeds requirements"
    )
    matching_skills: List[str] = Field(
        description="Skills present in both resume and job description"
    )
    missing_critical_skills: List[str] = Field(
        description="Required skills missing from the resume"
    )
    gap_analysis: str = Field(
        description="Detailed narrative explaining strengths and gaps"
    )
    recommendations: List[str] = Field(
        description="Actionable advice for the candidate to improve their fit"
    )


class AnalysisResponse(BaseModel):
    candidate: CandidateProfile
    job: JobRequirements
    match: MatchReport
