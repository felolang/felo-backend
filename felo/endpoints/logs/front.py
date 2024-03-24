import google.cloud.logging
from fastapi import APIRouter, Body

from felo.schemas.logs import PostLogsIn

client = google.cloud.logging.Client()
logger = client.logger(name="front_logs")

api_router = APIRouter(
    prefix="/logs",
    tags=["logs"],
)


@api_router.post("/")
async def send_logs(
    logs: PostLogsIn = Body(...),
):
    logger.log(
        logs.message,
        severity=logs.level.value,
        resource={"type": "global", "labels": {"front": logs.level.value}},
    )
