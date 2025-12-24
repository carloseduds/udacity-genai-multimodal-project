import logging

from fastapi import APIRouter, File, UploadFile

from multimodal_moderation.agents.image_agent import moderate_image
from multimodal_moderation.types.moderation_result import ImageModerationResult
from multimodal_moderation.utils import detect_file_type
from multimodal_moderation.env import get_default_model_choice
from multimodal_moderation.observability import get_trace_ids
from multimodal_moderation.analytics_store import STORE

router = APIRouter()
logger = logging.getLogger("multimodal_moderation.moderation")


@router.post("/moderate_image_file", response_model=ImageModerationResult)
async def moderate_image_file_endpoint(file: UploadFile = File(...)):
    model_choice = get_default_model_choice()
    file_bytes = await file.read()
    mime_type = detect_file_type(file_bytes, context=file.filename or "image file")
    result =  await moderate_image(model_choice, file_bytes, mime_type)
    
    trace_id, span_id = get_trace_ids()

    flags = {
        "contains_pii": getattr(result, "contains_pii", None),
        "is_disturbing": getattr(result, "is_disturbing", None),
        "is_low_quality": getattr(result, "is_low_quality", None),
    }
    
    extra = {
            "content_type": "image",
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
        extra=extra,
    )

    STORE.add(**extra)
    return result
