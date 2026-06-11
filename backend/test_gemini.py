import asyncio, sys
sys.path.insert(0, ".")

from app.config import get_settings
get_settings.cache_clear()

from app.services.gemini_service import GeminiProvider

async def test():
    provider = GeminiProvider()
    settings = get_settings()
    print(f"Provider : {provider.provider_name()}")
    print(f"Model    : {settings.gemini_model}")
    print(f"API key  : {settings.gemini_api_key[:15]}...")
    print()

    result = await provider.generate(
        'Reply with exactly this JSON: {"status": "Gemini 2.5 Flash is working!"}',
        system_message="You are a test assistant. Always reply with valid JSON only.",
        max_tokens=60,
    )
    print("Response :", result.strip())
    print()
    print("SUCCESS: Gemini provider test PASSED!")

asyncio.run(test())
