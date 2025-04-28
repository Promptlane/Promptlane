from ...models.llm_model import LLMModel

anthropic_models = [
    # Claude 3.7 Sonnet
    LLMModel(
        model_id="claude-3-7-sonnet-20250219",
        provider="Anthropic",
        name="Claude 3.7 Sonnet",
        model_type="text",
        description="Anthropic's most intelligent model. Highest level of intelligence and capability with toggleable extended thinking.",
        context_length=200000,
        completion_length=64000,
        prompt_price=3.00,
        completion_price=15.00,
        tags="chat,completion"
    ),
    # Claude 3.5 Sonnet (latest version)
    LLMModel(
        model_id="claude-3-5-sonnet-20241022",
        provider="Anthropic",
        name="Claude 3.5 Sonnet",
        model_type="text",
        description="Anthropic's previous most intelligent model. High level of intelligence and capability.",
        context_length=200000,
        completion_length=8192,
        prompt_price=3.00,
        completion_price=15.00,
        tags="chat,completion"
    ),
    # Claude 3.5 Haiku
    LLMModel(
        model_id="claude-3-5-haiku-20241022",
        provider="Anthropic",
        name="Claude 3.5 Haiku",
        model_type="text",
        description="Anthropic's fastest model. Intelligence at blazing speeds.",
        context_length=200000,
        completion_length=8192,
        prompt_price=0.80,
        completion_price=4.00,
        tags="chat,completion"
    ),
    # Claude 3 Opus
    LLMModel(
        model_id="claude-3-opus-20240229",
        provider="Anthropic",
        name="Claude 3 Opus",
        model_type="text",
        description="Powerful model for complex tasks. Top-level intelligence, fluency, and understanding.",
        context_length=200000,
        completion_length=4096,
        prompt_price=15.00,
        completion_price=75.00,
        tags="chat,completion"
    ),
    # Claude 3 Haiku
    LLMModel(
        model_id="claude-3-haiku-20240307",
        provider="Anthropic",
        name="Claude 3 Haiku",
        model_type="text",
        description="Fastest and most compact model for near-instant responsiveness. Quick and accurate targeted performance.",
        context_length=200000,
        completion_length=4096,
        prompt_price=0.25,
        completion_price=1.25,
        tags="chat,completion"
    ),
]
