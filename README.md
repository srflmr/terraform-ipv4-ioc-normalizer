# Terraform IPv4 IoC Normalizer

<div align="center">

**A Textual TUI application to normalize IPv4 Indicators of Compromise (IoC) for Terraform configuration**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Textual](https://img.shields.io/badge/Textual-7.1.0-teal)](https://github.com/Textualize/textual)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Screenshots](#screenshots) • [Project Structure](#project-structure)

</div>

---

## 🎯 Overview

This application converts raw IPv4 addresses from CSV/TSV/TXT files into Terraform-ready CIDR /32 blocks. Designed for security analysts and threat intelligence teams who need to quickly format IP indicators for infrastructure-as-code security policies.

### What It Does

1. **Parse** IPv4 addresses from various delimited text files
2. **Validate** and extract only valid IPv4 addresses
3. **Convert** to Terraform HCL format (`"IP/32"`)
4. **Export** to JSON with timestamps for audit trails

---

## ✨ Features

- 🔍 **Smart CSV Parsing**
  - Auto-detects delimiters (comma, semicolon, tab, pipe)
  - Fallback strategies for non-standard formats
  - Handles files with headers

- 📁 **Integrated File Browser**
  - Navigate and select files from `input/` directory
  - Manual path input support
  - File type validation

- 📊 **Real-time Statistics**
  - Live IOC count display
  - Source file tracking
  - Processing status updates

- 📋 **Multiple Export Options**
  - Copy Terraform list to clipboard
  - Export to JSON with timestamps
  - Unique filenames prevent data loss

- 🎨 **Responsive TUI**
  - Adapts to terminal size
  - Clean 3-panel layout
  - Keyboard navigation

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/terraform-ipv4-ioc-normalizer.git
cd terraform-ipv4-ioc-normalizer

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Using the Launcher

```bash
python launcher.py
```

The launcher will automatically set up the environment and run the app.

---

## 🚀 Usage

### 1. Prepare Your Input

Place your CSV/TSV/TXT files containing IPv4 addresses in the `input/` directory.

**Example CSV (semicolon-delimited):**
```csv
IP Address
102.129.165.164;
103.136.69.227;
103.231.74.10;
```

**Example CSV (comma-delimited):**
```csv
indicator,value
192.168.1.1,malicious
10.0.0.1,suspicious
```

### 2. Load and Process

1. **Select a file** from the file browser OR enter the path manually
2. Click **LOAD SELECTED** or **LOAD PATH**
3. Valid IPv4 addresses will appear in the "Raw IPv4" panel
4. Click **PROCESS** to convert to CIDR /32 blocks
5. Results appear in the "Terraform /32 Ready" panel

### 3. Export Your Data

- **Copy TF**: Copies Terraform list to clipboard
  ```
  ["192.168.1.1/32","10.0.0.1/32"]
  ```

- **SAVE JSON**: Exports to `output/` directory with timestamp
  ```json
  {
    "export_timestamp": "2026-01-10T20:43:07.827762",
    "source_file": "input/sample_ioc.csv",
    "ipv4_count": 10,
    "terraform_list": "[\"192.168.1.1/32\",...]",
    "cidr_blocks": ["192.168.1.1/32",...]
  }
  ```

---

## 📂 Project Structure

```
terraform-ipv4-ioc-normalizer/
├── app.py                  # Main application
├── launcher.py             # Auto-setup launcher
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
│
├── input/                 # INPUT: Place your CSV files here
│   └── sample_ioc.csv
│
└── output/                # OUTPUT: Generated JSON files
    └── terraform_iocs_10_20260110_204307.json
```

---

## 🔧 Dependencies

```
textual>=0.65.0,<1.0.0    # Terminal UI framework
rich>=14.0.0,<15.0.0       # Text rendering
pyperclip>=1.8.0,<2.0.0    # Clipboard operations
```

---

## 📝 Output Format

The exported JSON file contains:

| Field | Description | Example |
|-------|-------------|---------|
| `export_timestamp` | ISO 8601 timestamp | `2026-01-10T20:43:07.827762` |
| `source_file` | Full path to source file | `input/sample_ioc.csv` |
| `source_name` | Source filename only | `sample_ioc.csv` |
| `ipv4_count` | Number of IPs | `10` |
| `terraform_list` | Terraform HCL format list | `["IP/32",...]` |
| `cidr_blocks` | Clean CIDR list | `["IP/32",...]` |

---

## 🎯 Terraform Usage Example

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

## ⌨️ Keyboard Controls

| Key | Action |
|-----|--------|
| `Tab` | Navigate between panels |
| `Arrow Keys` | Navigate file browser |
| `Enter` | Load selected file |
| `Esc` | Quit application |

---

## 🐛 Troubleshooting

### "No valid IPv4 addresses found"
- Ensure your file contains valid IPv4 addresses (e.g., `192.168.1.1`)
- Check that the file format is supported (CSV/TSV/TXT with common delimiters)

### "Invalid CSV format"
- Try a different delimiter (comma, semicolon, tab, pipe)
- Ensure the file is not corrupted

### Clipboard not working
- On Linux, ensure `xclip` or `wl-clipboard` is installed
- On Windows/macOS, clipboard support should work out of the box

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

Built with:
- [Textual](https://github.com/Textualize/textual) - Awesome Python TUI framework
- [Rich](https://github.com/Textualize/rich) - Text rendering library
- [pyperclip](https://github.com/asweigart/pyperclip) - Cross-platform clipboard

---

<div align="center">

**Made with ❤️ for the security community**

</div>
