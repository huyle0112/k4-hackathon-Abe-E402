from fastapi import APIRouter, Request

router = APIRouter(tags=["system"])


@router.get("/health")
def health(request: Request) -> dict[str, object]:
    service_ready = hasattr(request.app.state, "rag_service")
    return {"status": "ok" if service_ready else "starting"}
