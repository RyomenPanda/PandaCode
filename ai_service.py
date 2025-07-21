import os
import logging
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from models import AIResponse

class AIService:
    """Service for AI integration using Gemini"""
    
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logging.warning("GEMINI_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
    
    def _is_available(self) -> bool:
        """Check if AI service is available"""
        return self.client is not None
    
    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Chat with AI assistant"""
        if not self._is_available():
            return AIResponse(
                success=False,
                content="",
                error="AI service not available. Please set GEMINI_API_KEY environment variable."
            )
        
        try:
            # Build context-aware prompt
            prompt = self._build_context_prompt(message, context or {})
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return AIResponse(
                success=True,
                content=response.text or "No response generated",
                error=None
            )
        except Exception as e:
            logging.error(f"AI chat error: {e}")
            return AIResponse(
                success=False,
                content="",
                error=f"AI service error: {str(e)}"
            )
    
    def refactor_code(self, code: str, language: str, instruction: str) -> AIResponse:
        """Refactor code using AI"""
        if not self._is_available():
            return AIResponse(
                success=False,
                content="",
                error="AI service not available. Please set GEMINI_API_KEY environment variable."
            )
        
        try:
            prompt = f"""You are an expert {language} developer. Please refactor the following code according to the instruction.

Instruction: {instruction}

Code to refactor:
```{language}
{code}
```

Please provide only the refactored code without additional explanation."""
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return AIResponse(
                success=True,
                content=response.text or "No response generated",
                error=None
            )
        except Exception as e:
            logging.error(f"AI refactor error: {e}")
            return AIResponse(
                success=False,
                content="",
                error=f"AI service error: {str(e)}"
            )
    
    def generate_tests(self, code: str, language: str) -> AIResponse:
        """Generate unit tests for the given code"""
        if not self._is_available():
            return AIResponse(
                success=False,
                content="",
                error="AI service not available. Please set GEMINI_API_KEY environment variable."
            )
        
        try:
            prompt = f"""You are an expert {language} developer. Generate comprehensive unit tests for the following code.

Code to test:
```{language}
{code}
```

Please provide complete unit tests with proper test framework setup and assertions."""
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return AIResponse(
                success=True,
                content=response.text or "No response generated",
                error=None
            )
        except Exception as e:
            logging.error(f"AI test generation error: {e}")
            return AIResponse(
                success=False,
                content="",
                error=f"AI service error: {str(e)}"
            )
    
    def _build_context_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """Build context-aware prompt for AI"""
        prompt_parts = []
        
        prompt_parts.append("You are an expert programming assistant. You help developers with code analysis, refactoring, debugging, and general programming tasks.")
        
        # Add current file context
        if context.get("currentFile"):
            current_file = context["currentFile"]
            prompt_parts.append(f"\nCurrent file: {current_file['path']} ({current_file['language']})")
            if current_file.get("content"):
                prompt_parts.append(f"```{current_file['language']}\n{current_file['content'][:2000]}...\n```")
        
        # Add open files context
        if context.get("openFiles"):
            open_files = context["openFiles"][:5]  # Limit to 5 files
            file_list = [f"- {f['path']} ({f['language']})" for f in open_files]
            prompt_parts.append(f"\nOpen files:\n{chr(10).join(file_list)}")
        
        # Add conversation history
        if context.get("conversationHistory"):
            prompt_parts.append("\nRecent conversation:")
            for exchange in context["conversationHistory"][-3:]:  # Last 3 exchanges
                prompt_parts.append(f"User: {exchange['user']}")
                prompt_parts.append(f"Assistant: {exchange['assistant'][:200]}...")
        
        prompt_parts.append(f"\nUser request: {message}")
        
        return "\n".join(prompt_parts)
