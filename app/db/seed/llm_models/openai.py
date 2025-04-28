from ...models.llm_model import LLMModel

openai_models = [
    # GPT-4.1
    LLMModel(
        model_id="gpt-4.1-2025-04-14",
        provider="OpenAI",
        name="GPT-4.1",
        model_type="text",
        description="OpenAI GPT-4.1 model (2025-04-14)",
        context_length=None,
        completion_length=None,
        prompt_price=2.00,
        completion_price=8.00,
        tags="chat,completion"
    ),
    # GPT-4.1 Mini
    LLMModel(
        model_id="gpt-4.1-mini-2025-04-14",
        provider="OpenAI",
        name="GPT-4.1 Mini",
        model_type="text",
        description="OpenAI GPT-4.1 Mini model (2025-04-14)",
        context_length=None,
        completion_length=None,
        prompt_price=0.40,
        completion_price=1.60,
        tags="chat,completion"
    ),
    # GPT-4.1 Nano
    LLMModel(
        model_id="gpt-4.1-nano-2025-04-14",
        provider="OpenAI",
        name="GPT-4.1 Nano",
        model_type="text",
        description="OpenAI GPT-4.1 Nano model (2025-04-14)",
        context_length=None,
        completion_length=None,
        prompt_price=0.10,
        completion_price=0.40,
        tags="chat,completion"
    ),
    # GPT-4.5 Preview
    LLMModel(
        model_id="gpt-4.5-preview-2025-02-27",
        provider="OpenAI",
        name="GPT-4.5 Preview",
        model_type="text",
        description="OpenAI GPT-4.5 Preview model (2025-02-27)",
        context_length=None,
        completion_length=None,
        prompt_price=75.00,
        completion_price=150.00,
        tags="chat,completion"
    ),
    # GPT-4o (multiple versions)
    LLMModel(
        model_id="gpt-4o-2024-08-06",
        provider="OpenAI",
        name="GPT-4o",
        model_type="text",
        description="OpenAI GPT-4o model (2024-08-06)",
        context_length=None,
        completion_length=None,
        prompt_price=2.50,
        completion_price=10.00,
        tags="chat,completion"
    ),
    LLMModel(
        model_id="gpt-4o-2024-11-20",
        provider="OpenAI",
        name="GPT-4o",
        model_type="text",
        description="OpenAI GPT-4o model (2024-11-20)",
        context_length=None,
        completion_length=None,
        prompt_price=2.50,
        completion_price=10.00,
        tags="chat,completion"
    ),
    LLMModel(
        model_id="gpt-4o-2024-05-13",
        provider="OpenAI",
        name="GPT-4o",
        model_type="text",
        description="OpenAI GPT-4o model (2024-05-13)",
        context_length=None,
        completion_length=None,
        prompt_price=5.00,
        completion_price=15.00,
        tags="chat,completion"
    ),
    # GPT-4o Mini
    LLMModel(
        model_id="gpt-4o-mini-2024-07-18",
        provider="OpenAI",
        name="GPT-4o Mini",
        model_type="text",
        description="OpenAI GPT-4o Mini model (2024-07-18)",
        context_length=None,
        completion_length=None,
        prompt_price=0.15,
        completion_price=0.60,
        tags="chat,completion"
    ),
    # GPT-4o Mini Search Preview
    LLMModel(
        model_id="gpt-4o-mini-search-preview-2025-03-11",
        provider="OpenAI",
        name="GPT-4o Mini Search Preview",
        model_type="text",
        description="OpenAI GPT-4o Mini Search Preview model (2025-03-11)",
        context_length=None,
        completion_length=None,
        prompt_price=0.15,
        completion_price=0.60,
        tags="chat,completion"
    ),
    # GPT-4o Search Preview
    LLMModel(
        model_id="gpt-4o-search-preview-2025-03-11",
        provider="OpenAI",
        name="GPT-4o Search Preview",
        model_type="text",
        description="OpenAI GPT-4o Search Preview model (2025-03-11)",
        context_length=None,
        completion_length=None,
        prompt_price=2.50,
        completion_price=10.00,
        tags="chat,completion"
    ),
    # chatgpt-4o-latest
    LLMModel(
        model_id="chatgpt-4o-latest",
        provider="OpenAI",
        name="ChatGPT-4o Latest",
        model_type="text",
        description="OpenAI ChatGPT-4o Latest",
        context_length=None,
        completion_length=None,
        prompt_price=5.00,
        completion_price=15.00,
        tags="chat,completion"
    ),
    # gpt-4-turbo-2024-04-09
    LLMModel(
        model_id="gpt-4-turbo-2024-04-09",
        provider="OpenAI",
        name="GPT-4 Turbo",
        model_type="text",
        description="OpenAI GPT-4 Turbo (2024-04-09)",
        context_length=None,
        completion_length=None,
        prompt_price=10.00,
        completion_price=30.00,
        tags="chat,completion"
    ),
    # gpt-4-turbo
    LLMModel(
        model_id="gpt-4-turbo",
        provider="OpenAI",
        name="GPT-4 Turbo",
        model_type="text",
        description="OpenAI GPT-4 Turbo",
        context_length=None,
        completion_length=None,
        prompt_price=10.00,
        completion_price=30.00,
        tags="chat,completion"
    ),
    # gpt-4-0125-preview
    LLMModel(
        model_id="gpt-4-0125-preview",
        provider="OpenAI",
        name="GPT-4 0125 Preview",
        model_type="text",
        description="OpenAI GPT-4 0125 Preview",
        context_length=None,
        completion_length=None,
        prompt_price=10.00,
        completion_price=30.00,
        tags="chat,completion"
    ),
    # gpt-4-1106-preview
    LLMModel(
        model_id="gpt-4-1106-preview",
        provider="OpenAI",
        name="GPT-4 1106 Preview",
        model_type="text",
        description="OpenAI GPT-4 1106 Preview",
        context_length=None,
        completion_length=None,
        prompt_price=10.00,
        completion_price=30.00,
        tags="chat,completion"
    ),
    # gpt-4-0613
    LLMModel(
        model_id="gpt-4-0613",
        provider="OpenAI",
        name="GPT-4 0613",
        model_type="text",
        description="OpenAI GPT-4 0613",
        context_length=None,
        completion_length=None,
        prompt_price=30.00,
        completion_price=60.00,
        tags="chat,completion"
    ),
    # gpt-4-0314
    LLMModel(
        model_id="gpt-4-0314",
        provider="OpenAI",
        name="GPT-4 0314",
        model_type="text",
        description="OpenAI GPT-4 0314",
        context_length=None,
        completion_length=None,
        prompt_price=30.00,
        completion_price=60.00,
        tags="chat,completion"
    ),
    # gpt-4-32k
    LLMModel(
        model_id="gpt-4-32k",
        provider="OpenAI",
        name="GPT-4 32k",
        model_type="text",
        description="OpenAI GPT-4 32k",
        context_length=None,
        completion_length=None,
        prompt_price=60.00,
        completion_price=120.00,
        tags="chat,completion"
    ),
    # gpt-3.5-turbo-0125
    LLMModel(
        model_id="gpt-3.5-turbo-0125",
        provider="OpenAI",
        name="GPT-3.5 Turbo 0125",
        model_type="text",
        description="OpenAI GPT-3.5 Turbo 0125",
        context_length=None,
        completion_length=None,
        prompt_price=0.50,
        completion_price=1.50,
        tags="chat,completion"
    ),
    # gpt-3.5-turbo
    LLMModel(
        model_id="gpt-3.5-turbo",
        provider="OpenAI",
        name="GPT-3.5 Turbo",
        model_type="text",
        description="OpenAI GPT-3.5 Turbo",
        context_length=None,
        completion_length=None,
        prompt_price=0.50,
        completion_price=1.50,
        tags="chat,completion"
    ),
    # gpt-3.5-turbo-1106
    LLMModel(
        model_id="gpt-3.5-turbo-1106",
        provider="OpenAI",
        name="GPT-3.5 Turbo 1106",
        model_type="text",
        description="OpenAI GPT-3.5 Turbo 1106",
        context_length=None,
        completion_length=None,
        prompt_price=1.00,
        completion_price=2.00,
        tags="chat,completion"
    ),
    # gpt-3.5-turbo-0613
    LLMModel(
        model_id="gpt-3.5-turbo-0613",
        provider="OpenAI",
        name="GPT-3.5 Turbo 0613",
        model_type="text",
        description="OpenAI GPT-3.5 Turbo 0613",
        context_length=None,
        completion_length=None,
        prompt_price=1.50,
        completion_price=2.00,
        tags="chat,completion"
    ),
    # gpt-3.5-0301
    LLMModel(
        model_id="gpt-3.5-0301",
        provider="OpenAI",
        name="GPT-3.5 0301",
        model_type="text",
        description="OpenAI GPT-3.5 0301",
        context_length=None,
        completion_length=None,
        prompt_price=1.50,
        completion_price=2.00,
        tags="chat,completion"
    ),
    # gpt-3.5-turbo-instruct
    LLMModel(
        model_id="gpt-3.5-turbo-instruct",
        provider="OpenAI",
        name="GPT-3.5 Turbo Instruct",
        model_type="text",
        description="OpenAI GPT-3.5 Turbo Instruct",
        context_length=None,
        completion_length=None,
        prompt_price=1.50,
        completion_price=2.00,
        tags="chat,completion"
    ),
    # gpt-3.5-turbo-16k-0613
    LLMModel(
        model_id="gpt-3.5-turbo-16k-0613",
        provider="OpenAI",
        name="GPT-3.5 Turbo 16k 0613",
        model_type="text",
        description="OpenAI GPT-3.5 Turbo 16k 0613",
        context_length=None,
        completion_length=None,
        prompt_price=3.00,
        completion_price=4.00,
        tags="chat,completion"
    ),
    # davinci-002
    LLMModel(
        model_id="davinci-002",
        provider="OpenAI",
        name="Davinci-002",
        model_type="text",
        description="OpenAI Davinci-002",
        context_length=None,
        completion_length=None,
        prompt_price=2.00,
        completion_price=2.00,
        tags="chat,completion"
    ),
    # babbage-002
    LLMModel(
        model_id="babbage-002",
        provider="OpenAI",
        name="Babbage-002",
        model_type="text",
        description="OpenAI Babbage-002",
        context_length=None,
        completion_length=None,
        prompt_price=0.40,
        completion_price=0.40,
        tags="chat,completion"
    ),
] 