from fastapi import UploadFile, File
from fastapi import APIRouter

from multimodal_moderation.agents.video_agent import moderate_video
from multimodal_moderation.types.moderation_result import VideoModerationResult
from multimodal_moderation.utils import detect_file_type  
from multimodal_moderation.env import get_default_model_choice

router = APIRouter()


@router.post("/moderate_video_file", response_model=VideoModerationResult)
async def moderate_video_file_endpoint(file: UploadFile = File(...)):
    file_bytes = await file.read()
    mime_type = detect_file_type(file_bytes, context=file.filename or "video file")
    return await moderate_video(get_default_model_choice(), file_bytes, mime_type)
