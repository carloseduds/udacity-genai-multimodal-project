from fastapi import APIRouter, File, UploadFile
from multimodal_moderation.agents.audio_agent import moderate_audio
from multimodal_moderation.types.moderation_result import AudioModerationResult
from multimodal_moderation.utils import detect_file_type
from multimodal_moderation.env import get_default_model_choice

router = APIRouter()


@router.post("/moderate_audio_file", response_model=AudioModerationResult)
async def moderate_audio_file_endpoint(file: UploadFile = File(...)):
    file_bytes = await file.read()
    mime_type = detect_file_type(file_bytes, context=file.filename or "audio file")
    return await moderate_audio(get_default_model_choice(), file_bytes, mime_type)