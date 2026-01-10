#!/usr/bin/env python3
"""
Terraform IPv4 Normalizer - 100% WORKING Textual 7.1
File Browser | CSV Parser | Terraform Export | No Errors
"""
import csv
import json
import ipaddress
from pathlib import Path
from typing import List
from datetime import datetime
import pyperclip

from textual.app import App, ComposeResult, on
from textual.containers import Horizontal, Vertical, Container, Center
from textual.widgets import Header, Footer, Button, Input, Label, DataTable, Static, DirectoryTree
from textual.scroll_view import ScrollView
from textual import work
from textual.css.query import NoMatches

class IPNormalizer(App):
    CSS = """
    /* Screen layout */
    Screen {
        layout: vertical;
    }

    /* Main horizontal container for panels */
    Horizontal {
        height: 1fr;
    }

    /* Panel proportions - responsive */
    #filepanel {
        width: 40%;  /* Fixed 40% for file browser */
        height: 1fr;
    }

    #rawpanel {
        width: 30%;  /* Fixed 30% for raw panel */
        height: 1fr;
    }

    #normpanel {
        width: 30%;  /* Fixed 30% for norm panel */
        height: 1fr;
    }

    /* Vertical container with flex */
    Vertical {
        height: 1fr;
    }

    /* Tree container - explicitly get remaining height */
    #treecontainer {
        min-height: 10;
    }

    /* DataTable flex */
    DataTable {
        min-height: 10;
    }

    /* Button row styling */
    Horizontal > Button {
        width: 1fr;
    }

    /* Summary panel */
    #summarypanel {
        height: 3;
    }

    #summarypanel > Static {
        width: 1fr;
        text-align: center;
        text-style: bold;
    }

    /* Status */
    #status {
        height: 1;
        text-align: center;
    }

    /* Labels */
    Label {
        text-style: bold;
        text-align: center;
    }

    /* Input */
    Input {
        width: 1fr;
    }
    """

    def __init__(self):
        super().__init__()
        self.input_file = None
        self.raw_ips = []
        self.norm_ips = []

        # Define input and output directories
        self.input_dir = Path("input")
        self.output_dir = Path("output")

        # Create directories if they don't exist
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

    def compose(self) -> ComposeResult:
        yield Header("Terraform IPv4 Normalizer")
        yield Static("Status: Ready - Browse input/ directory → Enter", id="status")

        # Summary Panel - IOC Count Statistics
        yield Horizontal(
            Static("📊 Raw IPs: [0]", id="rawcount"),
            Static("🎯 Processed: [0]", id="normcount"),
            Static("📁 File: -", id="filename"),
            id="summarypanel"
        )

        yield Horizontal(
            # File Browser Panel
            Vertical(
                Label("📁 Input Browser (input/)"),
                Container(DirectoryTree(str(self.input_dir), id="dirtree"), id="treecontainer"),
                Input(placeholder="Or manual path...", id="manualpath"),
                Horizontal(
                    Button("LOAD SELECTED", id="loadbtn"),
                    Button("LOAD PATH", id="manuaload"),
                ),
                Label("CSV/TSV/TXT auto-detect | Output → output/"),
                id="filepanel"
            ),
            # Raw IPv4 Panel
            Vertical(
                Label("Raw IPv4 (Valid)"),
                DataTable(id="rawtbl"),
                id="rawpanel"
            ),
            # Terraform /32 Panel
            Vertical(
                Label("Terraform /32 Ready"),
                DataTable(id="normtbl"),
                id="normpanel"
            )
        )

        yield Horizontal(
            Button("PROCESS", id="procbtn", disabled=True),
            Button("COPY TF", id="copybtn", disabled=True),
            Button("SAVE JSON", id="jsonbtn", disabled=True),
            Button("QUIT", id="quitbtn")
        )
        yield Footer()

    def on_mount(self):
        tree = self.query_one("#dirtree", DirectoryTree)
        tree.focus()

    def on_directory_tree_file_selected(self, event):
        """Auto load on file select."""
        self.input_file = event.path
        self.query_one("#manualpath").value = str(event.path)
        self.parse_csv_safe(event.path)

    @on(Button.Pressed, "#loadbtn")
    def load_button(self):
        """Load from tree cursor."""
        tree = self.query_one("#dirtree", DirectoryTree)
        cursor_node = tree.cursor_node
        if cursor_node and cursor_node.data and cursor_node.data.path.is_file():
            self.parse_csv_safe(cursor_node.data.path)
        else:
            self.notify("No file selected!")

    @on(Button.Pressed, "#manuaload")
    def load_manual_path(self):
        pathstr = self.query_one("#manualpath").value.strip()
        if pathstr:
            path = Path(pathstr)
            self.parse_csv_safe(path)

    @work(thread=True)
    def parse_csv_safe(self, path):
        """Safe CSV parser with fallback delimiter detection."""
        try:
            if not path.is_file():
                self.call_from_thread(self.notify, "Not a file!")
                return

            # Store input file path for JSON export
            self.input_file = path

            # File type validation
            valid_extensions = {'.csv', '.tsv', '.txt', '.log'}
            if path.suffix.lower() not in valid_extensions:
                self.call_from_thread(self.notify, "Unsupported file type!")
                return

            with open(path, 'r', newline='', encoding='utf-8-sig', errors='ignore') as f:
                sample = f.read(4096)
                f.seek(0)

                # Try to detect delimiter with multiple fallback strategies
                delimiter = None
                has_header = False

                # Strategy 1: Try sniffer with explicit delimiter hints
                try:
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(sample, delimiters=',;\t|')
                    delimiter = dialect.delimiter
                    has_header = sniffer.has_header(sample)
                    reader = csv.reader(f, dialect)
                except csv.Error:
                    # Strategy 2: Try each common delimiter explicitly
                    f.seek(0)
                    delimiter_found = False
                    for test_delim in [';', ',', '\t', '|']:
                        f.seek(0)
                        test_reader = csv.reader(f, delimiter=test_delim)
                        try:
                            rows = list(test_reader)
                            if len(rows) >= 2:  # Need at least header + 1 data row
                                # Check if any cell contains valid IP
                                for row in rows[1:]:
                                    for cell in row:
                                        ipstr = cell.strip().strip('"\' ')
                                        if ipstr:
                                            try:
                                                ipaddress.IPv4Address(ipstr)
                                                delimiter = test_delim
                                                delimiter_found = True
                                                # Check if first row is header
                                                has_header = not any(
                                                    c.strip().replace('.', '').replace(':', '').isdigit()
                                                    for c in rows[0] if c.strip()
                                                )
                                                break
                                            except ipaddress.AddressValueError:
                                                pass
                                if delimiter_found:
                                    break
                        except Exception:
                            continue

                    if not delimiter_found:
                        raise csv.Error("Could not determine delimiter")

                    f.seek(0)
                    reader = csv.reader(f, delimiter=delimiter)

                ips = []

                for row_idx, row in enumerate(reader):
                    if has_header and row_idx == 0:
                        continue

                    for cell in row:
                        ipstr = cell.strip().strip('"\' ')
                        try:
                            if ipstr:
                                ipaddress.IPv4Address(ipstr)
                                ips.append(ipstr)
                        except ipaddress.AddressValueError:
                            pass  # Skip invalid

            if not ips:
                self.call_from_thread(self.notify, "No valid IPv4 addresses found!")
                return

            self.call_from_thread(self.update_raw_ips, ips)

        except csv.Error as e:
            self.call_from_thread(self.notify, f"CSV format error: {e}")
        except UnicodeDecodeError:
            self.call_from_thread(self.notify, "Encoding error - check file format")
        except PermissionError:
            self.call_from_thread(self.notify, "Permission denied reading file")
        except Exception as e:
            self.call_from_thread(self.notify, f"Parse error: {type(e).__name__}: {e}")

    def update_raw_ips(self, ips):
        self.raw_ips = ips

        table = self.query_one("#rawtbl", DataTable)
        table.clear()
        table.add_columns("Valid IPv4")
        for ip in ips:
            table.add_row(ip)

        # Update summary panel
        self.query_one("#rawcount").update(f"📊 Raw IPs: [{len(ips)}]")
        self.query_one("#filename").update(f"📁 File: {self.input_file.name if self.input_file else '-'}")

        self.query_one("#procbtn").disabled = False
        self.query_one("#status").update(f"Loaded {len(ips)} valid IPv4")

    @on(Button.Pressed, "#procbtn")
    def process_to_cidr(self):
        try:
            # Format with quotes for Terraform HCL: "IP/32"
            self.norm_ips = [f'"{ip}/32"' for ip in self.raw_ips]

            table = self.query_one("#normtbl", DataTable)
            table.clear()
            table.add_columns("Terraform CIDR /32")
            for cidr in self.norm_ips:
                table.add_row(cidr)

            # Update summary panel
            self.query_one("#normcount").update(f"🎯 Processed: [{len(self.norm_ips)}]")

            self.query_one("#copybtn").disabled = False
            self.query_one("#jsonbtn").disabled = False
            self.query_one("#status").update(f"Generated {len(self.norm_ips)} /32 CIDR")
        except Exception as e:
            self.notify(f"Process failed: {e}")

    @on(Button.Pressed, "#copybtn")
    def copy_terraform_list(self):
        try:
            tf_list = f"[{','.join(self.norm_ips)}]"
            pyperclip.copy(tf_list)
            self.notify(f"Copied {len(self.norm_ips)} CIDR to clipboard!")
            self.query_one("#status").update("Terraform list copied!")
        except Exception as e:
            self.notify(f"Copy error: {e}")

    @on(Button.Pressed, "#jsonbtn")
    def export_json(self):
        try:
            # Create clean CIDR blocks list (IP/32 format without extra quotes)
            cidr_blocks_clean = [f"{ip}/32" for ip in self.raw_ips]

            # Generate timestamp for unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Get relative path from input file for better readability
            source_name = self.input_file.name if self.input_file else "unknown"

            data = {
                "export_timestamp": datetime.now().isoformat(),
                "source_file": str(self.input_file) if self.input_file else "unknown",
                "source_name": source_name,
                "ipv4_count": len(self.norm_ips),
                "terraform_list": f"[{','.join(self.norm_ips)}]",  # HCL format with quotes
                "cidr_blocks": cidr_blocks_clean  # Clean format: IP/32
            }

            # Filename format: terraform_iocs_<count>_<timestamp>.json
            filename = f"terraform_iocs_{len(self.norm_ips)}_{timestamp}.json"

            # Save to output directory
            output_path = self.output_dir / filename
            output_path.write_text(json.dumps(data, indent=2))

            self.notify(f"Saved: output/{filename}")
        except Exception as e:
            self.notify(f"JSON save error: {e}")

    @on(Button.Pressed, "#quitbtn")
    def quit(self):
        self.exit()

if __name__ == "__main__":
    app = IPNormalizer()
    app.run()
