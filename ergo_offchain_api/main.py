from fastapi import FastAPI
from ergo_offchain_api.routes.filter import filter_router
from ergo_offchain_api.routes.config import config_router
import uvicorn
import logging

levelname = logging.DEBUG
logging.basicConfig(format='{asctime}:{name:>8s}:{levelname:<8s}::{message}', style='{', level=levelname)

app = FastAPI(
    title="Ergo Off-chain Execution",
    docs_url="/api/docs",
    openapi_url="/api"
)

app.include_router(config_router, prefix="/api/config", tags=["config"])
app.include_router(filter_router, prefix="/api/filter", tags=["filter"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)