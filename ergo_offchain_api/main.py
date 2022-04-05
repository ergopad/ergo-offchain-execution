from fastapi import FastAPI
from ergo_offchain_api.routes.filter import filter_router
import uvicorn

app = FastAPI(
    title="Ergo Off-chain Execution",
    docs_url="/api/docs",
    openapi_url="/api"
)

app.include_router(filter_router,       prefix="/api/filter",       tags=["filter"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)