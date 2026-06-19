"""Human-confirmed messaging automation."""
import time, webbrowser, urllib.parse
class MessagingSkill:
    """Draft and send messages through browser UIs after user confirmation."""
    def draft(self, recipient, message): """Create a message draft payload."""; return {'recipient':recipient,'message':message,'requires_confirmation':True}
    def send_whatsapp(self, phone_or_name: str, message: str) -> str:
        """Open WhatsApp Web in Edge and send a message. Requires user confirmation first."""
        import pyautogui
        encoded = urllib.parse.quote(message)
        url = f"https://web.whatsapp.com/send?phone={phone_or_name}&text={encoded}"
        webbrowser.open(url); time.sleep(6); pyautogui.hotkey("enter")
        return f"Message sent to {phone_or_name} via WhatsApp Web."
    def open_gmail_compose(self, to: str, subject: str, body: str) -> str:
        """Open Gmail compose window in Edge with pre-filled fields."""
        encoded_body = urllib.parse.quote(body); encoded_subject = urllib.parse.quote(subject)
        url = f"https://mail.google.com/mail/?view=cm&to={to}&su={encoded_subject}&body={encoded_body}"
        webbrowser.open(url); return f"Gmail compose opened for {to}."
