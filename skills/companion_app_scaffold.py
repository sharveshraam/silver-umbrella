"""
COPE Companion App Bridge — Phase 4B (ACTIVE)

Listens on TCP port 9876 for connections from the COPE Android companion app.
Handles notifications, voice commands, clipboard sync, location, and file
transfer over local Wi-Fi via ADB USB or the COPE Companion App.
"""
from __future__ import annotations
import socket
import threading
import json
import time
from pathlib import Path


COMPANION_PORT = 9876
COMPANION_HOST = "0.0.0.0"
BUFFER_SIZE = 4096


class CompanionBridge:
    """Wi-Fi TCP bridge between COPE desktop and the COPE Android companion app."""

    def __init__(self, brain=None, memory=None, on_message=None, on_status=None):
        self.brain = brain
        self.memory = memory
        self.on_message = on_message      # callback(text) → routes to handle_text in main.py
        self.on_status = on_status        # callback(str) → shows in COPE HUD
        self._server: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self.client: socket.socket | None = None
        self.active = False
        self.last_ping = 0.0

    def start(self) -> str:
        """Start the TCP server and begin listening for companion app."""
        if self.active:
            return "Companion bridge already running."
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((COMPANION_HOST, COMPANION_PORT))
        self._server.listen(1)
        self._server.settimeout(1.0)
        self.active = True
        self._thread = threading.Thread(
            target=self._listen_loop, name="cope-companion", daemon=True
        )
        self._thread.start()
        return f"Companion bridge listening on port {COMPANION_PORT}."

    def stop(self) -> None:
        """Stop the TCP server."""
        self.active = False
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
            self.client = None
        if self._server:
            try:
                self._server.close()
            except Exception:
                pass
        self._server = None

    def is_phone_connected(self) -> bool:
        """Return True if a companion app client is currently connected."""
        return self.client is not None and (time.time() - self.last_ping) < 15

    def connection_status(self) -> str:
        return "WIFI: CONNECTED" if self.is_phone_connected() else "WIFI: WAITING"

    def send(self, payload: dict) -> bool:
        """Send a JSON payload to the companion app."""
        if not self.client:
            return False
        try:
            data = json.dumps(payload).encode() + b"\n"
            self.client.sendall(data)
            return True
        except Exception:
            self.client = None
            return False

    def push_notification(self, title: str, body: str) -> bool:
        """Push a notification to the companion app."""
        return self.send({"type": "notification", "title": title, "body": body})

    def sync_clipboard_to_phone(self, content: str) -> bool:
        """Send PC clipboard content to the companion app."""
        return self.send({"type": "clipboard", "content": content})

    def _listen_loop(self) -> None:
        """Main TCP accept + receive loop."""
        if self.on_status:
            self.on_status("Companion bridge: waiting for phone connection...")
        while self.active:
            if self._server is None:
                break
            try:
                conn, addr = self._server.accept()
                self.client = conn
                self.last_ping = time.time()
                if self.on_status:
                    self.on_status(f"Phone connected: {addr[0]}")
                self._handle_client(conn)
            except socket.timeout:
                continue
            except Exception:
                break

    def _handle_client(self, conn: socket.socket) -> None:
        """Receive and route messages from the companion app."""
        buffer = ""
        while self.active:
            try:
                chunk = conn.recv(BUFFER_SIZE).decode(errors="ignore")
                if not chunk:
                    break
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                        self._route(payload)
                        self.last_ping = time.time()
                    except json.JSONDecodeError:
                        pass
            except Exception:
                break
        self.client = None
        if self.on_status:
            self.on_status("Phone disconnected.")

    def _route(self, payload: dict) -> None:
        """Route incoming payload to the right COPE handler."""
        ptype = payload.get("type", "")

        if ptype == "ping":
            self.send({"type": "pong"})

        elif ptype == "voice_command":
            # Phone mic sent a voice command → route to handle_text
            text = payload.get("text", "").strip()
            if text and callable(self.on_message):
                self.on_message(text)

        elif ptype == "notification":
            # Phone notification → show in COPE HUD
            app = payload.get("app", "Phone")
            title = payload.get("title", "")
            body = payload.get("body", "")
            msg = f"[{app}] {title}: {body}"
            if callable(self.on_status):
                self.on_status(msg)
            if self.memory:
                self.memory.log_activity(f"Phone notification: {msg[:100]}")

        elif ptype == "clipboard":
            # Phone clipboard → sync to PC
            content = payload.get("content", "")
            if content:
                try:
                    import pyperclip
                    pyperclip.copy(content)
                    if callable(self.on_status):
                        self.on_status("Clipboard synced from phone.")
                except Exception:
                    pass

        elif ptype == "location":
            # Phone GPS → update COPE location context
            lat = payload.get("lat")
            lon = payload.get("lon")
            if lat and lon and callable(self.on_status):
                try:
                    self.on_status(f"Phone location updated: {float(lat):.4f}, {float(lon):.4f}")
                except (TypeError, ValueError):
                    self.on_status(f"Phone location updated: {lat}, {lon}")

        elif ptype == "file":
            # Phone sending a file → save to local folder
            filename = payload.get("filename", "phone_file")
            import base64
            data_b64 = payload.get("data", "")
            if data_b64:
                safe_name = Path(str(filename)).name or "phone_file"
                out = Path("data/phone_transfers") / safe_name
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(base64.b64decode(data_b64))
                if callable(self.on_status):
                    self.on_status(f"File received from phone: {safe_name}")
