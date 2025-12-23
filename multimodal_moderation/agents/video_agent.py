from pydantic_ai import Agent
from pydantic_ai.messages import BinaryContent

from multimodal_moderation.types.model_choice import ModelChoice
from multimodal_moderation.types.moderation_result import VideoModerationResult

MODERATION_INSTRUCTIONS = """
CONTEXT
At ACME Enterprise we strive for a friendly but professional interaction with our customers.

ROLE
You are a customer service reviewer at ACME Enterprise.

TASK
You will receive a video. Determine if it is appropriate for a professional customer service setting.

IMPORTANT RULES
- If you see ANY human face in ANY frame, set contains_pii=True.
- Treat any visible person (even partial face/head) as PII.
- If you are unsure whether a face/person appears (e.g., low resolution, brief appearance), err on the side of contains_pii=True.
- Do NOT infer; base your answer on what is visible/audible in the video.

CHECKLIST
1) Disturbing content:
   - Set is_disturbing=True if the video contains disturbing or unsafe content.
2) PII / Faces:
   - Set contains_pii=True if any face/person/identifying info appears (faces, name badges, IDs, addresses on screen, etc.).
3) Quality:
   - Set is_low_quality=True ONLY if low-quality footage makes up the majority of the video.

OUTPUT FORMAT
- Provide a detailed rationale.
- Explicitly state:
  (a) whether a face/person was detected and why,
  (b) why the video is or is not disturbing,
  (c) whether quality is low and whether it affects most of the video.
"""


video_moderation_agent = Agent(
    instructions=MODERATION_INSTRUCTIONS,
    output_type=VideoModerationResult,
)


async def moderate_video(
    model_choice: ModelChoice,
    video_source: bytes,
    media_type: str
) -> VideoModerationResult:

    video_input = BinaryContent(data=video_source, media_type=media_type)

    moderation_result = await video_moderation_agent.run(
        ["Check this video for: (1) faces/PII, (2) disturbing content, (3) majority low quality.", video_input],
        message_history=[],
        model=model_choice.model,
        model_settings=model_choice.model_settings,
    )

    return moderation_result.output
    