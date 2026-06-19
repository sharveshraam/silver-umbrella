"""Local-first LLM brain and intent router."""
from __future__ import annotations
import json, requests
class Brain:
    """Routes natural language to local skills and Ollama/OpenAI/Gemini responses."""
    irreversible = ('delete','send','upload','shutdown','restart','commit','push','lock')
    def __init__(self, settings, memory): self.settings=settings; self.memory=memory
    def needs_confirmation(self, text: str) -> bool:
        """Return True for irreversible user requests."""; return any(w in text.lower() for w in self.irreversible)
    def parse_intent(self, text: str) -> dict:
        """Parse lightweight intents without requiring an LLM."""
        t=text.lower()
        if 'remember this idea' in t: return {'skill':'second_brain','action':'remember','text':text.split(':',1)[-1].strip()}
        if 'thumbnail' in t: return {'skill':'thumbnail_gen','action':'generate'}
        if 'focus mode' in t: return {'skill':'focus_mode','action':'start'}
        if 'remind me' in t: return {'skill':'reminder','action':'create','text':text}
        if 'go dark' in t: return {'skill':'privacy_mode','action':'lockdown','confirm':True}
        return {'skill':'chat','action':'answer','text':text}
    def ask(self, prompt: str) -> str:
        """Ask the configured LLM provider, falling back to an offline response."""
        if self.settings.get('llm_provider') == 'ollama':
            try:
                r=requests.post('http://localhost:11434/api/generate',json={'model':self.settings.get('llm_model','llama3:8b'),'prompt':prompt,'stream':False,'options':{'num_ctx':self.settings.get('llm_context_window',2048)}},timeout=30)
                return r.json().get('response','').strip()
            except Exception as exc: return f'Ollama is unavailable, Sir. {exc}'
        return 'Cloud fallback is configured but no API key/provider client is active, Sir.'
