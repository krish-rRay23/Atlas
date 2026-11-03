"""ATLAS Pydantic Core Data Models & Schemas.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class ProjectCreate(BaseModel):
    title: str = Field(..., description="Project title")
    research_question: str = Field(..., description="Primary research question")
    countries: List[str] = Field(default=["IND", "IDN", "VNM", "THA", "PHL"])
    indicators: List[str] = Field(default=[])
    date_start: int = Field(default=2015)
    date_end: int = Field(default=2024)

class Project(ProjectCreate):
    id: str
    created_at: str
    status: str = "active"

class SourceMetadata(BaseModel):
    source_id: str
    name: str
    publisher: str
    url: str
    source_type: Literal["international_organization", "central_bank", "industry_association", "academic_benchmark"]
    methodology: str
    coverage_geos: List[str]
    reference_period: str
    publication_date: str
    retrieval_date: str
    file_hash_sha256: Optional[str] = None
    data_format: str = "json"
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    limitations: Optional[str] = None

class IndicatorDefinition(BaseModel):
    indicator_code: str
    name: str
    category: str  # financial_inclusion, digital_payments, infrastructure, macro_demographic
    unit: str
    denominator: Optional[str] = None
    target_population: Optional[str] = None
    source_id: str
    description: Optional[str] = None

class ObservationRecord(BaseModel):
    id: Optional[str] = None
    country_iso3: str
    country_name: str
    indicator_code: str
    indicator_name: str
    year: int
    value: Optional[float] = None
    unit: str
    source_id: str
    source_name: str
    reference_period: str
    extraction_date: str
    confidence: float = 1.0
    status: Literal["available", "missing", "projected"] = "available"
    notes: Optional[str] = None

class EvidenceRecord(BaseModel):
    evidence_id: str
    source_id: str
    country_iso3: str
    country_name: str
    indicator_code: str
    value: Optional[float]
    unit: str
    year: int
    citation_text: str
    page_or_table_ref: str
    extraction_method: Literal["api_deterministic", "table_parser", "pdf_extractor", "manual_audit"]
    validation_status: Literal["verified", "caveat", "flagged", "rejected"]
    reviewer_notes: Optional[str] = None
    verified_by_human: bool = False
    verified_at: Optional[str] = None

class ComparabilityAssessment(BaseModel):
    assessment_id: str
    indicator_code: str
    country_a: str
    country_b: str
    classification: Literal["comparable", "comparable_with_caveats", "not_comparable", "insufficient_information"]
    justification: str
    rule_applied: str
    unit_consistency: bool
    denominator_consistency: bool
    population_consistency: bool
    methodology_consistency: bool
    period_consistency: bool

class ClaimValidation(BaseModel):
    claim_id: str
    claim_text: str
    referenced_evidence_ids: List[str]
    status: Literal["supported", "partially_supported", "contradicted", "unverified", "missing_evidence"]
    numerical_fidelity_score: float = Field(..., ge=0.0, le=1.0)
    temporal_match: bool
    geographic_match: bool
    explanation: str

class ResearchMemoSection(BaseModel):
    section_number: int
    title: str
    content: str
    citations: List[str] = []
    interpretations: List[str] = []
    data_limitations: List[str] = []

class ResearchMemo(BaseModel):
    memo_id: str
    project_id: str
    title: str
    research_question: str
    generated_at: str
    model_used: str
    sections: List[ResearchMemoSection]
    referenced_evidence_count: int
    validation_status: Literal["fully_grounded", "grounded_with_caveats", "unverified"]
    total_tokens: int
    inference_seconds: float

class BenchmarkRun(BaseModel):
    run_id: str
    benchmark_name: str
    dataset_version: str
    sample_count: int
    metrics: Dict[str, float]
    passed_threshold: bool
    execution_time_seconds: float
    timestamp: str
    details: Dict[str, Any] = {}

class EconomicsReport(BaseModel):
    manual_hours_estimated: float
    assisted_hours_actual: float
    time_saved_percent: float
    productivity_improvement_ratio: float
    total_tokens_consumed: int
    estimated_api_cost_usd: float
    cost_per_accepted_output_usd: float
    scenarios: Dict[str, Dict[str, Any]]
