from pydantic import BaseModel


class DocFileRequest(BaseModel):
    branch: str
    path: str
    content: str
    overwrite: bool = True


class PullRequestRequest(BaseModel):
    branch: str
    base: str = "main"
    title: str
    description: str
