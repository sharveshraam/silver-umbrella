"""JARVIS desktop entry point."""
import ctypes
import importlib.util
import os
import subprocess
import sys
import time
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from core.settings import Settings
from core.memory import MemoryStore
from core.brain import Brain
from core.voice import VoiceEngine, MicListener
from core.wake import DoubleClapDetector
from core.stealth_mode import StealthMode
from core.sloth_mode import SlothMode
from core.teacher import Teacher
from core.self_learner import SelfLearner
from core.location_adapter import LocationAdapter
from core.pattern_learner import PatternLearner
from ui.main_window import MainWindow
from ui.sidebar_chat import SidebarChat
from ui.pet_widget import PetWidget
from ui.mini_widget import MiniOrb
from skills.focus_mode import FocusMode
from skills.health_nudge import HealthNudge
from skills.reminder import ReminderSkill

def get_idle_seconds_windows() -> float:
    """Return seconds since last user input on Windows, with a safe non-Windows fallback."""
    if os.name != "nt":
        return 0.0
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
    lii = LASTINPUTINFO(); lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
    return millis / 1000.0

def main() -> int:
    """Start JARVIS with lazy-loaded services, Phase 3 timers, and HUD UI."""
    settings=Settings(); memory=MemoryStore(); sloth=SlothMode(); stealth=StealthMode(enabled=settings.get('stealth_mode_default', False)); teacher=Teacher(memory, settings.get('teaching_depth_default','medium'), settings.get('skip_known_concepts', True)); brain=Brain(settings,memory,stealth,sloth,teacher); voice=VoiceEngine(settings,stealth,sloth)
    location=LocationAdapter(settings,memory); location.refresh(); learner=SelfLearner(settings,memory,brain,sloth); patterns=PatternLearner(memory); focus=FocusMode(settings); health=HealthNudge(); reminders=ReminderSkill(memory)
    app=QApplication(sys.argv); app.setStyleSheet(open('ui/styles.qss',encoding='utf-8').read())
    win=MainWindow(); sidebar=SidebarChat(settings.get('stealth_sidebar_position','right'), settings.get('stealth_sidebar_opacity',0.85)); orb=MiniOrb(); pet=None
    if settings.get('pet_enabled', True):
        pet=PetWidget(settings.get('pet_size',120), settings.get('pet_speech_bubbles', True)); pet.show()
    def sidebar_message(_speaker: str, formatted: str) -> None:
        sidebar.append_message(formatted)
    stealth.on_message=sidebar_message
    def restore_from_orb() -> None:
        orb.hide(); win.show(); win.raise_(); win.activateWindow()
    def go_orb() -> None:
        win.hide(); orb.show()
    def toggle_mute() -> None:
        voice.muted = not voice.muted
        win.buttons['Mute'].setText('Unmute' if voice.muted else 'Mute')
        win.reactor.set_mode('muted' if voice.muted else ('stealth' if stealth.enabled else 'idle'))
        if pet: pet.show_bubble('Muted.' if voice.muted else 'Voice on.')
    def set_stealth(active: bool) -> None:
        msg=stealth.activate(settings.get('user_name','Sir')) if active else stealth.deactivate(settings.get('user_name','Sir'))
        win.set_stealth_badge(stealth.enabled); win.add_message('JARVIS', msg); sidebar.set_stealth_active(stealth.enabled); win.reactor.set_mode('stealth' if stealth.enabled else 'idle'); orb.set_badge('[STEALTH]' if stealth.enabled else '')
        if stealth.enabled: sidebar.show()
        if pet: pet.set_state('stealth' if stealth.enabled else 'idle'); pet.show_bubble('Stealth mode.' if stealth.enabled else 'Voice restored.')
    def toggle_stealth() -> None: set_stealth(not stealth.enabled)
    def toggle_sloth() -> None:
        if sloth.is_active():
            msg=sloth.wake(settings.get('user_name','Sir')); voice.muted=False; win.set_sleeping_badge(False); win.reactor.set_mode('idle'); orb.set_badge('[STEALTH]' if stealth.enabled else '')
            if pet: pet.set_state('idle')
        else:
            msg=sloth.sleep(); win.set_sleeping_badge(True); win.reactor.set_mode('sleeping'); orb.set_badge('[SLEEPING]'); voice.muted=True; learner.stop_learning_session()
            if pet: pet.set_state('sleeping')
        win.add_message('JARVIS', msg); sidebar.append_message(stealth.format_message('JARVIS', msg))
    def start_focus() -> None:
        msg = focus.start(settings.get('focus_default_minutes', 25), on_complete=lambda: win.add_message('JARVIS', 'Focus session complete. Take a five-minute break.'))
        win.add_message('JARVIS', msg); win.reactor.set_mode('working')
        if pet: pet.set_state('focused')
    def on_wake() -> None:
        """Called on confirmed double-clap."""
        if sloth.is_active(): return
        win.reactor.set_mode('listening')
        if pet: pet.set_state('listening')
        win.add_message('JARVIS', 'Yes, Sir?')
        if not stealth.enabled: voice.speak('Yes, Sir?')
        QTimer.singleShot(3000, lambda: win.reactor.set_mode('idle'))
        if pet: QTimer.singleShot(3000, lambda: pet.set_state('idle'))
    def handle_text(text: str) -> None:
        intent=brain.parse_intent(text); patterns.log_event(intent.get('skill','chat'), hour=True); win.add_message('Sir', text); sidebar.append_message(stealth.format_message('Sir', text))
        if intent['skill']=='stealth_mode': set_stealth(intent['action']=='activate'); return
        if intent['skill']=='sloth_mode': toggle_sloth(); return
        win.reactor.set_mode('thinking')
        if pet: pet.set_state('thinking')
        if intent['skill']=='teacher': reply=brain.answer_with_teaching(text)
        elif intent['skill']=='self_learner': reply='Recent learnings: ' + str(learner.recent_learnings())
        else: reply=brain.ask(text)
        win.add_message('JARVIS', reply); sidebar.append_message(stealth.format_message('JARVIS', reply))
        win.reactor.set_mode('stealth' if stealth.enabled else 'idle')
        if pet: pet.set_state('stealth' if stealth.enabled else 'idle')
        if stealth.should_speak(): voice.speak(reply)
    win.stealth_toggled.connect(toggle_stealth); win.sloth_toggled.connect(toggle_sloth); sidebar.submitted.connect(handle_text); win.message_submitted.connect(handle_text)
    win.buttons['Mute'].clicked.connect(toggle_mute); win.buttons['Focus Mode'].clicked.connect(start_focus); win.buttons['Minimize to Orb'].clicked.connect(go_orb); win.buttons['Close'].clicked.connect(app.quit); win.buttons['Settings'].clicked.connect(lambda: subprocess.Popen(['notepad.exe','config.yaml']))
    orb.open_requested=restore_from_orb; orb.mute_requested=toggle_mute; orb.stealth_requested=toggle_stealth; orb.sloth_requested=toggle_sloth
    if pet:
        pet.open_requested=restore_from_orb; pet.toggle_mute=toggle_mute; pet.toggle_stealth=toggle_stealth; pet.toggle_sloth=toggle_sloth
    detector=DoubleClapDetector(sensitivity=settings.get('clap_sensitivity',0.75), sloth_mode=sloth); mic_listener=MicListener(detector,on_wake,sloth_mode=sloth)
    if settings.get('features', {}).get('wake', True): mic_listener.start()
    app.aboutToQuit.connect(mic_listener.stop)
    idle_timer=QTimer(); idle_timer.setInterval(int(settings.get('idle_poll_interval_seconds',60))*1000)
    def on_idle_tick() -> None:
        idle_secs=get_idle_seconds_windows(); learner.tick(idle_secs); is_learning=learner.worker and learner.worker.is_alive()
        if pet and is_learning: pet.set_state('reading')
        elif pet and getattr(pet.state,'value',None)=='reading': pet.set_state('idle')
        if idle_secs < 5 and learner.learned_since_return:
            count=len(learner.learned_since_return); win.add_message('JARVIS', f"Welcome back, Sir. I used the downtime to catch up — found {count} things you'd like. Want a summary?"); learner.learned_since_return.clear()
    idle_timer.timeout.connect(on_idle_tick); idle_timer.start()
    suggest_timer=QTimer(); suggest_timer.setInterval(30*60*1000)
    def check_suggestions() -> None:
        if sloth.is_active(): return
        for suggestion in patterns.suggestions():
            win.add_message('JARVIS', suggestion)
            if not stealth.enabled: voice.speak(suggestion)
    suggest_timer.timeout.connect(check_suggestions); suggest_timer.start()
    screen_minutes=0; health_timer=QTimer(); health_timer.setInterval(60_000)
    def on_health_tick() -> None:
        nonlocal screen_minutes
        if not settings.get('health_nudge_enabled', True) or sloth.is_active(): return
        idle=get_idle_seconds_windows(); screen_minutes = screen_minutes + 1 if idle < 60 else 0; msg=health.message(screen_minutes)
        if msg:
            win.add_message('JARVIS', msg)
            if not stealth.enabled: voice.speak(msg)
            if pet: pet.show_bubble(msg)
    health_timer.timeout.connect(on_health_tick); health_timer.start()
    reminder_timer=QTimer(); reminder_timer.setInterval(int(settings.get('reminder_check_interval_seconds',30))*1000)
    def check_reminders() -> None:
        if sloth.is_active(): return
        for row in reminders.due():
            rid,text,due_at=row; msg=f'Reminder, Sir: {text}'; win.add_message('JARVIS', msg)
            if not stealth.enabled: voice.speak(msg)
            if pet:
                pet.set_state('alert'); pet.show_bubble('Reminder!'); QTimer.singleShot(3000, lambda: pet.set_state('idle'))
            with memory.connect() as con: con.execute('UPDATE reminders SET done=1 WHERE id=?',(rid,))
    reminder_timer.timeout.connect(check_reminders); reminder_timer.start()
    game_watch_timer=QTimer(); game_watch_timer.setInterval(10_000)
    def check_game_processes() -> None:
        cfg=settings.get('sloth_on_game_launch', {})
        if not cfg.get('enabled', False): return
        if sloth.should_auto_sleep_for_processes(cfg.get('game_processes', [])) and not sloth.is_active(): toggle_sloth()
    game_watch_timer.timeout.connect(check_game_processes); game_watch_timer.start()
    git_watch_repo=settings.get('git_auto_watch_repo','')
    if git_watch_repo and importlib.util.find_spec('git') and importlib.util.find_spec('watchdog'):
        from skills.git_auto import GitAuto
        git_auto=GitAuto(brain); git_auto.start_watching(git_watch_repo, int(settings.get('git_debounce_seconds',30)))
        app.aboutToQuit.connect(git_auto.stop_watching)
    startup=f"All systems online. Good to see you again, {settings.get('user_name','Sir')}."; win.add_message('JARVIS', startup); memory.log_activity('JARVIS started'); win.set_stealth_badge(stealth.enabled)
    if stealth.enabled: sidebar.show()
    for rec in location.recommendations(): win.add_message('Context', rec)
    win.show(); return app.exec()
if __name__ == '__main__': raise SystemExit(main())
