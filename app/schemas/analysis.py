from pydantic import BaseModel, Field

class AnalysisRequest(BaseModel):
    github_repo_id: int = Field(gt=0)
    branch: str = Field(min_length=1, max_length=200, pattern=r"^[A-Za-z0-9._/-]+$")
