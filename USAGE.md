# Usage Guide - Terraform IPv4 IoC Normalizer

A complete beginner-friendly guide to installing and using the Terraform IPv4 IoC Normalizer on Windows, Linux, and macOS.

---

## Table of Contents

1. [What is This Tool?](#what-is-this-tool)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
   - [Windows Installation](#windows-installation)
   - [Linux Installation](#linux-installation)
   - [macOS Installation](#macos-installation)
4. [Preparing Your Data](#preparing-your-data)
5. [Running the Application](#running-the-application)
6. [Step-by-Step Workflow](#step-by-step-workflow)
7. [Understanding the Interface](#understanding-the-interface)
8. [Export Options](#export-options)
9. [Using the Output in Terraform](#using-the-output-in-terraform)
10. [Troubleshooting](#troubleshooting)

---

## What is This Tool?

This is a **Terminal User Interface (TUI)** application that helps security analysts and threat intelligence teams convert raw IPv4 addresses into Terraform-ready CIDR /32 blocks.

**What it does:**
- Reads IPv4 addresses from CSV, TSV, or TXT files
- Validates and extracts only valid IPv4 addresses
- Converts them to Terraform HCL format (`"IP/32"`)
- Exports to JSON or copies directly to clipboard

**Why use it?**
- Quickly format threat intelligence IPs for infrastructure-as-code security policies
- No manual formatting required
- Audit trail with timestamped exports
- Works with various CSV formats (auto-detects delimiters)

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Windows 10+, Ubuntu 20.04+, Debian 11+, macOS 11+ |
| **Python** | Python 3.8 or higher |
| **Memory** | 512 MB RAM |
| **Disk Space** | 100 MB for dependencies |
| **Terminal** | Any modern terminal (see platform specifics below) |

### Platform-Specific Terminal Requirements

**Windows:** PowerShell or Command Prompt
**Linux:** Any terminal emulator (GNOME Terminal, Konsole, etc.)
**macOS:** Terminal.app or iTerm2

---

## Installation

### Windows Installation

#### Option 1: Using the Auto Launcher (Recommended for Beginners)

1. **Install Python (if not already installed)**
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check the box **"Add Python to PATH"**
   - Verify installation: Open PowerShell and type `python --version`

2. **Clone or Download the Repository**
   ```powershell
   # Using Git (if installed)
   git clone https://github.com/srflmr/terraform-ipv4-ioc-normalizer.git
   cd terraform-ipv4-ioc-normalizer

   # OR download and extract the ZIP file from GitHub
   ```

3. **Run the Launcher**
   ```powershell
   python launcher.py
   ```

   The launcher will automatically:
   - Verify Python 3.8+ is installed
   - Create a virtual environment (`.venv`)
   - Ensure pip is available
   - Install all required dependencies from requirements.txt
   - Launch the application

#### Option 2: Manual Installation (For Advanced Users)

1. **Open PowerShell or Command Prompt**

2. **Navigate to the Project Directory**
   ```powershell
   cd path\to\terraform-ipv4-ioc-normalizer
   ```

3. **Create Virtual Environment**
   ```powershell
   python -m venv .venv
   ```

4. **Activate Virtual Environment**
   ```powershell
   .\.venv\Scripts\activate
   ```

5. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

6. **Run the Application**
   ```powershell
   python app.py
   ```

---

### Linux Installation

#### Option 1: Using the Auto Launcher (Recommended)

1. **Install Python (if not already installed)**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv -y

   # Fedora/RHEL
   sudo dnf install python3 python3-pip -y

   # Arch Linux
   sudo pacman -S python python-pip -y
   ```

2. **Clone the Repository**
   ```bash
   git clone https://github.com/srflmr/terraform-ipv4-ioc-normalizer.git
   cd terraform-ipv4-ioc-normalizer
   ```

3. **Run the Launcher**
   ```bash
   python3 launcher.py
   ```

#### Option 2: Manual Installation

1. **Create Virtual Environment**
   ```bash
   python3 -m venv .venv
   ```

2. **Activate Virtual Environment**
   ```bash
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

#### Clipboard Support on Linux

For clipboard functionality, install one of the following:

```bash
# For X11-based systems
sudo apt install xclip -y           # Ubuntu/Debian
sudo dnf install xclip -y           # Fedora/RHEL

# For Wayland-based systems
sudo apt install wl-clipboard -y    # Ubuntu/Debian
sudo dnf install wl-clipboard -y    # Fedora/RHEL
```

---

### macOS Installation

#### Option 1: Using the Auto Launcher (Recommended)

1. **Install Python (if not already installed)**
   ```bash
   # Using Homebrew (recommended)
   brew install python@3.11

   # OR download from python.org
   ```

2. **Clone the Repository**
   ```bash
   git clone https://github.com/srflmr/terraform-ipv4-ioc-normalizer.git
   cd terraform-ipv4-ioc-normalizer
   ```

3. **Run the Launcher**
   ```bash
   python3 launcher.py
   ```

#### Option 2: Manual Installation

1. **Create Virtual Environment**
   ```bash
   python3 -m venv .venv
   ```

2. **Activate Virtual Environment**
   ```bash
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

---

## Preparing Your Data

### Supported File Formats

The application accepts the following file types:
- **CSV** (Comma-Separated Values)
- **TSV** (Tab-Separated Values)
- **TXT** (Plain text)
- **LOG** (Log files)

### Supported Delimiters

The application automatically detects these delimiters:
- Comma (`,`)
- Semicolon (`;`)
- Tab (`\t`)
- Pipe (`|`)

### Preparing Your Input File

1. **Place your file in the `input/` directory**
   - The application creates this directory automatically on first run
   - Simply copy your CSV/TSV/TXT files there

2. **Example File Formats**

   **Semicolon-delimited CSV (with header):**
   ```csv
   IP Address;
   102.129.165.164;
   103.136.69.227;
   103.231.74.10;
   ```

   **Comma-delimited CSV (with header):**
   ```csv
   indicator,value
   192.168.1.1,malicious
   10.0.0.1,suspicious
   172.16.0.1,scanner
   ```

   **Tab-delimited TSV (no header):**
   ```
   192.168.1.1	Threat_A
   10.0.0.1	Threat_B
   172.16.0.1	Threat_C
   ```

   **Plain text (one IP per line):**
   ```
   192.168.1.1
   10.0.0.1
   172.16.0.1
   ```

3. **File Naming Tips**
   - Use descriptive names: `threat_feed_2024-01.csv`
   - Avoid spaces in filenames (use underscores instead)
   - Keep files under 10MB for best performance

---

## Running the Application

### Quick Start

**After installation, simply run:**

```bash
# Windows
python launcher.py

# Linux/macOS
python3 launcher.py
```

The launcher handles everything automatically:
- Verifies Python 3.8+ is installed
- Creates/updates virtual environment
- Ensures pip is available
- Installs/upgrades dependencies
- Launches the TUI application

### Running Manually (After First Setup)

```bash
# Windows
.venv\Scripts\activate
python app.py

# Linux/macOS
source .venv/bin/activate
python app.py
```

### What You'll See

When the application launches, you'll see a **3-panel interface**:

```
+---------------------+----------------------+----------------------+
|  File Browser       |  Raw IPv4 (Valid)    |  Terraform /32 Ready |
+---------------------+----------------------+----------------------+
|  [input files]      |  192.168.1.1         |  "192.168.1.1/32"    |
|  sample.csv         |  10.0.0.1            |  "10.0.0.1/32"       |
|  threat_feed.csv    |  172.16.0.1          |  "172.16.0.1/32"     |
+---------------------+----------------------+----------------------+
| [Load Selected]     |                      |                      |
| [Load Path]         |                      |                      |
+---------------------+----------------------+----------------------+
| PROCESS | COPY TF | SAVE JSON | QUIT                            |
+------------------------------------------------------------------+
```

---

## Step-by-Step Workflow

### Step 1: Load Your File

**Option A: Use the File Browser (Recommended)**

1. The **File Browser** panel shows all files in the `input/` directory
2. Use arrow keys to navigate to your file
3. Press `Enter` to select the file
4. The file loads automatically and displays valid IPv4 addresses in the **Raw IPv4** panel

**Option B: Manual Path Input**

1. Click on the input field below the file browser
2. Type the full path to your file (e.g., `/path/to/your/file.csv`)
3. Click **LOAD PATH** or press `Enter`
4. Valid IPv4 addresses will appear in the **Raw IPv4** panel

### Step 2: Review Raw IPv4 Addresses

- Check the **Raw IPv4 (Valid)** panel
- The status bar shows how many IPs were found
- Only valid IPv4 addresses are displayed (invalid ones are filtered out)
- The file name is shown in the summary bar

### Step 3: Process to CIDR /32

1. Click the **PROCESS** button (or press `Tab` to navigate and `Enter` to select)
2. The application converts each IP to CIDR /32 format
3. Results appear in the **Terraform /32 Ready** panel
4. Each IP is formatted as `"IP/32"` (with quotes for Terraform HCL)

### Step 4: Export Your Data

**Option A: Copy to Clipboard**

1. Click **COPY TF**
2. The Terraform list is copied to your clipboard
3. Paste directly into your Terraform configuration:

   ```hcl
   cidr_blocks = ["192.168.1.1/32","10.0.0.1/32","172.16.0.1/32"]
   ```

**Option B: Save to JSON**

1. Click **SAVE JSON**
2. A JSON file is created in the `output/` directory
3. Filename format: `terraform_iocs_<count>_<timestamp>.json`
   - Example: `terraform_iocs_10_20240110_204307.json`

---

## Understanding the Interface

### Layout Overview

| Panel | Purpose |
|-------|---------|
| **File Browser** | Navigate and select input files |
| **Raw IPv4 (Valid)** | Shows extracted valid IPv4 addresses |
| **Terraform /32 Ready** | Shows converted CIDR /32 blocks |

### Buttons and Actions

| Button | Action | Keyboard Shortcut |
|--------|--------|-------------------|
| **LOAD SELECTED** | Load the currently selected file from the browser | `Enter` (on file) |
| **LOAD PATH** | Load file from the manual path input | `Enter` (in input field) |
| **PROCESS** | Convert raw IPs to CIDR /32 format | `Tab` + `Enter` |
| **COPY TF** | Copy Terraform list to clipboard | `Tab` + `Enter` |
| **SAVE JSON** | Export data to JSON file | `Tab` + `Enter` |
| **QUIT** | Exit the application | `Esc` or `Ctrl+C` |

### Status Indicators

The summary bar shows:
- **Raw IPs: [X]** - Number of valid IPv4 addresses found
- **Processed: [X]** - Number of CIDR blocks generated
- **File: [name]** - Currently loaded source file

### Keyboard Navigation

| Key | Action |
|-----|--------|
| `Tab` | Navigate between panels and buttons |
| `Arrow Keys` | Navigate file browser and data tables |
| `Enter` | Select file / Click button |
| `Esc` | Quit application |
| `Ctrl+C` | Force quit (emergency exit) |

---

## Export Options

### Clipboard Export (COPY TF)

**Best for:** Quick paste into Terraform files

**Output format:**
```
["192.168.1.1/32","10.0.0.1/32","172.16.0.1/32"]
```

**Usage:**
1. Click **COPY TF**
2. Open your Terraform configuration file
3. Paste at the appropriate location

### JSON Export (SAVE JSON)

**Best for:** Audit trails, automation, and record-keeping

**Output file location:** `output/terraform_iocs_<count>_<timestamp>.json`

**JSON structure:**
```json
{
  "export_timestamp": "2024-01-10T20:43:07.827762",
  "source_file": "/path/to/input/sample.csv",
  "source_name": "sample.csv",
  "ipv4_count": 3,
  "terraform_list": "[\"192.168.1.1/32\",\"10.0.0.1/32\",\"172.16.0.1/32\"]",
  "cidr_blocks": [
    "192.168.1.1/32",
    "10.0.0.1/32",
    "172.16.0.1/32"
  ]
}
```

**Field descriptions:**

| Field | Description | Example |
|-------|-------------|---------|
| `export_timestamp` | ISO 8601 timestamp of export | `2024-01-10T20:43:07.827762` |
| `source_file` | Full path to source file | `/path/to/input/sample.csv` |
| `source_name` | Source filename only | `sample.csv` |
| `ipv4_count` | Number of IPs processed | `3` |
| `terraform_list` | HCL-formatted list (with quotes) | `["IP/32",...]` |
| `cidr_blocks` | Clean CIDR array | `["IP/32",...]` |

---

## Using the Output in Terraform

### AWS Security Group Example

```hcl
# security_groups.tf
resource "aws_security_group_rule" "ingress_rules" {
  type        = "ingress"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = [
    "192.168.1.1/32",
    "10.0.0.1/32",
    "172.16.0.1/32"
  ]
}
```

### Azure Network Security Group Example

```hcl
# azure_nsg.tf
resource "azurerm_network_security_rule" "allow_threat_ips" {
  name                        = "allow-known-threats"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "443"
  source_address_prefixes     = [
    "192.168.1.1/32",
    "10.0.0.1/32",
    "172.16.0.1/32"
  ]
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.example.name
  network_security_group_name = azurerm_network_security_group.example.name
}
```

### Loading from JSON (Terraform)

```hcl
# main.tf
locals {
  ioc_data = jsondecode(file("${path.module}/output/terraform_iocs_10_20240110_204307.json"))
  cidr_blocks = local.ioc_data.cidr_blocks
}

resource "aws_security_group_rule" "ingress_rules" {
  type        = "ingress"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = local.cidr_blocks
}
```

---

## Troubleshooting

### Installation Issues

**Problem: `python` command not found (Windows)**
```
Solution:
1. Download Python from python.org
2. During installation, check "Add Python to PATH"
3. Restart your terminal
4. Try 'py' instead of 'python'
```

**Problem: `python3` command not found (Linux/macOS)**
```bash
# Install Python 3
sudo apt install python3 python3-pip python3-venv -y    # Ubuntu/Debian
brew install python@3.11                                # macOS
```

**Problem: Permission denied during installation**
```bash
# Linux/macOS: Use a virtual environment instead of sudo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Problem: Dependencies fail to install**
```bash
# Upgrade pip first
pip install --upgrade pip

# Then try again
pip install -r requirements.txt
```

### Application Issues

**Problem: "No valid IPv4 addresses found"**
- Verify your file contains valid IPv4 addresses (e.g., `192.168.1.1`)
- Check that the file format is supported (CSV/TSV/TXT with common delimiters)
- Try opening the file in a text editor to verify the content
- Ensure the file is not empty

**Problem: "Invalid CSV format"**
- Try a different delimiter (comma, semicolon, tab, pipe)
- Ensure the file is not corrupted
- Check for special characters that might interfere
- Try saving the file as UTF-8 encoded CSV

**Problem: "Unsupported file type"**
- The application only supports: `.csv`, `.tsv`, `.txt`, `.log`
- Rename your file to have one of these extensions

**Problem: Clipboard not working (Linux)**
```bash
# Install clipboard support
sudo apt install xclip -y           # X11
sudo apt install wl-clipboard -y    # Wayland
```

**Problem: Clipboard not working (Windows/macOS)**
- Ensure your terminal has clipboard permissions
- Try running as administrator (Windows)
- Check that no other application is blocking clipboard access

**Problem: Application won't start**
```bash
# Make sure you're in the correct directory
ls app.py  # Should exist

# Check Python version
python --version  # Should be 3.8+

# Try the launcher
python launcher.py
```

**Problem: Terminal size issues**
- The application requires a minimum terminal size of 80x24
- Resize your terminal window to be larger
- On Windows, try PowerShell instead of Command Prompt

### File Issues

**Problem: `input/` directory doesn't exist**
- The application creates it automatically on first run
- Or create it manually: `mkdir input` (Linux/macOS) or `mkdir input` (Windows)

**Problem: Can't find my file**
- Ensure the file is in the `input/` directory
- Use the full path with manual path input
- Check file permissions: `ls -la input/` (Linux/macOS)

**Problem: Output file not created**
- Check the `output/` directory exists
- Verify you have write permissions
- Look for notification messages in the application

### Performance Issues

**Problem: Large files take too long to load**
- For files with 10,000+ IPs, consider splitting into smaller files
- The application works best with files under 10MB
- Use a more powerful machine if processing millions of IPs

### Getting Help

If you encounter issues not covered here:

1. **Check the GitHub repository:** [https://github.com/srflmr/terraform-ipv4-ioc-normalizer](https://github.com/srflmr/terraform-ipv4-ioc-normalizer)
2. **Open an issue:** Include your OS, Python version, and error message
3. **Check the logs:** The application shows error messages in the status bar

---

## Tips and Best Practices

1. **Always backup your original files** before processing
2. **Use descriptive filenames** for your input files (e.g., `threat_feed_2024-01.csv`)
3. **Keep a copy of exported JSON files** for audit trails
4. **Test with a small sample** before processing large files
5. **Use the JSON export** for automation and CI/CD pipelines
6. **Validate your Terraform** configuration after applying CIDR blocks

---

## Quick Reference Card

```
INSTALLATION
  Windows:  python launcher.py
  Linux:    python3 launcher.py
  macOS:    python3 launcher.py

RUNNING
  Manual setup:
    python -m venv .venv
    source .venv/bin/activate  (Linux/macOS)
    .venv\Scripts\activate     (Windows)
    pip install -r requirements.txt
    python app.py

KEYBOARD SHORTCUTS
  Tab      - Navigate
  Enter    - Select
  Esc      - Quit
  Arrows   - Move selection

WORKFLOW
  1. Place file in input/
  2. Select file from browser
  3. Click PROCESS
  4. Copy TF or SAVE JSON
```

---

**For more information, visit:** [https://github.com/srflmr/terraform-ipv4-ioc-normalizer](https://github.com/srflmr/terraform-ipv4-ioc-normalizer)
