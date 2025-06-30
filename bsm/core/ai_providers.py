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
        "unsupported_assertions": ["List of unsupported assertions"]
    },
    "logical_analysis": {
        "fallacies_identified": ["List of logical fallacies found"],
        "argument_strengths": ["Strong points in the argument"],
        "argument_weaknesses": ["Weak points in the argument"]
    },
    "counter_arguments": ["List of counter-arguments"],
    "alternative_perspectives": ["List of alternative viewpoints"],
    "confidence_score": 0.0-1.0,
    "sources_needed": ["What sources would help verify claims"],
    "conclusion": "Overall assessment"
}"""
        
        if attitude_mode == "argumentative":
            return base_prompt + "\n\nAdopt a more aggressive, debate-focused tone. Your goal is to find flaws and construct strong counter-arguments. Be thorough in identifying weaknesses."
        elif attitude_mode == "helpful":
            return base_prompt + "\n\nAdopt a helpful, educational tone. Focus on providing balanced information and gentle corrections. Be constructive rather than confrontational."
        else:  # balanced
            return base_prompt + "\n\nMaintain a balanced, objective tone. Present facts and counter-arguments neutrally without taking sides."
    
    async def analyze_text(self, text: str, attitude_mode: str) -> Dict[str, Any]:
        """Analyze text using OpenAI API."""
        try:
            self._report_progress(10)  # Starting analysis
            
            # Create completion with streaming for better progress tracking
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_system_prompt(attitude_mode)},
                    {"role": "user", "content": f"Please analyze the following text:\n\n{text}"}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            self._report_progress(80)  # Got response
            
            content = response.choices[0].message.content.strip()
            
            self._report_progress(90)  # Parsing response
            
            # Try to parse as JSON, fall back to text if needed
            try:
                result = json.loads(content)
                result['provider_used'] = self.get_name()
                self._report_progress(100)  # Complete
                return result
            except json.JSONDecodeError:
                self._report_progress(100)  # Complete
                return {
                    "summary": "Analysis completed",
                    "analysis": content,
                    "confidence_score": 0.8,
                    "provider_used": self.get_name(),
                    "error": "Response was not in expected JSON format"
                }
                
        except asyncio.CancelledError:
            logger.info("OpenAI analysis cancelled")
            raise
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
        base_prompt = """You are an expert fact-checker and critical analyst. Analyze the provided text and respond with a comprehensive fact-check and counter-argument analysis.

Your response must be valid JSON with this exact structure:
{
    "summary": "Brief summary of your analysis",
    "fact_check": {
        "verified_facts": ["List of verified facts"],
        "questionable_claims": ["List of questionable or false claims"],
        "unsupported_assertions": ["List of unsupported assertions"]
    },
    "logical_analysis": {
        "fallacies_identified": ["List of logical fallacies found"],
        "argument_strengths": ["Strong points in the argument"],
        "argument_weaknesses": ["Weak points in the argument"]
    },
    "counter_arguments": ["List of counter-arguments"],
    "alternative_perspectives": ["List of alternative viewpoints"],
    "confidence_score": 0.85,
    "sources_needed": ["What sources would help verify claims"],
    "conclusion": "Overall assessment"
}"""
        
        if attitude_mode == "argumentative":
            return base_prompt + "\n\nUse a more aggressive, debate-focused approach. Find flaws and construct strong counter-arguments."
        elif attitude_mode == "helpful":
            return base_prompt + "\n\nUse a helpful, educational approach. Provide balanced information and constructive corrections."
        else:  # balanced
            return base_prompt + "\n\nMaintain objectivity and present facts neutrally."
    
    async def analyze_text(self, text: str, attitude_mode: str) -> Dict[str, Any]:
        """Analyze text using Claude API."""
        try:
            self._report_progress(10)  # Starting analysis
            
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.3,
                system=self._get_system_prompt(attitude_mode),
                messages=[
                    {"role": "user", "content": f"Please analyze the following text:\n\n{text}"}
                ]
            )
            
            self._report_progress(80)  # Got response
            
            content = response.content[0].text.strip()
            
            self._report_progress(90)  # Parsing response
            
            # Try to parse as JSON
            try:
                result = json.loads(content)
                result['provider_used'] = self.get_name()
                self._report_progress(100)  # Complete
                return result
            except json.JSONDecodeError:
                self._report_progress(100)  # Complete
                return {
                    "summary": "Analysis completed",
                    "analysis": content,
                    "confidence_score": 0.8,
                    "provider_used": self.get_name(),
                    "error": "Response was not in expected JSON format"
                }
                
        except asyncio.CancelledError:
            logger.info("Claude analysis cancelled")
            raise
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return {
                "error": f"Claude API error: {str(e)}",
                "confidence_score": 0.0,
                "provider_used": self.get_name()
            }

class OllamaProvider(AIProvider):
    """Ollama local AI provider."""
    
    def __init__(self, base_url="http://localhost:11434", model="llama3.2-vision:latest"):
        super().__init__()
        self.endpoint = base_url.rstrip('/')
        self.model = model
    
    def get_name(self) -> str:
        return f"Ollama ({self.model})"
    
    def _get_prompt(self, text: str, attitude_mode: str) -> str:
        """Get prompt based on attitude mode."""
        base_instruction = """Analyze the following text and provide a fact-check and counter-argument analysis. Focus on:

1. Verifying factual claims
2. Identifying logical fallacies
3. Providing counter-arguments
4. Suggesting alternative perspectives

"""
        
        if attitude_mode == "argumentative":
            instruction = base_instruction + "Be aggressive in finding flaws and constructing strong counter-arguments.\n\n"
        elif attitude_mode == "helpful":
            instruction = base_instruction + "Be helpful and educational. Provide balanced, constructive feedback.\n\n"
        else:  # balanced
            instruction = base_instruction + "Maintain objectivity and present facts neutrally.\n\n"
        
        return instruction + f"Text to analyze:\n{text}"
    
    async def analyze_text(self, text: str, attitude_mode: str) -> Dict[str, Any]:
        """Analyze text using local Ollama."""
        try:
            self._report_progress(10)  # Starting analysis
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": self._get_prompt(text, attitude_mode),
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "max_tokens": 2000
                    }
                }
                
                async with session.post(
                    f"{self.endpoint}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    self._report_progress(50)  # Request sent
                    
                    if response.status == 200:
                        result = await response.json()
                        self._report_progress(80)  # Got response
                        
                        analysis_text = result.get('response', '').strip()
                        
                        self._report_progress(90)  # Parsing response
                        
                        self._report_progress(100)  # Complete
                        return {
                            "summary": "Local analysis completed",
                            "analysis": analysis_text,
                            "confidence_score": 0.7,
                            "provider_used": self.get_name()
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: HTTP {response.status}, {error_text}")
                        return {
                            "error": f"Ollama API error: HTTP {response.status}",
                            "confidence_score": 0.0,
                            "provider_used": self.get_name()
                        }
                        
        except asyncio.CancelledError:
            logger.info("Ollama analysis cancelled")
            raise
        except Exception as e:
            logger.error(f"Ollama connection error: {e}")
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