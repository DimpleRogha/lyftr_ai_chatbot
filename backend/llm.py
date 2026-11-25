import os
from dotenv import load_dotenv
from litellm import Router

load_dotenv()

MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/google/gemma-3-27b-it")

model_list = [
    {
        "model_name": "lyftr-key-1",
        "litellm_params": {
            "model": MODEL,
            "api_key": os.getenv("OPENROUTER_API_KEY_1")
        }
    },
    {
        "model_name": "lyftr-key-2",
        "litellm_params": {
            "model": MODEL,
            "api_key": os.getenv("OPENROUTER_API_KEY_2")
        }
    }
]

router = Router(
    model_list=model_list,
    num_retries=0,
    cache_responses=True
)


def get_ai_response(messages, simulated_failure=None):
    failures = {}

    if simulated_failure:
        for item in simulated_failure.split(","):
            if "=" in item:
                key, status = item.split("=", 1)
                failures[key.strip()] = status.strip()

    last_error = None

    for index, (model_name, key_id) in enumerate([
        ("lyftr-key-1", "key_1"),
        ("lyftr-key-2", "key_2")
    ]):
        if key_id in failures or "*" in failures:
            last_error = Exception(
                f"Simulated failure: {failures.get(key_id, failures.get('*'))}"
            )
            continue

        try:
            response = router.completion(
                model=model_name,
                messages=messages,
                temperature=0.7,
                timeout=20
            )

            cache_hit = response._hidden_params.get("cache_hit", False)

            return response, cache_hit, (
                None if cache_hit else key_id
            ), index

        except Exception as error:
            last_error = error

    raise last_error or Exception("All providers unavailable")