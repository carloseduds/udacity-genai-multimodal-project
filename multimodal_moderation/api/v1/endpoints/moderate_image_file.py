from fastapi import APIRouter, File, UploadFile

from multimodal_moderation.agents.image_agent import moderate_image
from multimodal_moderation.types.moderation_result import ImageModerationResult
from multimodal_moderation.utils import detect_file_type
from multimodal_moderation.env import get_default_model_choice

router = APIRouter()


@router.post("/moderate_image_file", response_model=ImageModerationResult)
async def moderate_image_file_endpoint(file: UploadFile = File(...)):
    file_bytes = await file.read()
    mime_type = detect_file_type(file_bytes, context=file.filename or "image file")
    return await moderate_image(get_default_model_choice(), file_bytes, mime_type)
  