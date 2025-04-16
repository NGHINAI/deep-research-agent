from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class ResearchData(BaseModel):
    source_url: str
    extracted_content: str
    credibility_score: float
    freshness: datetime
    topics: list[str]
    primary_sources: int = 0
    secondary_sources: int = 0

    def validate_source_ratio(self):
        if self.secondary_sources == 0:
            return True
        return (self.primary_sources / self.secondary_sources) >= 0.33

class ReportFragment(BaseModel):
    section_id: UUID
    content: str
    sources: list[str]
    version_history: list[dict]

class SessionContext(BaseModel):
    research_state: dict
    generation_progress: dict
    validation_metrics: dict