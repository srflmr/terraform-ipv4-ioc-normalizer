# Usage Guide - Terraform IPv4 IoC Normalizer

A complete guide to installing and using the Terraform IPv4 IoC Normalizer on Windows, Linux, and macOS.

---

## Table of Contents

1. [What is This Tool?](#what-is-this-tool)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Preparing Your Data](#preparing-your-data)
5. [Running the Application](#running-the-application)
6. [Step-by-Step Workflow](#step-by-step-workflow)
7. [Keyboard Reference](#keyboard-reference)
8. [Export Options](#export-options)
9. [Using in Terraform](#using-in-terraform)
10. [Troubleshooting](#troubleshooting)

---

## What is This Tool?

A **Lazygit-style Terminal User Interface (TUI)** application that converts raw IPv4 addresses into Terraform CIDR /32 blocks for security groups.

**Features:**
- Clean, keyboard-driven interface (no mouse required)
- Auto-detects CSV delimiters (comma, semicolon, tab, pipe)
- Validates and extracts IPv4 addresses automatically
- Copy to clipboard or export to JSON
- Cross-platform (Windows, Linux, macOS)

---

## System Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10+, Ubuntu 20.04+, macOS 11+ |
| **Python** | Python 3.8 or higher |
| **Memory** | 512 MB RAM |
| **Disk** | 100 MB for dependencies |
| **Terminal** | Any modern terminal emulator |

---

## Installation

### Quick Install (Recommended)

The launcher handles everything automatically:

```bash
# Windows
python launcher.py

# Linux/macOS
python3 launcher.py
```

The launcher will:
- Verify Python 3.8+
- Create virtual environment (`.venv`)
- Install dependencies
- Launch the application

### Manual Installation

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

### Linux Clipboard Support

For clipboard functionality on Linux:

```bash
# X11-based systems
sudo apt install xclip -y

# Wayland-based systems
sudo apt install wl-clipboard -y
```

---

## Preparing Your Data

### Supported File Formats

| Format | Extensions | Delimiters |
|--------|------------|------------|
| CSV | `.csv` | Comma, semicolon, tab, pipe |
| TSV | `.tsv` | Tab |
| Text | `.txt`, `.log` | Auto-detected |

### Example Input Files

**Semicolon-delimited CSV:**
```csv
IP Address;
102.129.165.164;
103.136.69.227;
103.231.74.10;
```

**Comma-delimited CSV:**
```csv
indicator,value
192.168.1.1,malicious
10.0.0.1,suspicious
```

**Plain text (one IP per line):**
```
192.168.1.1
10.0.0.1
172.16.0.1
```

### File Placement

Place your input files in the `input/` directory (created automatically on first run).

---

## Running the Application

### Quick Start

```bash
# Windows
python launcher.py

# Linux/macOS
python3 launcher.py
```

### Running After First Setup

```bash
# Windows
.venv\Scripts\activate
python app.py

# Linux/macOS
source .venv/bin/activate
python app.py
```

---

## Step-by-Step Workflow

### Interface Layout

```
┌─────────────────────────────────────────────────┐
│ IPNormalizer                                   │
├──────────────┬──────────────────────────────────┤
│ ┌─ Files ───┐│                                  │
│ │ 📁 input/ ││  TERRAFORM IPv4 NORMALIZER        │
│ │ sample.csv││                                  │
│ └───────────┘│  Select a file to begin...       │
│ ┌─ Raw IPs ─┐│                                  │
│ │192.168... ││                                  │
│ └───────────┘│                                  │
│ ┌─Terraform─┐│                                  │
│ │"192.../32"││                                  │
│ └───────────┘│                                  │
├──────────────┴──────────────────────────────────┤
│ <1>Files  <2>Raw  <3>TF  <0>Preview │ <p>Process │
└─────────────────────────────────────────────────┘
```

### Workflow

1. **Place CSV file** in `input/` directory
2. **Select file** from Files panel (auto-loads on selection)
3. **Press `p`** to process IPs to Terraform /32 format
4. **Press `c`** to copy to clipboard OR **`s`** to save as JSON

---

## Keyboard Reference

### Panel Navigation

| Key | Action |
|-----|--------|
| `1` | Jump to Files panel |
| `2` | Jump to Raw IPs panel |
| `3` | Jump to Terraform panel |
| `0` | Jump to Preview panel |
| `Tab` | Cycle to next panel |
| `q` | Quit application |

### Actions

| Key | Action |
|-----|--------|
| `p` | Process IPs to /32 format |
| `c` | Copy Terraform list to clipboard |
| `s` | Save as JSON |
| `r` | Refresh file browser |
| `?` | Show help |

### File Browser

| Key | Action |
|-----|--------|
| `Arrow Keys` | Navigate files |
| `Enter` | Select file (auto-loads) |

---

## Export Options

### Copy to Clipboard (`c`)

**Format:** `["192.168.1.1/32","10.0.0.1/32"]`

**Usage:** Paste directly into Terraform configuration:
```hcl
cidr_blocks = ["192.168.1.1/32","10.0.0.1/32"]
```

### Save as JSON (`s`)

**File location:** `output/terraform_iocs_<count>_<timestamp>.json`

**Format:**
```json
{
  "export_timestamp": "2024-01-15T10:30:00.000000",
  "source_file": "input/sample.csv",
  "source_name": "sample.csv",
  "ipv4_count": 3,
  "terraform_list": "[\"192.168.1.1/32\",\"10.0.0.1/32\"]",
  "cidr_blocks": [
    "192.168.1.1/32",
    "10.0.0.1/32",
    "172.16.0.1/32"
  ]
}
```

---

## Using in Terraform

### AWS Security Group

```hcl
resource "aws_security_group_rule" "ingress" {
  type        = "ingress"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = ["192.168.1.1/32", "10.0.0.1/32"]
}
```

### Load from JSON

```hcl
locals {
  ioc_data = jsondecode(file("${path.module}/output/terraform_iocs_3_20240115.json"))
}

resource "aws_security_group_rule" "ingress" {
  cidr_blocks = local.ioc_data.cidr_blocks
  # ... other config
}
```

---

## Troubleshooting

### "No valid IPv4 addresses found"
- Verify file contains valid IPv4 addresses (e.g., `192.168.1.1`)
- Check file is supported format (.csv, .tsv, .txt, .log)

### "Unsupported file type"
- Only `.csv`, `.tsv`, `.txt`, `.log` files are supported
- Rename file to have correct extension

### Clipboard not working (Linux)
```bash
sudo apt install xclip -y          # X11
sudo apt install wl-clipboard -y   # Wayland
```

### Application won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Check you're in correct directory
ls app.py

# Try the launcher
python launcher.py
```

### Terminal size issues
- Minimum terminal size: 80x24
- Resize terminal window if needed
- On Windows, try PowerShell instead of CMD

---

## Tips

1. **Backup original files** before processing
2. **Use descriptive filenames** (e.g., `threat_feed_2024-01.csv`)
3. **Test with sample data** before processing large files
4. **Keep JSON exports** for audit trails
5. **Use JSON export** for automation pipelines

---

**For more information:** [https://github.com/srflmr/terraform-ipv4-ioc-normalizer](https://github.com/srflmr/terraform-ipv4-ioc-normalizer)
