import json
import httpx
import logging
from backend.core.config import settings

logger = logging.getLogger("study_planner_agents")


class LLMProvider:
    DEFAULT_TIMEOUT_SECS: float = 90.0
    DEFAULT_MAX_RETRIES: int = 0
    DEFAULT_BACKOFF_SECS: float = 0.5

    @staticmethod
    def generate(
        prompt: str,
        system_prompt: str = "You are a helpful study planner assistant.",
        json_mode: bool = False,
        provider: str | None = None,
        model: str | None = None,
        timeout_secs: float | None = None,
        max_retries: int | None = None,
    ) -> str:
        provider = provider or settings.DEFAULT_PROVIDER
        model = model or settings.DEFAULT_MODEL
        
        effective_timeout_secs = timeout_secs if timeout_secs is not None else LLMProvider.DEFAULT_TIMEOUT_SECS
        effective_max_retries = max_retries if max_retries is not None else LLMProvider.DEFAULT_MAX_RETRIES
        
        print("=" * 60)
        print("LLM GENERATE")
        print("Provider :", provider)
        print("Model    :", model)
        print("Timeout  :", effective_timeout_secs)
        print("Retries  :", effective_max_retries)
        print("Prompt Length:", len(prompt))
        print("=" * 60)
        logger.info(
            "Generating LLM response using provider=%s, model=%s, json_mode=%s",
            provider,
            model,
            json_mode,
        )

        

        timeout = httpx.Timeout(
            connect=15.0,
            read=effective_timeout_secs,
            write=effective_timeout_secs,
            pool=effective_timeout_secs,
        )

        last_err: Exception | None = None
        for attempt in range(effective_max_retries + 1):
            try:
                if provider == "gemini":
                    return LLMProvider._call_gemini(prompt, system_prompt, json_mode, model, timeout)
                if provider == "openai":
                    return LLMProvider._call_openai(prompt, system_prompt, json_mode, model, timeout)
                if provider == "ollama":
                    return LLMProvider._call_ollama(prompt, system_prompt, json_mode, model, timeout)
                if provider == "anthropic":
                    return LLMProvider._call_anthropic(prompt, system_prompt, json_mode, model, timeout)

                logger.warning("Unknown provider '%s'. Using mock fallback.", provider)
                return LLMProvider._mock_fallback(prompt, json_mode)
            except (httpx.TimeoutException, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                last_err = e
                logger.warning(
                    "LLM timeout (provider=%s model=%s) attempt %s/%s: %s",
                    provider,
                    model,
                    attempt + 1,
                    effective_max_retries + 1,
                    str(e),
                )
            except Exception as e:
                last_err = e
                logger.error(
                    "Error in LLM Generation with provider=%s model=%s attempt %s/%s: %s",
                    provider,
                    model,
                    attempt + 1,
                    effective_max_retries + 1,
                    str(e),
                )

            if attempt < effective_max_retries:
                try:
                    import time

                    time.sleep(LLMProvider.DEFAULT_BACKOFF_SECS)
                except Exception:
                    pass

        if provider != "ollama":
            logger.warning("Primary provider failed. Attempting fallback to Ollama...")
            try:
                return LLMProvider._call_ollama(prompt, system_prompt, json_mode, model="llama3", timeout=timeout)
            except Exception as ollama_err:
                logger.error("Ollama fallback failed: %s", str(ollama_err))

        if last_err:
            raise RuntimeError(f"LLM generation failed after retries: {str(last_err)}")
        raise RuntimeError("LLM generation failed after retries")

    @staticmethod
    def _call_gemini(prompt: str, system_prompt: str, json_mode: bool, model: str, timeout: httpx.Timeout) -> str:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
        }

        if json_mode:
            payload["generationConfig"] = {"responseMimeType": "application/json"}

        response = httpx.post(url, headers=headers, json=payload, timeout=timeout)
        if response.status_code != 200:
            raise RuntimeError(f"Gemini API error: {response.status_code} - {response.text}")

        res_data = response.json()
        try:
            return res_data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise RuntimeError(f"Unexpected response structure from Gemini API: {res_data}")

    @staticmethod
    def _call_openai(prompt: str, system_prompt: str, json_mode: bool, model: str, timeout: httpx.Timeout) -> str:
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        payload = {
            "model": model or "gpt-4o-mini",
            "messages": messages,
            "temperature": 0.7,
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        response = httpx.post(url, headers=headers, json=payload, timeout=timeout)
        if response.status_code != 200:
            raise RuntimeError(f"OpenAI API error: {response.status_code} - {response.text}")

        res_data = response.json()
        return res_data["choices"][0]["message"]["content"]

    @staticmethod
    def _call_ollama(
        prompt: str,
        system_prompt: str,
        json_mode: bool,
        model: str = "llama3.2:latest",
        timeout: httpx.Timeout | None = None,
    ) -> str:
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        headers = {"Content-Type": "application/json"}

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": settings.OLLAMA_NUM_PREDICT,
            },
        }

        if json_mode:
            payload["format"] = "json"
        print("=" * 60)
        print("PROMPT LENGTH:", len(prompt))
        print("SYSTEM LENGTH:", len(system_prompt))
        print("=" * 60)

        response = httpx.post(
            url,
            headers=headers,
            json=payload,
            timeout=timeout or httpx.Timeout(
    connect=30.0,
    read=300.0,
    write=300.0,
    pool=300.0,
),
        )
        response.raise_for_status()

        data = response.json()
        if "message" not in data:
            raise RuntimeError(f"Unexpected Ollama response: {data}")

        return data["message"]["content"]

    @staticmethod
    def _call_anthropic(
        prompt: str,
        system_prompt: str,
        json_mode: bool,
        model: str,
        timeout: httpx.Timeout,
    ) -> str:
        # Fallback until fully wired; avoids crashing if configured.
        raise NotImplementedError("Anthropic provider is not implemented in this project.")

    @staticmethod
    def _mock_fallback(prompt: str, json_mode: bool) -> str:
        if json_mode:
            return json.dumps(
                {
                    "status": "mock",
                    "message": "Please set up API keys (e.g. GEMINI_API_KEY) in backend .env file.",
                    "data": {},
                }
            )
        return "Mock response. Please set up API keys in the backend .env file."
