# Terraform IPv4 IoC Normalizer

A cross-platform Terminal User Interface (TUI) application for normalizing IPv4 Indicators of Compromise (IoCs) into Terraform CIDR /32 format.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

## Features

- **Lazygit-style UI** - Clean, keyboard-driven interface with panel navigation
- **Multi-format CSV support** - Auto-detects delimiters (comma, semicolon, tab, pipe)
- **Smart parsing** - Automatically detects headers and extracts IPv4 addresses
- **IP Deduplication** - Automatically removes duplicate IPv4 addresses
- **Terraform format** - Converts IPs to CIDR /32 blocks for security groups
- **Export options** - Copy to clipboard or save as JSON + TXT
- **Cross-platform** - Works on Windows, Linux, and macOS

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (comes with Python)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/terraform-ipv4-ioc-normalizer.git
cd terraform-ipv4-ioc-normalizer

# Run the launcher (auto-sets up everything)
# Windows:
python launcher.py

# Linux/macOS:
python3 launcher.py
```

The launcher will:
- Create a virtual environment (`.venv`)
- Install all dependencies
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

### Updating the Application

If you have already cloned the repository and want to update to the latest version:

```bash
# Navigate to the project directory
cd terraform-ipv4-ioc-normalizer

# Pull the latest changes from repository
git pull origin main

# Activate virtual environment (if not already active)
# Windows:
.venv\Scripts\activate

# Linux/macOS:
source .venv/bin/activate

# Upgrade dependencies (recommended)
pip install --upgrade -r requirements.txt

# Run the application
python app.py
```

## Usage

1. **Place your CSV file** in the `input/` directory
2. **Select the file** from the Files panel (auto-loads on selection)
3. **Press `p`** to convert IPs to Terraform /32 format
4. **Press `c`** to copy to clipboard or `s` to save as JSON & TXT

See [USAGE.md](USAGE.md) for detailed documentation.

## Keybindings

| Key | Action |
|-----|--------|
| `1` | Jump to Files panel |
| `2` | Jump to Raw IPs panel |
| `3` | Jump to Terraform panel |
| `0` | Jump to Preview panel |
| `Tab` | Cycle to next panel |
| `p` | Process IPs to /32 |
| `c` | Copy to clipboard |
| `s` | Save as JSON & TXT |
| `r` | Refresh file browser |
| `?` | Show help |
| `q` | Quit application |

## Supported File Formats

| Format | Extensions | Delimiters |
|--------|------------|------------|
| CSV | `.csv` | Comma, semicolon, tab, pipe |
| TSV | `.tsv` | Tab |
| Text | `.txt`, `.log` | Auto-detected |

## Output

### Terraform List Format
```hcl
["192.168.1.1/32", "10.0.0.1/32", "172.16.0.1/32"]
```

### JSON Export Format
```json
{
  "export_timestamp": "2024-01-15T10:30:00.000000",
  "source_file": "input/sample.csv",
  "source_name": "sample.csv",
  "ipv4_count": 3,
  "terraform_list": "[\"192.168.1.1/32\",\"10.0.0.1/32\",\"172.16.0.1/32\"]",
  "cidr_blocks_form1": ["192.168.1.1/32", "10.0.0.1/32", "172.16.0.1/32"],
  "cidr_blocks_form2": "[192.168.1.1/32, 10.0.0.1/32, 172.16.0.1/32]"
}
```

### TXT Export Format (Plain Text)
```
192.168.1.1
10.0.0.1
172.16.0.1
```

## Project Structure

```
terraform-ipv4-ioc-normalizer/
├── app.py           # Main application
├── launcher.py      # Cross-platform launcher
├── requirements.txt # Python dependencies
├── input/           # Place CSV files here
├── output/          # JSON & TXT exports saved here
├── USAGE.md         # Detailed usage guide
└── README.md        # This file
```

## Requirements

- textual >= 0.65.0
- rich
- pyperclip

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
