from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, JSON, Integer
# map - Provides Python type annotations for ORM attributes
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Deletes associated reports when the referenced user is deleted
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    github_repo_id: Mapped[int] = mapped_column(Integer, nullable=False)
    repo_full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    branch: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="completed", nullable=False)
    report_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="reports")
