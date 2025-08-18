#!/usr/bin/env python3
import socket
import os
import subprocess
import re
import platform
from datetime import datetime
import sys

def load_config(config_file="osc.cfg", verbose=True):
    config = {}
    if not os.path.exists(config_file):
        if verbose:
            print(f"✗ Configuration file '{config_file}' not found")
            print("Creating sample configuration file...")
        sample_config = """# Oscilloscope Configuration
vendor=Rigol
model=DHO924

# Preferred: Direct IP address (fast, no ARP lookup)
ip=192.168.1.100

# Optional: MAC address (used only if IP not provided)
# mac=aa:bb:cc:dd:ee:ff

# Optional: Port number for TCP connection (default: 5555, Keysight: 5025)
# port=5025

# Optional: Change screenshot save directory (default: ~/Pictures/osc)
# output_dir=/path/to/save/screenshots

# Optional: Prefix format for saved screenshots.
# Can be "yyyy-mm-dd", "yyyy-mm-dd-HH-MM-SS", or left empty for no prefix.
# output_prefix=yyyy-mm-dd-HH-MM-SS
"""
        with open(config_file, 'w') as f:
            f.write(sample_config)
        if verbose:
            print(f"✓ Sample '{config_file}' created. Please edit it with your oscilloscope details.")
        return None

    try:
        with open(config_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    if key in ['vendor', 'model', 'mac', 'output_dir', 'output_prefix', 'ip', 'port']:
                        config[key] = value
                    else:
                        if verbose:
                            print(f"⚠️  Unknown config key '{key}' on line {line_num}")

        required_fields = ['vendor', 'model']
        for field in required_fields:
            if field not in config:
                print(f"✗ Missing required field '{field}' in {config_file}")
                return None

        if 'output_dir' not in config or not config['output_dir']:
            config['output_dir'] = os.path.join(os.path.expanduser("~"), "Pictures", "osc")

        config['output_prefix'] = config.get('output_prefix', '').strip().lower()
        config['ip'] = config.get('ip', '').strip()
        config['mac'] = config.get('mac', '').strip().lower().replace(':', '').replace('-', '')

        if 'port' in config and config['port']:
            config['port'] = int(config['port'])
        elif config['vendor'].strip().lower() == 'keysight':
            config['port'] = 5025
        else:
            config['port'] = 5555

        if verbose:
            print(f"✓ Configuration loaded: {config['vendor']} {config['model']}")
            print(f"📂 Output directory: {config['output_dir']}")
            if config['output_prefix']:
                print(f"📝 Output prefix format: {config['output_prefix']}")
            else:
                print("📝 Output prefix: (none)")
            if config['ip']:
                print(f"🌐 Using direct IP: {config['ip']}")
            elif config['mac']:
                print(f"🔍 Will search ARP table for MAC: {config['mac']}")
            else:
                print("⚠️ No IP or MAC provided — connection will fail unless one is added.")
            print(f"🔌 TCP Port: {config['port']}")
        return config

    except Exception as e:
        print(f"✗ Error reading config file: {e}")
        return None


class OscilloscopeCapture:
    def __init__(self, vendor, model, mac_address=None, output_dir=None, output_prefix="",
                 ip_address=None, port=5555, timeout=10, verbose=True):
        self.vendor = vendor.lower()
        self.model = model.upper()
        self.mac_address = mac_address if mac_address else None
        self.ip_address = ip_address if ip_address else None
        self.port = port
        self.timeout = timeout
        self.sock = None
        self.output_dir = os.path.expanduser(output_dir or os.path.join("~", "Pictures", "osc"))
        self.output_prefix = output_prefix
        self.verbose = verbose
        self.log(f"🔧 Initialized {vendor} {model} capture interface")

    def log(self, msg):
        if self.verbose:
            print(msg)

    def find_ip_by_mac(self, mac_address):
        self.log(f"🔍 Searching ARP table for MAC: {mac_address}")
        try:
            target_mac = mac_address.lower()
            system = platform.system().lower()
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            arp_output = result.stdout
            for line in arp_output.split('\n'):
                if system == "windows":
                    if 'dynamic' in line.lower():
                        mac_match = re.search(r'([0-9a-f]{2}-){5}[0-9a-f]{2}', line.lower())
                        if mac_match:
                            found_mac = mac_match.group().replace('-', '').replace(':', '').lower()
                            if found_mac == target_mac:
                                ip_match = re.search(r'^([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', line.strip())
                                if ip_match:
                                    ip_addr = ip_match.group(1)
                                    self.log(f"✓ Found MAC in ARP table → IP: {ip_addr}")
                                    return ip_addr
                else:
                    if 'ether' in line.lower():
                        mac_match = re.search(r'([0-9a-f]{2}[:\-]){5}[0-9a-f]{2}', line.lower())
                        if mac_match:
                            found_mac = mac_match.group().replace('-', '').replace(':', '').lower()
                            if found_mac == target_mac:
                                ip_match = re.search(r'\(([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\)', line)
                                if ip_match:
                                    ip_addr = ip_match.group(1)
                                    self.log(f"✓ Found MAC in ARP table → IP: {ip_addr}")
                                    return ip_addr
            self.log("✗ MAC not found in ARP table")
            return None
        except Exception as e:
            self.log(f"✗ MAC lookup failed: {e}")
            return None

    def connect(self):
        try:
            if not self.ip_address:
                if self.mac_address:
                    self.ip_address = self.find_ip_by_mac(self.mac_address)
                    if not self.ip_address:
                        print("✗ Could not find device with specified MAC address")
                        return False
                else:
                    print("✗ No IP address or MAC address available")
                    return False
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.ip_address, self.port))
            print(f"✓ Connected to {self.vendor.title()} {self.model} at {self.ip_address}:{self.port}")
            if self.mac_address:
                self.log(f"📱 Device MAC: {self.mac_address}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    def disconnect(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            print("✓ Disconnected from oscilloscope")

    def send_command(self, command):
        if not self.sock:
            raise Exception("Not connected to oscilloscope")
        if not command.endswith('\n'):
            command += '\n'
        self.sock.send(command.encode())

    def query_command(self, command):
        if not self.sock:
            raise Exception("Not connected to oscilloscope")
        if not command.endswith('\n'):
            command += '\n'
        self.sock.send(command.encode())
        return self.sock.recv(1024).decode().strip()

    def get_screenshot_command(self):
        if self.vendor == 'rigol':
            return ":DISPlay:DATA?"
        elif self.vendor == 'keysight':
            return ":DISPlay:DATA? PNG"
        elif self.vendor == 'tektronix':
            return "HARDCopy:PORT ETHernet"
        else:
            return ":DISPlay:DATA?"

    def get_screenshot(self, filename=None, label=None):
        if not self.sock:
            raise Exception("Not connected to oscilloscope")
        self.log("📸 Capturing screenshot...")
        original_timeout = self.sock.gettimeout()
        self.sock.settimeout(15)
        try:
            self.send_command(self.get_screenshot_command())
            header = b""
            while len(header) < 2:
                chunk = self.sock.recv(2 - len(header))
                if not chunk:
                    raise Exception("Connection closed before header")
                header += chunk
            if header[0:1] != b'#':
                raise Exception("Invalid response format (missing #)")
            digit_count = int(chr(header[1]))
            if digit_count <= 0:
                raise Exception("Invalid length digit in header")
            length_str = b""
            while len(length_str) < digit_count:
                chunk = self.sock.recv(digit_count - len(length_str))
                if not chunk:
                    raise Exception("Connection closed before length")
                length_str += chunk
            data_length = int(length_str.decode())
            self.log(f"📊 Receiving {data_length} bytes of image data...")
            image_data = b""
            while len(image_data) < data_length:
                chunk = self.sock.recv(min(4096, data_length - len(image_data)))
                if not chunk:
                    raise Exception("Connection closed during image transfer")
                image_data += chunk
            if filename is None:
                os.makedirs(self.output_dir, exist_ok=True)
                prefix = ""
                if self.output_prefix == "yyyy-mm-dd":
                    prefix = datetime.now().strftime("%Y-%m-%d")
                elif self.output_prefix == "yyyy-mm-dd-hh-mm-ss":
                    prefix = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                base_name_part = label if label else self.model.lower()
                if prefix:
                    base_name = f"{prefix}_{base_name_part}"
                else:
                    base_name = base_name_part
                ext = self.get_default_extension()
                counter = 1
                while True:
                    candidate = os.path.join(self.output_dir, f"{base_name}_{counter:02d}.{ext}")
                    if not os.path.exists(candidate):
                        filename = candidate
                        break
                    counter += 1
            with open(filename, 'wb') as f:
                f.write(image_data)
            print(f"✓ Screenshot saved as: {filename}")
            return filename
        finally:
            self.sock.settimeout(original_timeout)

    def get_default_extension(self):
        if self.vendor == 'rigol':
            return 'bmp'
        elif self.vendor == 'keysight':
            return 'png'
        elif self.vendor == 'tektronix':
            return 'png'
        return 'bmp'

    def get_info(self):
        try:
            info = self.query_command("*IDN?")
            self.log(f"📋 Oscilloscope Info: {info}")
            return info
        except Exception as e:
            self.log(f"✗ Failed to get info: {e}")
            return None

def _is_wsl():
    try:
        return 'microsoft' in platform.uname().release.lower() or 'microsoft' in platform.version().lower()
    except Exception:
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except Exception:
            return False

def main():
    if "-o" in sys.argv:
        config = load_config("osc.cfg", verbose=False)
        if not config:
            print("✗ Could not load configuration. Please check osc.cfg file.")
            return

        output_dir = os.path.expanduser(config.get('output_dir', os.path.join("~", "Pictures", "osc")))
        os.makedirs(output_dir, exist_ok=True)

        system = platform.system().lower()
        if _is_wsl():
            # Convert to Windows path and open in Explorer
            try:
                res = subprocess.run(["wslpath", "-w", output_dir], capture_output=True, text=True)
                win_path = res.stdout.strip() if res.returncode == 0 and res.stdout else output_dir
                subprocess.run(["explorer.exe", win_path])
            except Exception as e:
                print(f"✗ Failed to open folder from WSL: {e}")
        elif system == "windows":
            os.startfile(output_dir)
        elif system == "darwin":
            subprocess.run(["open", output_dir])
        else:
            subprocess.run(["xdg-open", output_dir])
        return

    if "-h" in sys.argv:
        config = load_config("osc.cfg", verbose=False) or {}
        save_loc = os.path.expanduser(config.get('output_dir', os.path.join("~", "Pictures", "osc")))
        prefix_fmt = config.get('output_prefix', '').strip().lower() or "(none)"
        scope_parts = [config.get('vendor', ''), config.get('model', '')]
        if config.get('ip'): scope_parts.append(config['ip'])
        if config.get('mac'): scope_parts.append(config['mac'])
        if config.get('port'): scope_parts.append(str(config['port']))
        scope_line = " / ".join([p for p in scope_parts if p])

        print("Usage: osc [label] [-v] [-o] [-h]\n")
        print("Options:")
        print("  label        Optional filename label instead of model name (spaces become underscores)")
        print("  -v           Verbose mode, shows detailed connection and capture info")
        print("  -o           Opens the screenshot output directory without taking a screenshot")
        print("  -h           Shows this help message\n")
        print("Details:")
        print(f"  Oscilloscope: {scope_line}")
        print(f"  Save location: {save_loc}")
        print(f"  Prefix format: {prefix_fmt}\n")
        print("Examples:")
        print("  osc testlabel")
        print("  osc -v mylabel")
        print("  osc -o")
        print("  osc")
        return

    verbose = "-v" in sys.argv
    args = [a for a in sys.argv[1:] if a != "-v"]
    label_arg = args[0].strip().lower().replace(" ", "_") if len(args) > 0 else None
    config = load_config("osc.cfg", verbose=verbose)
    if not config:
        print("✗ Could not load configuration. Please check osc.cfg file.")
        return
    scope = OscilloscopeCapture(
        vendor=config['vendor'],
        model=config['model'],
        mac_address=config.get('mac', None),
        output_dir=config.get('output_dir'),
        output_prefix=config.get('output_prefix', ""),
        ip_address=config.get('ip', ""),
        port=config.get('port', 5555),
        verbose=verbose
    )
    try:
        if not scope.connect():
            return
        scope.get_info()
        scope.get_screenshot(label=label_arg)
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        scope.disconnect()


if __name__ == "__main__":
    main()
