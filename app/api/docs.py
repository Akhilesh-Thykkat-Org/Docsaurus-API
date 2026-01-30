from fastapi import APIRouter, HTTPException
from app.schemas.docs import DocFileRequest, PullRequestRequest
from app.services.github import GitHubService

router = APIRouter(prefix="/docs", tags=["Docs"])


@router.post("/files")
def write_markdown(req: DocFileRequest):
    try:
        token = GitHubService.installation_token()
        GitHubService.ensure_branch(token, req.branch)

        result = GitHubService.upsert_file(
            token=token,
            branch=req.branch,
            path=req.path,
            content=req.content,
        )

        return {"status": "written", "commit": result["commit"]["sha"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pull-requests")
def create_pr(req: PullRequestRequest):
    try:
        token = GitHubService.installation_token()

        pr_url = GitHubService.open_pull_request(
            token=token,
            branch=req.branch,
            title=req.title,
            body=req.description,
        )

        return {"status": "created", "pull_request": pr_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
