import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
import openai
import anthropic
import requests
import logging

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self):
        self._progress_callback: Optional[Callable[[int], None]] = None
    
    def set_progress_callback(self, callback: Optional[Callable[[int], None]]):
        """Set callback for progress updates."""
        self._progress_callback = callback
    
    def _report_progress(self, progress: int):
        """Report progress if callback is set."""
        if self._progress_callback:
            self._progress_callback(progress)
    
    @abstractmethod
    async def analyze_text(self, text: str, attitude_mode: str) -> Dict[str, Any]:
        """Analyze text and return counter-argument/fact-check."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get provider name."""
        pass

class OpenAIProvider(AIProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: str):
        super().__init__()
        self.client = openai.OpenAI(api_key=api_key)
    
    def get_name(self) -> str:
        return "OpenAI"
    
    def _get_system_prompt(self, attitude_mode: str) -> str:
        """Get system prompt based on attitude mode."""
        base_prompt = """You are an expert fact-checker and critical thinker. Your task is to analyze the provided text and provide a comprehensive response that includes:

1. Fact verification of claims made
2. Identification of logical fallacies or weak arguments
3. Counter-arguments or alternative perspectives
4. Confidence assessment of your analysis

Format your response as JSON with the following structure:
{
    "summary": "Brief summary of your analysis",
    "fact_check": {
        "verified_facts": ["List of verified facts"],
        "questionable_claims": ["List of questionable or false claims"],
        "sources_needed": ["Claims that need verification"]
    },
    "counter_arguments": ["List of counter-arguments or alternative perspectives"],
    "logical_fallacies": ["Any logical fallacies identified"],
    "confidence_score": 0.85,
    "recommendations": ["Suggestions for further research or consideration"]
}"""
        
        if attitude_mode == "argumentative":
            return base_prompt + "\n\nBe particularly aggressive in finding flaws and counter-arguments. Challenge every claim vigorously."
        elif attitude_mode == "helpful":
            return base_prompt + "\n\nBe constructive and educational. Focus on helping the user understand different perspectives."
        else:  # balanced
            return base_prompt + "\n\nProvide a balanced analysis that considers multiple viewpoints fairly."
    
    async def analyze_text(self, text: str, attitude_mode: str) -> Dict[str, Any]:
        """Analyze text using OpenAI API."""
        try:
            self._report_progress(25)
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_system_prompt(attitude_mode)},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            self._report_progress(75)
            
            content = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text if it fails
            try:
                result = json.loads(content)
                self._report_progress(100)
                return result
            except json.JSONDecodeError:
                self._report_progress(100)
                return {
                    "summary": content,
                    "confidence_score": 0.8,
                    "provider_used": self.get_name()
                }
                
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                "error": f"OpenAI API error: {str(e)}",
                "confidence_score": 0.0,
                "provider_used": self.get_name()
            }

class ClaudeProvider(AIProvider):
    """Anthropic Claude API provider."""
    
    def __init__(self, api_key: str):
        super().__init__()
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def get_name(self) -> str:
        return "Claude"
    
    def _get_system_prompt(self, attitude_mode: str) -> str:
        """Get system prompt based on attitude mode."""
        base_prompt = """You are an expert fact-checker and critical thinker. Analyze the provided text and provide a comprehensive response in JSON format with fact verification, counter-arguments, and confidence assessment."""
        
        if attitude_mode == "argumentative":
            return base_prompt + " Be particularly critical and challenge claims aggressively."
        elif attitude_mode == "helpful":
            return base_prompt + " Be constructive and educational in your analysis."
        else:  # balanced
            return base_prompt + " Provide a balanced and fair analysis."
    
    async def analyze_text(self, text: str, attitude_mode: str) -> Dict[str, Any]:
        """Analyze text using Claude API."""
        try:
            self._report_progress(25)
            
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                system=self._get_system_prompt(attitude_mode),
                messages=[
                    {"role": "user", "content": text}
                ]
            )
            
            self._report_progress(75)
            
            content = response.content[0].text
            
            # Try to parse as JSON, fallback to text if it fails
            try:
                result = json.loads(content)
                self._report_progress(100)
                return result
            except json.JSONDecodeError:
                self._report_progress(100)
                return {
                    "summary": content,
                    "confidence_score": 0.8,
                    "provider_used": self.get_name()
                }
                
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return {
                "error": f"Claude API error: {str(e)}",
                "confidence_score": 0.0,
                "provider_used": self.get_name()
            }

