"""Local-first LLM brain and intent router."""
from __future__ import annotations
import requests
class Brain:
    """Routes natural language to local skills and Ollama/OpenAI/Gemini responses."""
    irreversible = ('delete','send','upload','shutdown','restart','commit','push','lock')
    def __init__(self, settings, memory, stealth_mode=None, sloth_mode=None, teacher=None):
        self.settings=settings; self.memory=memory; self.stealth_mode=stealth_mode; self.sloth_mode=sloth_mode; self.teacher=teacher; self.conversation=[]
    def needs_confirmation(self, text: str) -> bool:
        """Return True for irreversible user requests."""; return any(w in text.lower() for w in self.irreversible)
    def parse_intent(self, text: str) -> dict:
        """Parse lightweight intents without requiring an LLM."""
        t=text.lower()
        if 'disable stealth' in t: return {'skill':'stealth_mode','action':'deactivate'}
        if 'stealth mode' in t: return {'skill':'stealth_mode','action':'activate'}
        if 'sloth mode' in t or 'go to sleep' in t or "don't disturb me" in t: return {'skill':'sloth_mode','action':'sleep'}
        if 'wake up' in t and 'jarvis' in t: return {'skill':'sloth_mode','action':'wake'}
        if 'what have you learned' in t: return {'skill':'self_learner','action':'recent'}
        if 'go deeper' in t: return {'skill':'teacher','action':'deeper'}
        if 'simpler' in t: return {'skill':'teacher','action':'simpler'}
        if 'just fix it' in t: return {'skill':'teacher','action':'fix_only'}
        if any(word in t for word in ['error','failed','traceback','what happened']): return {'skill':'teacher','action':'explain','text':text}
        if 'remember this idea' in t: return {'skill':'second_brain','action':'remember','text':text.split(':',1)[-1].strip()}
        if 'thumbnail' in t: return {'skill':'thumbnail_gen','action':'generate'}
        if 'focus mode' in t: return {'skill':'focus_mode','action':'start'}
        if 'remind me' in t: return {'skill':'reminder','action':'create','text':text}
        if 'go dark' in t: return {'skill':'privacy_mode','action':'lockdown','confirm':True}
        return {'skill':'chat','action':'answer','text':text}
    def answer_with_teaching(self, text: str) -> str:
        """Return a teaching explanation when teaching mode is enabled."""
        if self.teacher and self.settings.get('teaching_mode', True):
            return self.teacher.explain_error(text, self.settings.get('teaching_depth_default','medium'), just_fix='just fix it' in text.lower())
        return self.ask(text)
    def ask(self, prompt: str) -> str:
        """Ask the configured LLM provider, falling back to an offline response."""
        self.conversation.append({'role':'user','content':prompt})
        context='\n'.join(m['content'] for m in self.conversation[-6:])[-4000:]
        if self.settings.get('llm_provider') == 'ollama':
            try:
                r=requests.post('http://localhost:11434/api/generate',json={'model':self.settings.get('llm_model','llama3:8b'),'prompt':context,'stream':False,'options':{'num_ctx':self.settings.get('llm_context_window',2048)}},timeout=30)
                response=r.json().get('response','').strip(); self.conversation.append({'role':'assistant','content':response}); return response
            except Exception as exc: return f'Ollama is unavailable, Sir. {exc}'
        return 'Cloud fallback is configured but no API key/provider client is active, Sir.'
