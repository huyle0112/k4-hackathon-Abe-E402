from fastapi import APIRouter, Header, Request

from app.mindmaps import CreateMindmapRequest, MindmapResponse

router = APIRouter(tags=["mindmaps"])


@router.post("/mindmaps", response_model=MindmapResponse)
def create_mindmap(
    payload: CreateMindmapRequest,
    request: Request,
    x_user_id: str = Header(default="anonymous"),
) -> MindmapResponse:
    return request.app.state.mindmap_service.create(
        payload, user_id=x_user_id
    )
