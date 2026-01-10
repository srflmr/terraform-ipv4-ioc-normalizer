#!/usr/bin/env python3
"""
Terraform IPv4 Normalizer - Optimized Layout for 80x25 Terminal
Minimal Chrome | Split View | All Functions Working
"""
import csv
import json
import ipaddress
from pathlib import Path
from typing import List
from datetime import datetime
import pyperclip

from textual.app import App, ComposeResult, on
from textual.containers import Horizontal, Vertical, Container, Center, Grid
from textual.widgets import Header, Footer, Button, Input, Label, DataTable, Static, DirectoryTree
from textual.scroll_view import ScrollView
from textual import work
from textual.css.query import NoMatches

class IPNormalizer(App):
    """Modern, responsive Terraform IPv4 Normalizer with cross-platform support.

    UI Design Principles:
    - Responsive layout using viewport units (vw/vh) for terminal adaptation
    - Grid layout with proportional fr units for balanced distribution
    - Modern color scheme with semantic styling
    - Border titles for cleaner panel identification
    - Zebra striping for improved table readability
    - Smooth transitions and hover states for better UX
    """

    CSS = """
    /* ===== SCREEN & LAYOUT ===== */
    Screen {
        layout: vertical;
    }

    /* Header - docked at top with modern styling */
    Header {
        dock: top;
        height: 3;
        background: $accent;
        text-style: bold;
        text-align: center;
    }

    /* Status bar - visible and informative */
    #statusbar {
        dock: top;
        height: 2;
        padding: 0 2;
        background: $panel;
        border-bottom: solid $primary;
    }

    #statusbar > Static {
        width: 1fr;
        text-align: center;
        text-style: bold;
    }

    /* Footer - docked at bottom */
    Footer {
        dock: bottom;
    }

    /* Main content - fills available space */
    #maincontent {
        height: 1fr;
        padding: 1 1 0 1;
    }

    /* ===== RESPONSIVE GRID LAYOUT ===== */
    /* Grid for 3 panels - naturally responsive using fr units */
    #maingrid {
        layout: grid;
        grid-size: 3;
        grid-columns: 1fr 1fr 1fr;
        grid-rows: 1fr;
        grid-gutter: 1 1;
        height: 1fr;
    }

    /* ===== PANEL STYLING ===== */
    Vertical {
        height: 1fr;
    }

    /* Panel borders with modern styling using border_title */
    #filepanel, #rawpanel, #normpanel {
        border: thick $accent;
        background: $panel;
        padding: 0;
    }

    /* ===== COMPONENTS ===== */
    /* Labels hidden - using border titles instead */
    Label {
        display: none;
    }

    /* Directory Tree */
    #treecontainer {
        height: 1fr;
        padding: 0;
    }

    DirectoryTree {
        height: 1fr;
    }

    /* DataTable with modern styling */
    DataTable {
        height: 1fr;
        border: solid $accent;
    }

    /* Input field styling */
    Input {
        width: 1fr;
        height: 1;
        margin: 0;
        padding: 0 1;
        border: solid $primary;
    }

    Input:focus {
        border: thick $accent;
        background: $boost;
    }

    /* ===== BUTTON STYLING ===== */
    /* File panel button container */
    #filebtns {
        height: 3;
        padding: 1 0 0 0;
    }

    /* File panel buttons */
    #filebtns > Button {
        width: 1fr;
        min-width: 8;
        height: 1;
        margin: 0 0;
    }

    #filebtns > Button:hover {
        background: $boost;
        text-style: bold;
    }

    /* Refresh button */
    #refreshbtn {
        width: 1fr;
        min-width: 10;
        height: 1;
        margin: 0;
        padding: 0;
    }

    #refreshbtn:hover {
        background: $success;
        text-style: bold;
    }

    /* Action buttons bar */
    #actionbar {
        height: 3;
        padding: 1 0 0 0;
    }

    #actionbar > Button {
        width: 1fr;
        min-width: 12;
        margin: 0 0;
        height: 1;
    }

    #actionbar > Button:hover {
        text-style: bold;
        background: $boost;
    }

    /* Disabled button styling */
    Button:disabled {
        opacity: 0.5;
        text-style: dim;
    }

    Button:disabled:hover {
        background: $panel;
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
        """Compose the UI with modern border titles and responsive layout."""
        # Header - docked at top
        yield Header("Terraform IPv4 Normalizer")

        # Status bar - at top, below header, for maximum visibility
        with Horizontal(id="statusbar"):
            yield Static("Ready | Raw: 0 | Norm: 0 | File: -", id="status")

        # Main content area
        with Vertical(id="maincontent"):
            # Main grid with 3 panels
            with Grid(id="maingrid"):
                # File Browser Panel
                with Vertical(id="filepanel"):
                    yield Container(DirectoryTree(str(self.input_dir), id="dirtree"), id="treecontainer")
                    yield Input(placeholder="Or enter path...", id="manualpath")
                    with Horizontal(id="filebtns"):
                        yield Button("Load", id="loadbtn")
                        yield Button("Path", id="manuaload")
                    yield Button("Refresh", id="refreshbtn", variant="success")

                # Raw IPv4 Panel
                with Vertical(id="rawpanel"):
                    yield DataTable(id="rawtbl")

                # Terraform /32 Panel
                with Vertical(id="normpanel"):
                    yield DataTable(id="normtbl")

            # Action buttons - above footer
            with Horizontal(id="actionbar"):
                yield Button("Process", id="procbtn", disabled=True)
                yield Button("Copy TF", id="copybtn", disabled=True)
                yield Button("Save JSON", id="jsonbtn", disabled=True)
                yield Button("Quit", id="quitbtn")

        # Footer - docked at bottom
        yield Footer()

    def on_mount(self):
        """Set up border titles and initial focus."""
        # Set border titles for panels (modern Textual approach)
        try:
            filepanel = self.query_one("#filepanel", Vertical)
            filepanel.border_title = "[ Files ]"
            filepanel.border_subtitle = "input/"

            rawpanel = self.query_one("#rawpanel", Vertical)
            rawpanel.border_title = "[ Raw IPs ]"
            rawpanel.border_subtitle = "source"

            normpanel = self.query_one("#normpanel", Vertical)
            normpanel.border_title = "[ Terraform /32 ]"
            normpanel.border_subtitle = "output"
        except Exception:
            pass  # Border titles are optional

        # Focus on the directory tree for immediate navigation
        try:
            tree_container = self.query_one("#treecontainer", Container)
            for child in tree_container.children:
                if isinstance(child, DirectoryTree):
                    child.focus()
                    break
        except Exception:
            pass  # If tree not found, that's OK

    def on_directory_tree_file_selected(self, event):
        """Auto load on file select."""
        self.input_file = event.path
        self.query_one("#manualpath").value = str(event.path)
        self.parse_csv_safe(event.path)

    @on(Button.Pressed, "#loadbtn")
    def load_button(self):
        """Load from tree cursor."""
        # Get the DirectoryTree from the container
        tree_container = self.query_one("#treecontainer", Container)
        tree = None
        for child in tree_container.children:
            if isinstance(child, DirectoryTree):
                tree = child
                break

        if tree and tree.cursor_node and tree.cursor_node.data and tree.cursor_node.data.path.is_file():
            self.parse_csv_safe(tree.cursor_node.data.path)
        else:
            self.notify("No file selected!")

    @on(Button.Pressed, "#manuaload")
    def load_manual_path(self):
        pathstr = self.query_one("#manualpath").value.strip()
        if pathstr:
            path = Path(pathstr)
            self.parse_csv_safe(path)

    @on(Button.Pressed, "#refreshbtn")
    def refresh_directory(self):
        """Refresh the directory tree to show new files."""
        try:
            # Import time for unique ID generation
            import time

            # Get the container
            tree_container = self.query_one("#treecontainer", Container)

            # Store cursor position from old tree if it exists
            cursor_path = None
            try:
                old_tree = self.query_one("#dirtree", DirectoryTree)
                if old_tree.cursor_node and old_tree.cursor_node.data:
                    cursor_path = str(old_tree.cursor_node.data.path)
                old_tree.remove()
            except Exception:
                pass  # No old tree exists

            # Generate unique ID for the new tree
            unique_id = f"dirtree_{int(time.time() * 1000)}"

            # Mount new tree with unique ID
            new_tree = DirectoryTree(str(self.input_dir), id=unique_id)
            tree_container.mount(new_tree)

            # Restore cursor if path still exists
            if cursor_path and Path(cursor_path).exists():
                try:
                    new_tree.cursor_path = cursor_path
                except Exception:
                    pass  # Cursor restoration is optional

            # Count files for status
            file_count = len([f for f in self.input_dir.iterdir() if f.is_file()])
            self.notify(f"Directory refreshed: {file_count} files found")
            self.update_status(f"Directory refreshed - {file_count} files in input/")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.notify(f"Refresh error: {e}")

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
        """Update the raw IPs table with zebra striping enabled."""
        self.raw_ips = ips

        table = self.query_one("#rawtbl", DataTable)
        table.clear()

        # Add columns
        table.add_columns("Valid IPv4")

        # Enable zebra striping for better readability
        table.zebra_stripes = True

        # Add rows with data
        for ip in ips:
            table.add_row(ip)

        # Focus on the table for better UX
        table.focus()

        # Update status bar with all info
        self.update_status("Loaded")

        self.query_one("#procbtn").disabled = False

    def update_status(self, message: str):
        """Update status bar with compact format."""
        file_name = self.input_file.name if self.input_file else '-'
        status_text = f"{message} | Raw: {len(self.raw_ips)} | Norm: {len(self.norm_ips)} | {file_name}"
        self.query_one("#status").update(status_text)

    @on(Button.Pressed, "#procbtn")
    def process_to_cidr(self):
        """Process raw IPs to Terraform CIDR /32 format."""
        try:
            # Format with quotes for Terraform HCL: "IP/32"
            self.norm_ips = [f'"{ip}/32"' for ip in self.raw_ips]

            table = self.query_one("#normtbl", DataTable)
            table.clear()

            # Add columns
            table.add_columns("Terraform CIDR /32")

            # Enable zebra striping for better readability
            table.zebra_stripes = True

            # Add rows with formatted CIDR
            for cidr in self.norm_ips:
                table.add_row(cidr)

            # Focus on the normalized table
            table.focus()

            # Update status bar
            self.update_status("Processed")

            self.query_one("#copybtn").disabled = False
            self.query_one("#jsonbtn").disabled = False
        except Exception as e:
            self.notify(f"Process failed: {e}")

    @on(Button.Pressed, "#copybtn")
    def copy_terraform_list(self):
        try:
            tf_list = f"[{','.join(self.norm_ips)}]"
            pyperclip.copy(tf_list)
            self.notify(f"Copied {len(self.norm_ips)} CIDR to clipboard!")
            self.update_status("Terraform list copied!")
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
            self.update_status(f"Saved {filename}")
        except Exception as e:
            self.notify(f"JSON save error: {e}")

    @on(Button.Pressed, "#quitbtn")
    def quit(self):
        self.exit()

if __name__ == "__main__":
    app = IPNormalizer()
    app.run()
