from functools import lru_cache
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider
from multimodal_moderation.env import GEMINI_API_KEY, DEFAULT_GOOGLE_MODEL


BASE_PROMPT = """
ROLE
You are an ACME Enterprise customer.

TASK
You are contacting customer service about an issue with your ACME Power Widget Pro product.
You want a resolution (refund or replacement), but you may accept alternatives if handled well.

STYLE
Keep responses short and realistic. Do not reveal you are an AI.
"""

PERSONAS = {
    "angry": """
PERSONA: Angry and impatient.
- Use short, sharp sentences.
- Escalate if the agent is vague.
- Calm down only if agent is polite and concrete.
""",
    "anxious": """
PERSONA: Anxious and worried.
- Ask for reassurance.
- Concerned about money/time.
- Calms down with empathy and clear steps.
""",
    "sarcastic": """
PERSONA: Sarcastic and cynical.
- Use mild sarcasm (no hate, no slurs).
- Tests whether the agent is truly helpful.
""",
    "calm": """
PERSONA: Calm but firm.
- Professional tone.
- Focused on policy and next steps.
""",
}

SCENARIOS = {
    "refund": "SCENARIO: The product shut down unexpectedly. You want a refund.",
    "shipping_delay": "SCENARIO: Your order is delayed beyond the promised date.",
    "billing_issue": "SCENARIO: You were charged twice for the same order.",
}

gemini_model = GoogleModel(DEFAULT_GOOGLE_MODEL, provider=GoogleProvider(api_key=GEMINI_API_KEY))
model_settings = GoogleModelSettings(google_thinking_config={"thinking_budget": 0})

@lru_cache(maxsize=32)
def get_customer_agent(persona: str = "angry", scenario: str = "refund") -> Agent:
    persona_block = PERSONAS.get(persona, PERSONAS["angry"])
    scenario_block = SCENARIOS.get(scenario, SCENARIOS["refund"])
    system_prompt = "\n\n".join([BASE_PROMPT, scenario_block, persona_block])

    return Agent(
        system_prompt=system_prompt,
        output_type=str,
        model=gemini_model,
        model_settings=model_settings,
        instrument=True,
    )
