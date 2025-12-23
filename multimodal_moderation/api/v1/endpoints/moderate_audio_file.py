import logging

from fastapi import APIRouter, File, UploadFile
from multimodal_moderation.agents.audio_agent import moderate_audio
from multimodal_moderation.types.moderation_result import AudioModerationResult
from multimodal_moderation.utils import detect_file_type
from multimodal_moderation.env import get_default_model_choice
from multimodal_moderation.observability import get_trace_ids

router = APIRouter()
logger = logging.getLogger("multimodal_moderation.moderation")


@router.post("/moderate_audio_file", response_model=AudioModerationResult)
async def moderate_audio_file_endpoint(file: UploadFile = File(...)):
    file_bytes = await file.read()
    mime_type = detect_file_type(file_bytes, context=file.filename or "audio file")
    result =  await moderate_audio(get_default_model_choice(), file_bytes, mime_type)
    
    trace_id, span_id = get_trace_ids()

    logger.info(
        "moderation_result",
        extra={
            "content_type": "audio",
            "decision": "unsafe" if (result.contains_pii or result.is_unfriendly or result.is_unprofessional) else "safe",
            "flags": {"contains_pii": result.contains_pii, "is_unfriendly": result.is_unfriendly, "is_unprofessional": result.is_unprofessional},
            "model_name": str(get_default_model_choice()),
            "mime_type": mime_type,
            "input_size_bytes": len(file_bytes),
            "trace_id": trace_id,
            "span_id": span_id,
        }
    )
    
    return result
  