import logging

from fastapi import APIRouter, File, UploadFile

from multimodal_moderation.agents.audio_agent import moderate_audio
from multimodal_moderation.types.moderation_result import AudioModerationResult
from multimodal_moderation.utils import detect_file_type
from multimodal_moderation.env import get_default_model_choice
from multimodal_moderation.observability import get_trace_ids
from multimodal_moderation.analytics_store import STORE

router = APIRouter()
logger = logging.getLogger("multimodal_moderation.moderation")


@router.post("/moderate_audio_file", response_model=AudioModerationResult)
async def moderate_audio_file_endpoint(file: UploadFile = File(...)):
    model_choice = get_default_model_choice()
    file_bytes = await file.read()
    mime_type = detect_file_type(file_bytes, context=file.filename or "audio file")
    result =  await moderate_audio(model_choice, file_bytes, mime_type)
    
    trace_id, span_id = get_trace_ids()

    flags = {
        "contains_pii": getattr(result, "contains_pii", None),
        "is_unfriendly": getattr(result, "is_unfriendly", None),
        "is_unprofessional": getattr(result, "is_unprofessional", None),
        "is_hate_speech": getattr(result, "is_hate_speech", None),
        "is_spam": getattr(result, "is_spam", None),
        "is_misinformation": getattr(result, "is_misinformation", None),
    }

    extra = {
            "content_type": "audio",
            "decision": "unsafe" if any(v is True for v in flags.values()) else "safe",
            "flags": flags,
            "model_name": str(model_choice),
            "mime_type": mime_type,
            "input_size_bytes": len(file_bytes),
            "trace_id": trace_id,
            "span_id": span_id,
        }

    logger.info(
        "moderation_result",
        extra=extra
    )

    STORE.add(**extra)
    return result
  