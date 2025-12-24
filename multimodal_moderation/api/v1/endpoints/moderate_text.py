import logging

from fastapi import APIRouter

from multimodal_moderation.observability import get_trace_ids
from multimodal_moderation.env import get_default_model_choice
from multimodal_moderation.agents.text_agent import moderate_text
from multimodal_moderation.types.requests import TextRequest
from multimodal_moderation.types.moderation_result import TextModerationResult
from multimodal_moderation.analytics_store import STORE

router = APIRouter()
logger = logging.getLogger("multimodal_moderation.moderation")

@router.post("/moderate_text", response_model=TextModerationResult)
async def moderate_text_endpoint(request: TextRequest):
    model_choice = get_default_model_choice()
    result = await moderate_text(model_choice, request.text)

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
            "content_type": "text",
            "decision": "unsafe" if any(v is True for v in flags.values()) else "safe",
            "flags": flags,
            "model_name": str(model_choice),
            "mime_type": "text/plain",
            "input_size_bytes": len(request.text.encode("utf-8")),
            "trace_id": trace_id,
            "span_id": span_id,
        }

    logger.info(
        "moderation_result",
        extra=extra,
    )

    STORE.add(**extra)
    return result
