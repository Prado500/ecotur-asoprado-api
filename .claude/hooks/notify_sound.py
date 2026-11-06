"""Hook de notificación sonora para Claude Code.

Uso: `python .claude/hooks/notify_sound.py <evento>` con evento = `stop` | `permission`.
  - stop:       Claude terminó de responder (hook Stop).
  - permission: Claude o un subagente pide permiso (hook PermissionRequest).

Multiplataforma: Windows (winsound), macOS (afplay), Linux (paplay/aplay si existen).
Nunca falla: cualquier error se ignora y sale con 0 para no interferir con Claude Code.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

SOUNDS = {
    "win32": {
        # Lista de candidatos: se usa el primero que exista en el equipo.
        "stop": [r"C:\Windows\Media\tada.wav", r"C:\Windows\Media\Alarm01.wav"],
        "permission": r"C:\Windows\Media\Windows Exclamation.wav",
    },
    "darwin": {
        "stop": "/System/Library/Sounds/Glass.aiff",
        "permission": "/System/Library/Sounds/Funk.aiff",
    },
    "linux": {
        "stop": "/usr/share/sounds/freedesktop/stereo/complete.oga",
        "permission": "/usr/share/sounds/freedesktop/stereo/dialog-warning.oga",
    },
}


def main() -> int:
    event = sys.argv[1] if len(sys.argv) > 1 else "stop"
    platform = "linux" if sys.platform.startswith("linux") else sys.platform
    sound = SOUNDS.get(platform, {}).get(event)
    if isinstance(sound, list):
        sound = next((s for s in sound if os.path.exists(s)), None)
    if not sound:
        return 0
    try:
        if platform == "win32":
            import winsound

            winsound.PlaySound(sound, winsound.SND_FILENAME | winsound.SND_NODEFAULT)
        elif platform == "darwin":
            subprocess.run(["afplay", sound], capture_output=True, check=False)
        else:
            player = shutil.which("paplay") or shutil.which("aplay")
            if player:
                subprocess.run([player, sound], capture_output=True, check=False)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
