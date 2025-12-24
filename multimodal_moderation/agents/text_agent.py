from pydantic_ai import Agent

from multimodal_moderation.types.model_choice import ModelChoice
from multimodal_moderation.types.moderation_result import ModerationResult, TextModerationResult

MODERATION_INSTRUCTIONS = """
<context>
At ACME enterprise we strive for a friendly but professional interaction with our customers.
</context>

<role>
You are a customer service reviewer at ACME enterprise. You make sure that the customer
service interactions are friendly and professional.
</role>

<input>
You will receive a message from the customer representative towards the customer.
</input>

<instructions>
Detect if the text contains:
- PII (emails, phone numbers, addresses, IDs, full names tied to identity)
- Unfriendly tone (insults, aggression, hostility)  
- Unprofessional content (slurs, sexual content, explicit language, threats)
- Hate speech / harassment (targeting protected groups or identity-based dehumanization)
- Spam / scam (unsolicited ads, repetitive promos, phishing-like requests, suspicious links/codes)
- Misinformation (confident false claims presented as facts; especially about policies, refunds, safety)
</instructions>

<output>
Provide a detailed rationale for your choices as well as a confidence score between 0 and 1 on your assessment.
</output>
"""


text_moderation_agent = Agent(
    instructions=MODERATION_INSTRUCTIONS,
    output_type=TextModerationResult,
)


async def moderate_text(model_choice: ModelChoice, text: str) -> TextModerationResult:
    moderation_result = await text_moderation_agent.run(
        [f"Moderate the following customer service message:\n\n{text}"],
        message_history=[],
        model=model_choice.model,
        model_settings=model_choice.model_settings,
    )
    return moderation_result.output
