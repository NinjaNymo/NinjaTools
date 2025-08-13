# Oscilloscope Screenshot Tool

**Note:** For new setups, it is recommended to use this LAN-based `osc` tool instead of `osc_usb`.  
The LAN version has no driver requirements and works with supported oscilloscopes over the network.

## Quick Start
1. **Download or clone** this repository.  
2. **Run `osc`** from the command line — the first run will create a sample `osc.cfg`.  
3. **Edit `osc.cfg`** with your oscilloscope details (vendor, model, IP or MAC).  

Example:
```
osc mylabel
```
This will save a screenshot as `mylabel_01.<ext>` in your output folder.

---

## Overview
This tool captures screenshots from supported oscilloscopes over LAN using SCPI commands.

It uses a configuration file `osc.cfg` to define your oscilloscope model, IP/MAC, and other options.

## Usage
```
osc [label] [-v] [-o] [-h]
```

### Options
- **label** — Optional filename label instead of model name (spaces become underscores).  
- **-v** — Verbose mode, shows detailed connection and capture info.  
- **-o** — Opens the screenshot output directory without taking a screenshot.  
- **-h** — Shows help message and configuration summary.

### Examples
```
osc testlabel
osc -v mylabel
osc -o
osc
```

## Configuration
The script reads settings from `osc.cfg`. If the file does not exist, a sample will be created.  

Important settings:
- **vendor** — Oscilloscope vendor (Rigol, Keysight, Tektronix, etc.)
- **model** — Model name
- **ip** — IP address (preferred, faster connection)
- **mac** — MAC address (optional, used only if IP not provided)
- **port** — TCP port (default: 5555, Keysight default: 5025)
- **output_dir** — Directory where screenshots are saved (default: `~/Pictures/osc`)
- **output_prefix** — Can be `yyyy-mm-dd`, `yyyy-mm-dd-HH-MM-SS`, or empty for no prefix

## Output File Naming
- Default format: `<model>_01.<ext>` (or `<prefix>_<model>_01.<ext>` if prefix is set)
- If a file already exists, the numeric suffix increments automatically (`_02`, `_03`, etc.).
- The `label` argument replaces `<model>` in the naming scheme.

## Supported Vendors
- Rigol
- Keysight
- Tektronix
