"""AI integration for Numen."""

import json
from typing import Dict, List, Optional, Union

import anthropic
import openai
import requests
import google.generativeai as genai
from rich.console import Console

from numen.config import get_ai_config
from numen.utils import optimize_large_content

console = Console()

EXPAND_PROMPT = """You're a professional writer. Expand on the following text into 2–3 cohesive paragraphs of prose while keeping the original voice and tone. Return only the expanded text without any explanations:

{selected_text}
"""

SUMMARIZE_PROMPT = """Summarize the following note into bullet points with key takeaways. Keep technical details if present. Return only the summary without any explanations:

{note}
"""

POETIC_PROMPT = """Rewrite this text in the form of a metaphorical poem, keeping the meaning but transforming the tone. Return only the poem without any explanations:

{selected_text}
"""


class AIProvider:
    """Base class for AI providers."""
    
    def __init__(self) -> None:
        self.config = get_ai_config()
        self.max_content_size = 100000
    
    def expand(self, text: str) -> str:
        """Expand the given text."""
        optimized_text = optimize_large_content(text, self.max_content_size)
        prompt = EXPAND_PROMPT.format(selected_text=optimized_text)
        return self.generate_text(prompt)
    
    def summarize(self, text: str) -> str:
        """Summarize the given text."""
        optimized_text = optimize_large_content(text, self.max_content_size)
        prompt = SUMMARIZE_PROMPT.format(note=optimized_text)
        return self.generate_text(prompt)
    
    def poetic(self, text: str) -> str:
        """Transform the given text into poetry."""
        optimized_text = optimize_large_content(text, self.max_content_size)
        prompt = POETIC_PROMPT.format(selected_text=optimized_text)
        return self.generate_text(prompt)
    
    def generate_text(self, prompt: str) -> str:
        """Generate text from a prompt. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement generate_text")


class AnthropicProvider(AIProvider):
    """Provider for Anthropic Claude."""
    
    def __init__(self) -> None:
        super().__init__()
        api_key = self.config.get("anthropic_api_key", "")
        if not api_key:
            console.print("[red]Error: Anthropic API key is missing. Run 'numen config' to add your API key.")
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate_text(self, prompt: str) -> str:
        """Generate text using Anthropic Claude."""
        if not self.config.get("anthropic_api_key"):
            return "Error: Anthropic API key is missing. Run 'numen config' to add your API key."
            
        try:
            message = self.client.messages.create(
                model=self.config.get("default_model", "claude-3-sonnet-20240229"),
                max_tokens=1024,
                temperature=self.config.get("temperature", 0.7),
                system="You are a helpful writing assistant that helps expand, summarize, or transform text.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg:
                return "Error: Invalid Anthropic API key. Please check your API key in 'numen config'."
            elif "429" in error_msg:
                return "Error: Rate limit exceeded. Please try again later."
            else:
                console.print(f"[red]Error generating text with Anthropic: {e}")
                return f"Error: {error_msg}"


class OpenAIProvider(AIProvider):
    """Provider for OpenAI GPT models."""
    
    def __init__(self) -> None:
        super().__init__()
        api_key = self.config.get("openai_api_key", "")
        if not api_key:
            console.print("[red]Error: OpenAI API key is missing. Run 'numen config' to add your API key.")
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_text(self, prompt: str) -> str:
        """Generate text using OpenAI GPT."""
        if not self.config.get("openai_api_key"):
            return "Error: OpenAI API key is missing. Run 'numen config' to add your API key."
            
        try:
            model = self.config.get("default_model", "gpt-4-turbo")
            if "gpt" not in model.lower():
                model = "gpt-4-turbo"
                
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful writing assistant that helps expand, summarize, or transform text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get("temperature", 0.7),
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "authentication" in error_msg.lower():
                return "Error: Invalid OpenAI API key. Please check your API key in 'numen config'."
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                return "Error: Rate limit exceeded. Please try again later."
            else:
                console.print(f"[red]Error generating text with OpenAI: {e}")
                return f"Error: {error_msg}"


class OllamaProvider(AIProvider):
    """Provider for Ollama local LLMs."""
    
    def __init__(self) -> None:
        super().__init__()
        self.base_url = self.config.get("ollama_base_url", "http://localhost:11434")
    
    def generate_text(self, prompt: str) -> str:
        """Generate text using Ollama."""
        try:
            model = self.config.get("default_model", "llama3")
            if "claude" in model.lower() or "gpt" in model.lower():
                model = "llama3"
                
            data = {
                "model": model,
                "prompt": f"You are a helpful writing assistant that helps expand, summarize, or transform text.\n\n{prompt}",
                "temperature": self.config.get("temperature", 0.7),
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Error: No response from Ollama")
            else:
                console.print(f"[red]Error generating text with Ollama: {response.status_code}")
                return f"Error: HTTP {response.status_code}"
        except Exception as e:
            console.print(f"[red]Error generating text with Ollama: {e}")
            return f"Error: {str(e)}"


class GeminiProvider(AIProvider):
    """Provider for Google's Gemini AI."""
    
    def __init__(self) -> None:
        super().__init__()
        api_key = self.config.get("gemini_api_key", "")
        if not api_key:
            console.print("[red]Error: Gemini API key is missing. Run 'numen config' to add your API key.")
            
        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            console.print(f"[red]Error configuring Gemini: {e}")
    
    def generate_text(self, prompt: str) -> str:
        """Generate text using Google's Gemini AI."""
        if not self.config.get("gemini_api_key"):
            return "Error: Gemini API key is missing. Run 'numen config' to add your API key."
            
        try:
            model_name = self.config.get("default_model", "gemini-1.5-pro")
            if "gemini" not in model_name.lower():
                model_name = "gemini-1.5-pro"
            
            model = genai.GenerativeModel(model_name)
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.get("temperature", 0.7),
                    max_output_tokens=1024,
                )
            )
            
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "api key" in error_msg.lower():
                return "Error: Invalid Gemini API key. Please check your API key in 'numen config'."
            elif "429" in error_msg or "quota" in error_msg.lower():
                return "Error: Rate limit or quota exceeded. Please try again later."
            else:
                console.print(f"[red]Error generating text with Gemini: {e}")
                return f"Error: {error_msg}"


def get_ai_provider() -> AIProvider:
    """Get the configured AI provider."""
    config = get_ai_config()
    provider_name = config.get("default_provider", "anthropic").lower()
    
    if provider_name == "anthropic":
        return AnthropicProvider()
    elif provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "ollama":
        return OllamaProvider()
    elif provider_name == "gemini":
        return GeminiProvider()
    else:
        console.print(f"[yellow]Unknown provider '{provider_name}', falling back to Anthropic")
        return AnthropicProvider()


def process_text(action: str, text: str) -> str:
    """Process text with the configured AI provider."""
    provider = get_ai_provider()
    
    if action == "expand":
        return provider.expand(text)
    elif action == "summarize":
        return provider.summarize(text)
    elif action == "poetic":
        return provider.poetic(text)
    else:
        return f"Unknown action: {action}"
