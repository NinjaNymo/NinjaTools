# Oscilloscope Screenshot Tool (USB)

> **⚠️ Warning:**  
> Using **`osc_usb`** is **not recommended** because it requires installing USB drivers for each scope model you use.  
> Instead, it is recommended to use the newer **`osc`** tool, which works over **LAN** and has **no driver requirements**, offering faster setup and broader compatibility.

This is a simple Python utility for capturing screenshots directly from supported oscilloscopes connected via **USB** using the [PyVISA](https://pyvisa.readthedocs.io/en/latest/) library.

## Features
- Works with **Rigol DHO** series and **Keysight/Agilent MXR** series scopes (auto-detects via `*IDN?`).
- Automatically finds a connected supported scope over VISA/USB.
- Captures a full-resolution screenshot from the oscilloscope display.
- Saves images in `~/Pictures/Scope` by default.
- Auto-increments filenames to avoid overwriting.
- Optional `-open` flag to open the save folder.
- Runs on Windows, macOS, and Linux.

## Requirements
- Python 3.x  
- [PyVISA](https://pyvisa.readthedocs.io/en/latest/) (`pip install pyvisa`)  
- VISA backend (e.g., [NI-VISA](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html)) installed and configured.

## Usage
```bash
python osc_usb.py [label] [--folder PATH] [-open]
```

### Arguments
- `label` (optional) – A short name for the screenshot (e.g., `test1`). Spaces will be replaced with underscores.  
- `--folder PATH` – Custom folder to save screenshots. Defaults to `~/Pictures/Scope`.  
- `-open` – Opens the screenshot folder and exits (no capture).

### Examples
```bash
# Capture with label 'startup' and default folder
python osc_usb.py startup

# Capture with label 'waveform1' in a custom folder
python osc_usb.py waveform1 --folder ~/Desktop/scope_captures

# Open the save folder without capturing
python osc_usb.py -open
```

## How It Works
1. **Device Detection:**  
   - Uses PyVISA to list connected VISA resources.
   - Queries each with `*IDN?` and matches against known vendors/models.

2. **Capture Logic:**  
   - For **Rigol DHO**:  
     ```
     :DISP:DATA:FORM PNG
     :DISP:DATA?
     ```
   - For **Keysight/Agilent MXR**:  
     ```
     :DISPlay:DATA? PNG, SCREEN
     ```
   - Reads the raw binary block and strips SCPI headers.

3. **File Naming:**  
   - Files are named as:  
     ```
     YYYY_MM_DD_<label>_##.png
     ```
     Auto-incremented if a file already exists.
