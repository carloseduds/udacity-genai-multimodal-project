import logging

from fastapi import APIRouter, File, UploadFile

from multimodal_moderation.agents.image_agent import moderate_image
from multimodal_moderation.types.moderation_result import ImageModerationResult
from multimodal_moderation.utils import detect_file_type
from multimodal_moderation.env import get_default_model_choice
from multimodal_moderation.observability import get_trace_ids

router = APIRouter()
logger = logging.getLogger("multimodal_moderation.moderation")

@router.post("/moderate_image_file", response_model=ImageModerationResult)
async def moderate_image_file_endpoint(file: UploadFile = File(...)):
    file_bytes = await file.read()
    mime_type = detect_file_type(file_bytes, context=file.filename or "image file")
    result =  await moderate_image(get_default_model_choice(), file_bytes, mime_type)
    
    trace_id, span_id = get_trace_ids()

    logger.info(
        "moderation_result",
        extra={
            "content_type": "image",
            "decision": "unsafe" if (result.contains_pii or result.is_disturbing or result.is_low_quality) else "safe",
            "flags": {"contains_pii": result.contains_pii, "is_disturbing": result.is_disturbing, "is_low_quality": result.is_low_quality},
            "model_name": str(get_default_model_choice()),
            "mime_type": mime_type,
            "input_size_bytes": len(file_bytes),
            "trace_id": trace_id,
            "span_id": span_id,
        }
    )
    
    return result
  