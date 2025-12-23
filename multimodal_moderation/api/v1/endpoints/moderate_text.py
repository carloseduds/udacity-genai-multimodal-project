import logging
from multimodal_moderation.observability import get_trace_ids
from multimodal_moderation.env import get_default_model_choice
from multimodal_moderation.agents.text_agent import moderate_text
from multimodal_moderation.types.requests import TextRequest
from multimodal_moderation.types.moderation_result import TextModerationResult
from fastapi import APIRouter

router = APIRouter()
logger = logging.getLogger("multimodal_moderation.moderation")

@router.post("/moderate_text", response_model=TextModerationResult)
async def moderate_text_endpoint(request: TextRequest):
    model_choice = get_default_model_choice()  # <- chame a função
    result = await moderate_text(model_choice, request.text)

    decision = "unsafe" if (
        getattr(result, "contains_pii", False)
        or getattr(result, "is_unfriendly", False)
        or getattr(result, "is_unprofessional", False)
    ) else "safe"

    trace_id, span_id = get_trace_ids()

    logger.info(
        "moderation_result",
        extra={
            "content_type": "text",
            "decision": decision,
            "flags": {
                "contains_pii": getattr(result, "contains_pii", None),
                "is_unfriendly": getattr(result, "is_unfriendly", None),
                "is_unprofessional": getattr(result, "is_unprofessional", None),
            },
            "model_name": str(model_choice),
            "mime_type": "text/plain",
            "input_size_bytes": len(request.text.encode("utf-8")),
            "trace_id": trace_id,
            "span_id": span_id,
        },
    )
    return result
