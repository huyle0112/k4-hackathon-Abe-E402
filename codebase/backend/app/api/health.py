from fastapi import APIRouter, Request

router = APIRouter(tags=["system"])


@router.get("/health")
def health(request: Request) -> dict[str, object]:
    return {"status": "ok", "indexed_chunks": request.app.state.store.count}
