"""JARVIS desktop entry point."""
import sys
from PyQt6.QtWidgets import QApplication
from core.settings import Settings
from core.memory import MemoryStore
from core.brain import Brain
from core.voice import VoiceEngine
from core.stealth_mode import StealthMode
from core.sloth_mode import SlothMode
from core.teacher import Teacher
from core.self_learner import SelfLearner
from core.location_adapter import LocationAdapter
from ui.main_window import MainWindow
from ui.sidebar_chat import SidebarChat
from ui.pet_widget import PetWidget

def main() -> int:
    """Start JARVIS with lazy-loaded services, Phase 2 modes, and HUD UI."""
    settings=Settings(); memory=MemoryStore(); sloth=SlothMode(); stealth=StealthMode(enabled=settings.get('stealth_mode_default', False)); teacher=Teacher(memory, settings.get('teaching_depth_default','medium'), settings.get('skip_known_concepts', True)); brain=Brain(settings,memory,stealth,sloth,teacher); voice=VoiceEngine(settings,stealth,sloth)
    location=LocationAdapter(settings,memory); context=location.refresh(); learner=SelfLearner(settings,memory,brain,sloth)
    app=QApplication(sys.argv); app.setStyleSheet(open('ui/styles.qss',encoding='utf-8').read())
    win=MainWindow(); sidebar=SidebarChat(settings.get('stealth_sidebar_position','right'), settings.get('stealth_sidebar_opacity',0.85)); pet=None
    if settings.get('pet_enabled', True):
        pet=PetWidget(settings.get('pet_size',120), settings.get('pet_speech_bubbles', True)); pet.show()
    def sidebar_message(_speaker: str, formatted: str) -> None:
        sidebar.append_message(formatted)
    stealth.on_message=sidebar_message
    def set_stealth(active: bool) -> None:
        msg=stealth.activate(settings.get('user_name','Sir')) if active else stealth.deactivate(settings.get('user_name','Sir'))
        win.set_stealth_badge(stealth.enabled); win.add_message('JARVIS', msg); sidebar.set_stealth_active(stealth.enabled)
        if stealth.enabled: sidebar.show()
        if pet: pet.set_state('stealth' if stealth.enabled else 'idle'); pet.show_bubble('Stealth mode.' if stealth.enabled else 'Voice restored.')
    def toggle_stealth() -> None: set_stealth(not stealth.enabled)
    def toggle_sloth() -> None:
        if sloth.is_active():
            msg=sloth.wake(settings.get('user_name','Sir')); win.set_sleeping_badge(False)
            if pet: pet.set_state('idle')
        else:
            msg=sloth.sleep(); win.set_sleeping_badge(True); voice.muted=True; learner.stop_learning_session()
            if pet: pet.set_state('sleeping')
        win.add_message('JARVIS', msg); sidebar.append_message(stealth.format_message('JARVIS', msg))
    def handle_text(text: str) -> None:
        intent=brain.parse_intent(text); win.add_message('Sir', text); sidebar.append_message(stealth.format_message('Sir', text))
        if intent['skill']=='stealth_mode': set_stealth(intent['action']=='activate'); return
        if intent['skill']=='sloth_mode': toggle_sloth(); return
        if intent['skill']=='teacher': reply=brain.answer_with_teaching(text)
        else: reply=brain.ask(text)
        win.add_message('JARVIS', reply); sidebar.append_message(stealth.format_message('JARVIS', reply))
        if stealth.should_speak(): voice.speak(reply)
    win.stealth_toggled.connect(toggle_stealth); win.sloth_toggled.connect(toggle_sloth); sidebar.submitted.connect(handle_text)
    startup=f"All systems online. Good to see you again, {settings.get('user_name','Sir')}."
    win.add_message('JARVIS', startup); memory.log_activity('JARVIS started'); win.set_stealth_badge(stealth.enabled)
    if stealth.enabled: sidebar.show()
    for rec in location.recommendations(): win.add_message('Context', rec)
    win.show(); return app.exec()
if __name__ == '__main__': raise SystemExit(main())
