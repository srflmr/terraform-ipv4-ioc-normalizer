#!/usr/bin/env python3
"""
Terraform IPv4 Normalizer - True Lazygit-Style UI

Based on actual Lazygit structure:
- Left side panels (Files, Raw IPs, Terraform) - stacked vertically
- Right main panel (Preview/Details) - takes remaining space
- Top information bar
- Bottom options menu bar
- Panel switching with number keys
- Green border for focused panel (ActiveBorderColor)
"""
import csv
import json
import ipaddress
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import pyperclip

from textual.app import App, ComposeResult, on
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import (
    Header, Footer, DataTable, Static,
    DirectoryTree
)
from textual import work
from textual.reactive import reactive


class IPNormalizer(App):
    """True Lazygit-style Terraform IPv4 Normalizer.

    UI Layout (Lazygit pattern):
    ┌─────────────────────────────────────────────────────┐
    │ Header: Terraform IPv4 Normalizer                   │
    ├────────────────┬────────────────────────────────────┤
    │ ┌─ Files ────┐│                                    │
    │ │ 📁 input/  ││                                    │
    │ │ sample.csv ││         Preview Panel               │
    │ └────────────┘│         (Main View)                │
    │ ┌─ Raw IPs ──┐│                                    │
    │ │ 192.168... ││                                    │
    │ │ 10.0.0...  ││                                    │
    │ └────────────┘│                                    │
    │ ┌─ Terraform ─┐│                                    │
    │ │ "192.../32" ││                                    │
    │ │ "10.../32"  ││                                    │
    │ └────────────┘│                                    │
    ├────────────────┴────────────────────────────────────┤
    │ <1>Files  <2>Raw  <3>TF  <0>Prev │ <p>Proc <c>Copy │
    └─────────────────────────────────────────────────────┘
    """

    CSS = """
    /* ===== LAZYGIT COLOR SCHEME ===== */
    Screen {
        background: $background;
    }

    /* ===== HEADER ===== */
    Header {
        background: $primary;
        text-style: bold;
        padding: 0 1;
        height: 1;
    }

    /* ===== MAIN LAYOUT ===== */
    /* Main horizontal container */
    #main_layout {
        height: 1fr;
        layout: horizontal;
    }

    /* Left side panels container */
    #left_panels {
        width: 35;
        min-width: 30;
        layout: vertical;
    }

    /* Right main panel */
    #main_panel {
        height: 1fr;
    }

    /* ===== PANELS ===== */
    /* Individual panels on the left */
    .panel {
        border: solid $primary;
        padding: 0;
    }

    .panel:focus {
        border: thick green;
    }

    /* Files Panel */
    #files_panel {
        height: 12;
    }

    /* Raw IPs Panel */
    #raw_panel {
        height: 1fr;
    }

    /* Terraform Panel */
    #tf_panel {
        height: 1fr;
    }

    /* Main Preview Panel */
    #preview_panel {
        height: 1fr;
        border: solid $primary;
    }

    #preview_panel:focus {
        border: thick green;
    }

    /* ===== COMPONENTS ===== */
    /* Directory tree */
    DirectoryTree {
        height: 1fr;
        border: none;
    }

    /* DataTable */
    DataTable {
        height: 1fr;
        border: none;
    }

    /* Preview content */
    #preview_content {
        height: 1fr;
        padding: 1 2;
    }

    /* ===== BOTTOM OPTIONS BAR ===== */
    #options_bar {
        height: 1;
        dock: bottom;
        background: $panel;
        border-top: solid $primary;
        padding: 0 1;
    }

    #options_bar > Static {
        text-align: center;
        text-style: dim;
    }
    """

    BINDINGS = [
        ("1", "focus_panel('files')", "Files"),
        ("2", "focus_panel('raw')", "Raw"),
        ("3", "focus_panel('tf')", "Terraform"),
        ("0", "focus_panel('preview')", "Preview"),
        ("tab", "cycle_panels", "Next"),
        ("p", "process_ips", "Process"),
        ("c", "copy_result", "Copy"),
        ("s", "save_json", "Save"),
        ("r", "refresh_tree", "Refresh"),
        ("q", "app.quit", "Quit"),
        ("?", "show_help", "Help"),
    ]

    # Reactive state
    raw_count = reactive(0)
    tf_count = reactive(0)

    def __init__(self):
        super().__init__()
        self.input_file: Optional[Path] = None
        self.raw_ips: List[str] = []
        self.norm_ips: List[str] = []

        # Define directories
        self.input_dir = Path("input")
        self.output_dir = Path("output")
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

    def compose(self) -> ComposeResult:
        """Compose the Lazygit-style UI."""
        # Header
        yield Header()

        # Main layout
        with Horizontal(id="main_layout"):
            # Left panels
            with Vertical(id="left_panels"):
                # Files Panel
                with Vertical(id="files_panel", classes="panel"):
                    yield DirectoryTree(str(self.input_dir), id="dir_tree")

                # Raw IPs Panel
                with Vertical(id="raw_panel", classes="panel"):
                    yield DataTable(id="raw_table")

                # Terraform Panel
                with Vertical(id="tf_panel", classes="panel"):
                    yield DataTable(id="tf_table")

            # Right main panel
            with Vertical(id="preview_panel"):
                yield Static(
                    """TERRAFORM IPv4 NORMALIZER

Select a file from the Files panel to begin.

Keybindings:
  1 - Files Panel    p - Process IPs
  2 - Raw IPs Panel  c - Copy Result
  3 - Terraform Panel s - Save JSON
  0 - Preview Panel  r - Refresh Files
  Tab - Cycle Panels q - Quit
  ? - Help

Workflow:
1. Select a CSV file from the Files panel (auto-loads)
2. Raw IPv4 addresses will appear in Raw IPs panel
3. Press p to convert to Terraform /32 format
4. Results appear in Terraform panel
5. Press c to copy or s to save JSON""",
                    id="preview_content"
                )

        # Bottom options bar
        with Horizontal(id="options_bar"):
            yield Static(
                " <1>Files  <2>Raw  <3>TF  <0>Preview │ "
                "<p>Process  <c>Copy  <s>Save  <r>Refresh  <?>Help  <q>Quit "
            )

        # Footer (optional, for command palette)
        yield Footer()

    def on_mount(self) -> None:
        """Initialize UI on mount."""
        # Set border titles
        self.query_one("#files_panel", Vertical).border_title = " Files"
        self.query_one("#raw_panel", Vertical).border_title = " Raw IPs"
        self.query_one("#tf_panel", Vertical).border_title = " Terraform /32"
        self.query_one("#preview_panel", Vertical).border_title = " Preview"

        # Set up tables
        raw_table = self.query_one("#raw_table", DataTable)
        raw_table.add_columns("IPv4 Address")
        raw_table.zebra_stripes = True

        tf_table = self.query_one("#tf_table", DataTable)
        tf_table.add_columns("Terraform CIDR /32")
        tf_table.zebra_stripes = True

        # Focus files panel initially
        self.query_one("#files_panel").focus()

    def watch_raw_count(self) -> None:
        """Update raw panel border subtitle when count changes."""
        panel = self.query_one("#raw_panel", Vertical)
        panel.border_subtitle = f"{self.raw_count} items"

    def watch_tf_count(self) -> None:
        """Update TF panel border subtitle when count changes."""
        panel = self.query_one("#tf_panel", Vertical)
        panel.border_subtitle = f"{self.tf_count} items"

    # ===== PANEL NAVIGATION =====
    def action_focus_panel(self, panel: str) -> None:
        """Focus a specific panel."""
        panel_map = {
            "files": "#files_panel",
            "raw": "#raw_panel",
            "tf": "#tf_panel",
            "preview": "#preview_panel",
        }
        if panel in panel_map:
            try:
                self.query_one(panel_map[panel]).focus()
            except Exception:
                pass

    def action_cycle_panels(self) -> None:
        """Cycle to next panel."""
        panels = ["#files_panel", "#raw_panel", "#tf_panel", "#preview_panel"]
        focused = self.focused
        if focused:
            for i, panel_id in enumerate(panels):
                try:
                    if focused == self.query_one(panel_id):
                        next_panel = panels[(i + 1) % len(panels)]
                        self.query_one(next_panel).focus()
                        break
                except Exception:
                    continue

    def action_show_help(self) -> None:
        """Show help in preview panel."""
        preview = self.query_one("#preview_content", Static)
        preview.update(
            """HELP - Terraform IPv4 Normalizer

Panel Navigation:
  1 - Files Panel: Browse and load CSV files
  2 - Raw IPs Panel: View extracted IPv4 addresses
  3 - Terraform Panel: View converted /32 CIDR blocks
  0 - Preview Panel: View details and help
  Tab - Cycle through panels

Actions:
  p - Process: Convert raw IPs to Terraform /32 format
  c - Copy: Copy Terraform list to clipboard
  s - Save: Export to JSON file in output/ directory
  r - Refresh: Refresh the file browser
  q - Quit: Exit the application

Supported File Formats:
  - CSV with comma, semicolon, tab, or pipe delimiter
  - Files: .csv, .tsv, .txt, .log
  - Auto-detects delimiter and header

Output:
  - Terraform list: ["192.168.1.1/32", ...]
  - JSON with metadata and CIDR blocks

Press any panel key to return to work."""
        )

    # ===== EVENT HANDLERS =====
    def on_directory_tree_file_selected(self, event) -> None:
        """Auto-load file when selected."""
        self.input_file = event.path
        self.parse_csv_safe(event.path)

    # ===== CORE ACTIONS =====
    @work(thread=True)
    def parse_csv_safe(self, path: Path) -> None:
        """Parse CSV file and extract IPv4 addresses."""
        try:
            if not path.is_file():
                self.call_from_thread(self.notify, "Not a file!")
                return

            self.input_file = path

            valid_extensions = {'.csv', '.tsv', '.txt', '.log'}
            if path.suffix.lower() not in valid_extensions:
                self.call_from_thread(self.notify, "Unsupported file type!")
                return

            with open(path, 'r', newline='', encoding='utf-8-sig', errors='ignore') as f:
                sample = f.read(4096)
                f.seek(0)

                # Detect delimiter
                delimiter = None
                has_header = False

                try:
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(sample, delimiters=',;\t|')
                    delimiter = dialect.delimiter
                    has_header = sniffer.has_header(sample)
                    reader = csv.reader(f, dialect)
                except csv.Error:
                    f.seek(0)
                    for test_delim in [';', ',', '\t', '|']:
                        f.seek(0)
                        test_reader = csv.reader(f, delimiter=test_delim)
                        try:
                            rows = list(test_reader)
                            if len(rows) >= 2:
                                for row in rows[1:]:
                                    for cell in row:
                                        ipstr = cell.strip().strip('"\' ')
                                        if ipstr:
                                            try:
                                                ipaddress.IPv4Address(ipstr)
                                                delimiter = test_delim
                                                has_header = not any(
                                                    c.strip().replace('.', '').isdigit()
                                                    for c in rows[0] if c.strip()
                                                )
                                                break
                                            except ipaddress.AddressValueError:
                                                pass
                                if delimiter:
                                    break
                        except Exception:
                            continue

                if not delimiter:
                    raise csv.Error("Could not determine delimiter")

                f.seek(0)
                reader = csv.reader(f, delimiter=delimiter)

                # Extract IPs
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
                            pass

            if not ips:
                self.call_from_thread(self.notify, "No valid IPv4 addresses found!")
                return

            self.call_from_thread(self.update_raw_ips, ips)

        except csv.Error as e:
            self.call_from_thread(self.notify, f"CSV error: {e}")
        except Exception as e:
            self.call_from_thread(self.notify, f"Parse error: {e}")

    def update_raw_ips(self, ips: List[str]) -> None:
        """Update the raw IPs table."""
        self.raw_ips = ips
        self.raw_count = len(ips)

        table = self.query_one("#raw_table", DataTable)
        table.clear()
        table.add_columns("IPv4 Address")

        for ip in ips:
            table.add_row(ip)

        table.focus()
        self.notify(f"Loaded {len(ips)} IPv4 addresses")

        # Update preview
        self.update_preview_with_summary()

    def action_process_ips(self) -> None:
        """Process raw IPs to Terraform /32 format."""
        if not self.raw_ips:
            self.notify("No raw IPs to process!")
            return

        self.norm_ips = [f'"{ip}/32"' for ip in self.raw_ips]
        self.tf_count = len(self.norm_ips)

        table = self.query_one("#tf_table", DataTable)
        table.clear()
        table.add_columns("Terraform CIDR /32")

        for cidr in self.norm_ips:
            table.add_row(cidr)

        table.focus()
        self.notify(f"Processed {len(self.norm_ips)} CIDR blocks")

        # Update preview
        self.update_preview_with_results()

    def update_preview_with_summary(self) -> None:
        """Update preview with file summary."""
        if not self.input_file:
            return

        preview = self.query_one("#preview_content", Static)
        filename = self.input_file.name
        sample_ips = "\n".join(f"  - {ip}" for ip in self.raw_ips[:5])
        more = f"\n  - ... and {len(self.raw_ips) - 5} more" if len(self.raw_ips) > 5 else ""

        preview.update(
            f"""FILE SUMMARY

File: {filename}
Path: {self.input_file.parent}
IPv4 Addresses: {len(self.raw_ips)}

Sample Addresses:
{sample_ips}{more}

Press p to convert to Terraform /32 format"""
        )

    def update_preview_with_results(self) -> None:
        """Update preview with Terraform results."""
        preview = self.query_one("#preview_content", Static)
        tf_list = f"[{','.join(self.norm_ips)}]"
        preview_list = tf_list[:100] + ('...' if len(tf_list) > 100 else '')

        preview.update(
            f"""TERRAFORM CONVERSION COMPLETE

Total CIDR Blocks: {len(self.norm_ips)}

Terraform List:
{preview_list}

Actions:
  c - Copy to clipboard
  s - Save as JSON

Ready to use in your Terraform configuration!"""
        )

    def action_copy_result(self) -> None:
        """Copy Terraform list to clipboard."""
        if not self.norm_ips:
            self.notify("No results to copy!")
            return

        try:
            tf_list = f"[{','.join(self.norm_ips)}]"
            pyperclip.copy(tf_list)
            self.notify(f"Copied {len(self.norm_ips)} CIDR blocks!")
        except Exception as e:
            self.notify(f"Copy failed: {e}")

    def action_save_json(self) -> None:
        """Export results to JSON."""
        if not self.norm_ips:
            self.notify("No results to save!")
            return

        try:
            cidr_blocks_clean = [f"{ip}/32" for ip in self.raw_ips]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            source_name = self.input_file.name if self.input_file else "unknown"

            data = {
                "export_timestamp": datetime.now().isoformat(),
                "source_file": str(self.input_file) if self.input_file else "unknown",
                "source_name": source_name,
                "ipv4_count": len(self.norm_ips),
                "terraform_list": f"[{','.join(self.norm_ips)}]",
                "cidr_blocks": cidr_blocks_clean
            }

            filename = f"terraform_iocs_{len(self.norm_ips)}_{timestamp}.json"
            output_path = self.output_dir / filename
            output_path.write_text(json.dumps(data, indent=2))

            self.notify(f"Saved: output/{filename}")

        except Exception as e:
            self.notify(f"Save failed: {e}")

    def action_refresh_tree(self) -> None:
        """Refresh the directory tree."""
        try:
            import time
            tree_container = self.query_one("#files_panel", Vertical)

            # Save current cursor
            cursor_path = None
            try:
                old_tree = self.query_one("#dir_tree", DirectoryTree)
                if old_tree.cursor_node and old_tree.cursor_node.data:
                    cursor_path = str(old_tree.cursor_node.data.path)
                old_tree.remove()
            except Exception:
                pass

            # Create new tree
            new_tree = DirectoryTree(str(self.input_dir), id=f"dir_tree_{int(time.time())}")
            tree_container.mount(new_tree)

            # Restore cursor
            if cursor_path and Path(cursor_path).exists():
                try:
                    new_tree.cursor_path = cursor_path
                except Exception:
                    pass

            file_count = len([f for f in self.input_dir.iterdir() if f.is_file()])
            self.notify(f"Refreshed: {file_count} files")

        except Exception as e:
            self.notify(f"Refresh error: {e}")


if __name__ == "__main__":
    app = IPNormalizer()
    app.run()