class OllamaProvider(AIProvider):
    """Ollama local AI provider."""
    
    def __init__(self, endpoint: str = "http://localhost:11434", model: str = "llama2"):
        super().__init__()
        self.endpoint = endpoint.rstrip('/')
        self.model = model
    
    def get_name(self) -> str:
        return f"Ollama ({self.model})"
    
    def _get_system_prompt(self, attitude_mode: str) -> str:
        """Get system prompt based on attitude mode."""
        base_prompt = """You are an expert fact-checker and critical thinker. Analyze the provided text for accuracy, logical consistency, and provide counter-arguments or alternative perspectives. Be thorough and objective."""
        
        if attitude_mode == "argumentative":
            return base_prompt + " Be particularly critical and challenge every claim aggressively."
        elif attitude_mode == "helpful":
            return base_prompt + " Be constructive and educational, helping the user understand different viewpoints."
        else:  # balanced
            return base_prompt + " Provide a balanced analysis considering multiple perspectives fairly."
    
    async def analyze_text(self, text: str, attitude_mode: str) -> Dict[str, Any]:
        """Analyze text using Ollama API."""
        try:
            self._report_progress(25)
            
            # Prepare the prompt
            system_prompt = self._get_system_prompt(attitude_mode)
            full_prompt = f"{system_prompt}\n\nText to analyze: {text}\n\nProvide your analysis:"
            
            # Make request to Ollama
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }
            
            self._report_progress(50)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.endpoint}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get('response', '')
                        
                        self._report_progress(100)
                        
                        # Try to parse as JSON, fallback to text
                        try:
                            parsed_result = json.loads(content)
                            return parsed_result
                        except json.JSONDecodeError:
                            return {
                                "summary": content,
                                "confidence_score": 0.7,
                                "provider_used": self.get_name()
                            }
                    else:
                        error_text = await response.text()
                        return {
                            "error": f"Ollama API error: {response.status} - {error_text}",
                            "confidence_score": 0.0,
                            "provider_used": self.get_name()
                        }
                        
        except asyncio.TimeoutError:
            return {
                "error": "Ollama request timed out",
                "confidence_score": 0.0,
                "provider_used": self.get_name()
            }
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return {
                "error": f"Ollama connection error: {str(e)}",
                "confidence_score": 0.0,
                "provider_used": self.get_name()
            }

class AIProviderManager:
    """Manages AI providers and handles fallbacks."""
    
    def __init__(self):
        self.providers = {}
    
    def add_provider(self, name: str, provider: AIProvider):
        """Add an AI provider."""
        self.providers[name] = provider
    
    def remove_provider(self, name: str):
        """Remove an AI provider."""
        if name in self.providers:
            del self.providers[name]
    
    async def analyze_with_fallback(self, text: str, attitude_mode: str, 
                                  primary_provider: str, 
                                  fallback_providers: List[str] = None) -> Dict[str, Any]:
        """Analyze text with primary provider and fallback options."""
        if fallback_providers is None:
            fallback_providers = []
        
        # Try primary provider first
        if primary_provider in self.providers:
            result = await self.providers[primary_provider].analyze_text(text, attitude_mode)
            if 'error' not in result:
                result['provider_used'] = primary_provider
                return result
        
        # Try fallback providers
        for provider_name in fallback_providers:
            if provider_name in self.providers:
                try:
                    result = await self.providers[provider_name].analyze_text(text, attitude_mode)
                    if 'error' not in result:
                        result['provider_used'] = provider_name
                        result['fallback_used'] = True
                        return result
                except Exception:
                    continue
        
        # All providers failed
        return {
            "error": "All AI providers failed",
            "confidence_score": 0.0,
            "providers_tried": [primary_provider] + fallback_providers
        }