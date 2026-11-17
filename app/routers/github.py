from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.github_account import GitHubAccount
from app.services.github_service import build_authorization_url, exchange_code, github_get
from app.utils.oauth_state import create_oauth_state, verify_oauth_state
from app.utils.security import encrypt_secret, decrypt_secret

router = APIRouter(prefix="/github", tags=["GitHub"])

def get_account(db: Session, user_id: int) -> GitHubAccount:
    account = db.query(GitHubAccount).filter(GitHubAccount.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="GitHub account is not connected")
    return account

@router.get("/connect")
def connect(current_user: User = Depends(get_current_user)):
    state = create_oauth_state(current_user.id)
    return {"authorization_url": build_authorization_url(state), "message": "Open authorization_url in a browser"}



@router.get("/callback")
def callback(code: str = Query(min_length=1, max_length=500), state: str = Query(min_length=20, max_length=1000), db: Session = Depends(get_db)):
    try:
        user_id = verify_oauth_state(state)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="OAuth user is unavailable")
    token = exchange_code(code)
    profile = github_get("/user", token)
    account = db.query(GitHubAccount).filter(GitHubAccount.user_id == user_id).first()
    if account is None:
        account = GitHubAccount(user_id=user_id, github_user_id=profile["id"], github_username=profile["login"], encrypted_access_token=encrypt_secret(token))
        db.add(account)
    else:
        account.github_user_id = profile["id"]
        account.github_username = profile["login"]
        account.encrypted_access_token = encrypt_secret(token)
    db.commit()
    return {"message": "GitHub account connected", "github_username": profile["login"], "next": "Return to Postman and call GET /api/v1/github/repositories"}


@router.get("/repositories")
def repositories(
    page: int = Query(default=1, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    account = get_account(db, current_user.id)
    token = decrypt_secret(account.encrypted_access_token)

    repos = github_get(
        "/user/repos",
        token,
        {
            "per_page": 100,
            "page": page,
            "sort": "updated",
            "affiliation": "owner,collaborator,organization_member"
        }
    )

    return [
        {
            "id": repo["id"],
            "name": repo["name"],
            "full_name": repo["full_name"],
            "private": repo["private"],
            "default_branch": repo["default_branch"]
        }
        for repo in repos
    ]
@router.get("/repositories/{repo_id}/branches")
def branches(repo_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if repo_id <= 0:
        raise HTTPException(status_code=422, detail="Repository ID must be positive")
    account = get_account(db, current_user.id)
    token = decrypt_secret(account.encrypted_access_token)
    repos = github_get("/user/repos", token, {"per_page": 100, "affiliation": "owner,collaborator,organization_member"})
    # next() returns the first matching repository.  find the selected repository from the repos list.
    repo = next((r for r in repos if r["id"] == repo_id), None)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found or not accessible")
    # f-string. It dynamically inserts the repository owner's username and repository name.
    return github_get(f"/repos/{repo['owner']['login']}/{repo['name']}/branches", token, {"per_page": 100})
