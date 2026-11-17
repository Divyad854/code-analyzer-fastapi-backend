from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class GitHubAccount(Base):
    __tablename__ = "github_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    github_user_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    github_username: Mapped[str] = mapped_column(String(100), nullable=False)
    encrypted_access_token: Mapped[str] = mapped_column(String(2000), nullable=False)
    connected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    # back_populates is used to create a bidirectional relationship between two SQLAlchemy models.
    # It connects the relationship attributes on both sides
    user = relationship("User", back_populates="github_account")
