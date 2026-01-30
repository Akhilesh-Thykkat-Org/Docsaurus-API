from fastapi import FastAPI
from app.api.docs import router as docs_router

app = FastAPI(title="Docs Automation API")

app.include_router(docs_router)
