# Terraform IPv4 IoC Normalizer

<div align="center">

**A Textual TUI application to normalize IPv4 Indicators of Compromise (IoC) for Terraform configuration**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Textual](https://img.shields.io/badge/Textual-0.65%2B-teal)](https://github.com/Textualize/textual)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

[Features](#-features)  [Quick Start](#-quick-start)  [Documentation](#-documentation)  [Screenshots](#-screenshots)

</div>

---

## Overview

This application converts raw IPv4 addresses from CSV/TSV/TXT files into Terraform-ready CIDR /32 blocks. Designed for security analysts and threat intelligence teams who need to quickly format IP indicators for infrastructure-as-code security policies.

### What It Does

1. **Parse** IPv4 addresses from various delimited text files
2. **Validate** and extract only valid IPv4 addresses
3. **Convert** to Terraform HCL format (`"IP/32"`)
4. **Export** to JSON with timestamps for audit trails

---

## Features

- **Smart CSV Parsing** - Auto-detects delimiters (comma, semicolon, tab, pipe) with fallback strategies
- **Integrated File Browser** - Navigate and select files from `input/` directory with manual path input support
- **Real-time Statistics** - Live IOC count display, source file tracking, and processing status updates
- **Multiple Export Options** - Copy Terraform list to clipboard or export to JSON with unique filenames
- **Responsive TUI** - Adapts to terminal size with a clean 3-panel layout and keyboard navigation

---

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/srflmr/terraform-ipv4-ioc-normalizer.git
cd terraform-ipv4-ioc-normalizer

# Run the auto-launcher (sets up everything automatically)
# Windows (CMD/PowerShell):
python launcher.py

# Linux/macOS:
python3 launcher.py
```

The launcher will:
- Verify Python 3.8+ is installed
- Create a virtual environment (`.venv`)
- Ensure pip is available
- Install all dependencies from requirements.txt
- Launch the application

### Manual Installation

See the [USAGE.md](USAGE.md) for detailed platform-specific instructions (Windows/Linux/macOS).

```bash
# Create virtual environment
# Windows:
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS:
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [USAGE.md](USAGE.md) | Complete beginner-friendly guide with installation and usage instructions |
| [LICENSE](LICENSE) | MIT License |

---

## Project Structure

```
terraform-ipv4-ioc-normalizer/
├── app.py                  # Main application (Textual TUI)
├── launcher.py             # Auto-setup launcher
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── USAGE.md               # Detailed usage guide
├── LICENSE                # MIT License
├── .gitignore             # Git ignore rules
│
├── input/                 # INPUT: Place your CSV/TSV/TXT files here
│   └── sample.csv         # Example input file
│
└── output/                # OUTPUT: Generated JSON files
    └── terraform_iocs_*.json
```

---

## Dependencies

```
textual>=0.65.0,<1.0.0    # Terminal UI framework
rich>=14.0.0,<15.0.0       # Text rendering
pyperclip>=1.8.0,<2.0.0    # Clipboard operations
```

---

## Usage

### 1. Prepare Your Input

Place your CSV/TSV/TXT files containing IPv4 addresses in the `input/` directory.

**Example CSV (semicolon-delimited):**
```csv
IP Address;
102.129.165.164;
103.136.69.227;
103.231.74.10;
```

### 2. Load and Process

1. **Select a file** from the file browser OR enter the path manually
2. Click **LOAD SELECTED** or **LOAD PATH** (or press `Enter`)
3. Valid IPv4 addresses will appear in the "Raw IPv4" panel
4. Click **PROCESS** to convert to CIDR /32 blocks
5. Results appear in the "Terraform /32 Ready" panel

### 3. Export Your Data

- **Copy TF**: Copies Terraform list to clipboard
  ```hcl
  ["192.168.1.1/32","10.0.0.1/32"]
  ```

- **SAVE JSON**: Exports to `output/` directory with timestamp
  ```json
  {
    "export_timestamp": "2024-01-10T20:43:07.827762",
    "source_file": "input/sample.csv",
    "source_name": "sample.csv",
    "ipv4_count": 10,
    "terraform_list": "[\"192.168.1.1/32\",...]",
    "cidr_blocks": ["192.168.1.1/32",...]
  }
  ```

---

## Output Format

The exported JSON file contains:

| Field | Description | Example |
|-------|-------------|---------|
| `export_timestamp` | ISO 8601 timestamp | `2024-01-10T20:43:07.827762` |
| `source_file` | Full path to source file | `input/sample.csv` |
| `source_name` | Source filename only | `sample.csv` |
| `ipv4_count` | Number of IPs | `10` |
| `terraform_list` | Terraform HCL format list | `["IP/32",...]` |
| `cidr_blocks` | Clean CIDR list | `["IP/32",...]` |

---

## Terraform Usage Example

```hcl
# security_groups.tf
resource "aws_security_group_rule" "ingress_rules" {
  type        = "ingress"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = [
    "102.129.165.164/32",
    "103.136.69.227/32",
    "103.231.74.10/32",
  ]
}
```

---

## Keyboard Controls

| Key | Action |
|-----|--------|
| `Tab` | Navigate between panels |
| `Arrow Keys` | Navigate file browser |
| `Enter` | Load selected file / Activate button |
| `Esc` | Quit application |

---

## Troubleshooting

### "No valid IPv4 addresses found"
- Ensure your file contains valid IPv4 addresses (e.g., `192.168.1.1`)
- Check that the file format is supported (CSV/TSV/TXT with common delimiters)

### "Invalid CSV format"
- Try a different delimiter (comma, semicolon, tab, pipe)
- Ensure the file is not corrupted

### Clipboard not working
- On Linux, install `xclip` or `wl-clipboard`
- On Windows/macOS, clipboard support should work out of the box

For more troubleshooting tips, see [USAGE.md](USAGE.md).

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

Built with:
- [Textual](https://github.com/Textualize/textual) - Python TUI framework
- [Rich](https://github.com/Textualize/rich) - Text rendering library
- [pyperclip](https://github.com/asweigart/pyperclip) - Cross-platform clipboard

---

<div align="center">

**Made with ❤️ for the security community**

</div>
