
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.analysis_report import AnalysisReport
from app.models.github_account import GitHubAccount
from app.schemas.analysis import AnalysisRequest
from app.services.github_service import github_get
from app.services.analysis_service import (
    extract_repository_files,
    analyze_with_groq
)
from app.utils.security import decrypt_secret


router = APIRouter(
    prefix="/analysis",
    tags=["AI Code Analysis"]
)


# ------------------------- START ANALYSIS -------------------------

@router.post("/start", status_code=201)
def start_analysis(
    payload: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Get connected GitHub account.
    account = db.query(GitHubAccount).filter(
        GitHubAccount.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(
            status_code=400,
            detail="Connect your GitHub account first"
        )

    # Decrypt GitHub access token.
    token = decrypt_secret(account.encrypted_access_token)

    # Fetch accessible repositories.
    repos = github_get(
        "/user/repos",
        token,
        {
            "per_page": 100,
            "affiliation": "owner,collaborator,organization_member"
        }
    )

    # Find selected repository using GitHub repository ID.
    repo = next(
        (r for r in repos if r["id"] == payload.github_repo_id),
        None
    )

    if not repo:
        raise HTTPException(
            status_code=404,
            detail="Repository not found or not accessible"
        )

    owner = repo["owner"]["login"]
    name = repo["name"]

    # Verify selected branch.
    branches = github_get(
        f"/repos/{owner}/{name}/branches",
        token,
        {"per_page": 100}
    )

    if not any(b["name"] == payload.branch for b in branches):
        raise HTTPException(
            status_code=422,
            detail="Selected branch does not exist or is not accessible"
        )

    # Extract repository source files.
    files = extract_repository_files(
        token,
        owner,
        name,
        payload.branch
    )

    # Perform AI code analysis.
    report_data = analyze_with_groq(files)

    # Add repository metadata to report overview.
    report_data["overview"]["repository"] = repo["full_name"]
    report_data["overview"]["branch"] = payload.branch

    # Save report in database.
    report = AnalysisReport(
        user_id=current_user.id,
        github_repo_id=payload.github_repo_id,
        repo_full_name=repo["full_name"],
        branch=payload.branch,
        status="completed",
        report_data=report_data,
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "report_id": report.id,
        "status": report.status,
        "repository": report.repo_full_name,
        "branch": report.branch,
        "files_analyzed": len(files)
    }


# ------------------------- GET ANALYSIS REPORT -------------------------

@router.get("/{report_id}")
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    report = db.query(AnalysisReport).filter(
        AnalysisReport.id == report_id,
        AnalysisReport.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Analysis report not found"
        )

    return {
        "id": report.id,
        "repository": report.repo_full_name,
        "branch": report.branch,
        "status": report.status,
        "created_at": report.created_at,
        "report": report.report_data,
    }


# ------------------------- ANALYSIS HISTORY -------------------------

@router.get("/history/list")
def history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):

    limit = min(max(limit, 1), 100)
    offset = max(offset, 0)

    reports = (
        db.query(AnalysisReport)
        .filter(AnalysisReport.user_id == current_user.id)
        .order_by(AnalysisReport.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": r.id,
            "repository": r.repo_full_name,
            "branch": r.branch,
            "status": r.status,
            "created_at": r.created_at
        }
        for r in reports
    ]
