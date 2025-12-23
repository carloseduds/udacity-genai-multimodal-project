from fastapi import APIRouter
from multimodal_moderation.agents.text_agent import moderate_text
from multimodal_moderation.types.moderation_result import TextModerationResult
from multimodal_moderation.env import get_default_model_choice
from multimodal_moderation.types.requests import TextRequest


router = APIRouter()


@router.post("/moderate_text", response_model=TextModerationResult)
async def moderate_text_endpoint(request: TextRequest):
    return await moderate_text(get_default_model_choice(), request.text)