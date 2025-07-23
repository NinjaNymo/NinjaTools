import pyvisa
import datetime
import os
from pathlib import Path
import argparse
import sys
import subprocess
import platform

def open_folder(path: Path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", path])
    else:  # Linux and others
        subprocess.run(["xdg-open", path])

def find_supported_scope():
    rm = pyvisa.ResourceManager()
    for res in rm.list_resources():
        try:
            inst = rm.open_resource(res)
            idn = inst.query("*IDN?").strip()
            if any(key in idn.upper() for key in ["RIGOL", "DHO", "KEYSIGHT", "MXR", "AGILENT"]):
                print(f"Connected to: {idn} ({res})")
                return inst, idn
            inst.close()
        except Exception:
            continue
    return None, None

def capture_screenshot(scope, idn, filename):
    scope.timeout = 10000  # 10-second timeout

    if "RIGOL" in idn and "DHO" in idn:
        scope.write(":DISP:DATA:FORM PNG")
        scope.write(":DISP:DATA?")
        raw_data = scope.read_raw()

        # Parse SCPI binary block header
        if raw_data.startswith(b'#'):
            header_length = int(raw_data[1:2])
            data_start = 2 + header_length
            raw_data = raw_data[data_start:]

    elif "KEYSIGHT" in idn or "AGILENT" in idn:
        scope.write(":DISPlay:DATA? PNG, SCREEN")
        raw_data = scope.read_raw()

        if raw_data.startswith(b'#'):
            header_length = int(raw_data[1:2])
            data_len = int(raw_data[2:2 + header_length])
            raw_data = raw_data[2 + header_length : 2 + header_length + data_len]

    else:
        raise Exception("Unsupported scope type.")

    with open(filename, "wb") as f:
        f.write(raw_data)

def build_filename(folder: Path, label: str) -> Path:
    today_str = datetime.datetime.now().strftime("%Y_%m_%d")
    base_filename = f"{today_str}_{label}"
    counter = 1
    filename = folder / f"{base_filename}_{counter:02}.png"
    while filename.exists():
        counter += 1
        filename = folder / f"{base_filename}_{counter:02}.png"
    return filename

def main():
    parser = argparse.ArgumentParser(description="Oscilloscope screenshot tool (Rigol DHO, Keysight MXR)")
    parser.add_argument("label", nargs="?", help="Label for the filename (e.g., 'startup', 'test1')")
    parser.add_argument("--folder", help="Optional folder to save image. Defaults to Pictures/Scope")
    parser.add_argument("-open", action="store_true", help="Open the screenshot save folder and exit")
    args = parser.parse_args()

    # Determine save folder
    if args.folder:
        folder = Path(args.folder).expanduser()
    else:
        folder = Path.home() / "Pictures" / "Scope"
    folder.mkdir(parents=True, exist_ok=True)

    # If -open is used, open the folder and exit
    if args.open:
        print(f"Opening folder: {folder}")
        open_folder(folder)
        sys.exit(0)

    # Handle label
    if not args.label:
        label = input("Enter a label for the screenshot (e.g., 'test1', 'startup'): ").strip()
        if not label:
            print("Error: Label cannot be empty.")
            sys.exit(1)
    else:
        label = args.label.strip()
    label = label.replace(" ", "_")

    filename = build_filename(folder, label)

    # Connect to scope
    scope, idn = find_supported_scope()
    if not scope:
        print("❌ No supported oscilloscope found.")
        sys.exit(1)

    try:
        capture_screenshot(scope, idn, filename)
        print(f"✅ Screenshot saved as: {filename}")
    finally:
        scope.close()

if __name__ == "__main__":
    main()
