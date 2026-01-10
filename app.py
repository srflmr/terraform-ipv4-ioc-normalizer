#!/usr/bin/env python3
"""
Terraform IPv4 Normalizer - Lazygit-Style UI

Inspired by Lazygit terminal UI with:
- Horizontal split layout (side panels 30% + main preview 70%)
- Panel jump keybindings (1, 2, 3, 0)
- Border titles with dynamic subtitles
- Green border for focused panel
- Bottom line with keybinding hints
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
    """Lazygit-style Terraform IPv4 Normalizer.

    UI Features:
    - Horizontal split: side panels (30%) + main preview (70%)
    - Panel jumps: 1=Files, 2=Raw IPs, 3=Terraform, 0=Preview
    - Green bold border for focused panel
    - Border titles with dynamic subtitles showing item counts
    - Bottom line with keybinding hints
    - Zebra striping for data tables
    """

    BINDINGS = [
        ("1", "focus_files", "Files"),
        ("2", "focus_raw", "Raw IPs"),
        ("3", "focus_norm", "Terraform"),
        ("0", "focus_preview", "Preview"),
        ("tab", "next_panel", "Next Panel"),
        ("p", "process_action", "Process"),
        ("c", "copy_action", "Copy"),
        ("s", "save_action", "Save"),
        ("r", "refresh_action", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    CSS = """
    /* ===== LAZYGIT-STYLE LAYOUT ===== */
    Screen {
        layout: vertical;
    }

    /* Header - compact like Lazygit */
    Header {
        dock: top;
        height: 1;
        background: $primary;
        text-style: bold;
    }

    /* Main horizontal split */
    #mainsplit {
        height: 1fr;
        layout: horizontal;
    }

    /* Side panels container (30% width) */
    #sidepanel {
        width: 30%;
        min-width: 25;
        layout: vertical;
    }

    /* Main preview panel (70% width) */
    #mainpreview {
        width: 70%;
        height: 1fr;
    }

    /* ===== PANEL STYLING ===== */
    /* All vertical panels (side panels + preview) */
    Vertical {
        height: 1fr;
        border: rounded $accent;
        padding: 0;
    }

    /* Focused panel - green bold border (Lazygit style) */
    Vertical:focus {
        border: thick green bold;
    }

    /* Individual panel heights */
    #filepanel, #rawpanel, #normpanel {
        height: 1fr;
    }

    /* ===== COMPONENT STYLING ===== */
    /* Hide labels - using border titles */
    Label {
        display: none;
    }

    /* Directory tree */
    #treecontainer {
        height: 1fr;
        padding: 0;
    }

    DirectoryTree {
        height: 1fr;
    }

    /* DataTable with zebra striping */
    DataTable {
        height: 1fr;
        border: none;
    }

    /* Input field */
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
    /* File buttons container */
    #filebtns {
        height: 1;
        padding: 0;
    }

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
        height: 1;
        margin: 0;
    }

    #refreshbtn:hover {
        background: $success;
        text-style: bold;
    }

    /* Action buttons container */
    #actionbtns {
        height: 1;
        padding: 0;
        dock: bottom;
    }

    #actionbtns > Button {
        width: 1fr;
        min-width: 10;
        margin: 0 0;
        height: 1;
    }

    #actionbtns > Button:hover {
        text-style: bold;
        background: $boost;
    }

    Button:disabled {
        opacity: 0.5;
        text-style: dim;
    }

    Button:disabled:hover {
        background: $panel;
    }

    /* ===== PREVIEW PANEL ===== */
    #previewcontent {
        height: 1fr;
        padding: 1 2;
        text-style: default;
    }

    #previewcontent Static {
        margin: 1 0;
    }

    .preview-title {
        text-style: bold;
        text-align: center;
        margin: 0 0 1 0;
    }

    .preview-label {
        text-style: dim;
        margin: 0 0 0 0;
    }

    .preview-value {
        text-style: bold;
        margin: 0 0 2 0;
    }

    /* ===== BOTTOM LINE STATUS ===== */
    #bottomline {
        height: 1;
        dock: bottom;
        padding: 0 1;
        background: $panel;
        border-top: solid $primary;
    }

    #bottomline > Static {
        width: 1fr;
        text-align: center;
        text-style: dim;
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
        """Compose Lazygit-style UI with horizontal split."""
        # Header
        yield Header("Terraform IPv4 Normalizer")

        # Main horizontal split
        with Horizontal(id="mainsplit"):
            # Side panels (left)
            with Vertical(id="sidepanel"):
                # Files Panel
                with Vertical(id="filepanel"):
                    yield Container(DirectoryTree(str(self.input_dir), id="dirtree"), id="treecontainer")
                    yield Input(placeholder="Or enter path...", id="manualpath")
                    with Horizontal(id="filebtns"):
                        yield Button("Load", id="loadbtn")
                        yield Button("Path", id="manuaload")
                    yield Button("Refresh", id="refreshbtn", variant="success")

                # Raw IPs Panel
                with Vertical(id="rawpanel"):
                    yield DataTable(id="rawtbl")

                # Terraform /32 Panel
                with Vertical(id="normpanel"):
                    yield DataTable(id="normtbl")

            # Main preview panel (right)
            with Vertical(id="mainpreview"):
                yield Static(
                    "[ Preview ]\n\n"
                    "Select an item from any panel to see details here.\n\n"
                    "Keybindings:\n"
                    "  1/2/3/0 - Jump to panel\n"
                    "  <tab> - Next panel\n"
                    "  <enter> - Load file\n"
                    "  p - Process IPs\n"
                    "  c - Copy to clipboard\n"
                    "  s - Save JSON\n"
                    "  r - Refresh\n"
                    "  q - Quit",
                    id="previewcontent"
                )

        # Action buttons bar
        with Horizontal(id="actionbtns"):
            yield Button("Process", id="procbtn", disabled=True)
            yield Button("Copy", id="copybtn", disabled=True)
            yield Button("Save", id="jsonbtn", disabled=True)
            yield Button("Quit", id="quitbtn")

        # Bottom line with keybinding hints
        with Horizontal(id="bottomline"):
            yield Static(" <1>Files  <2>Raw  <3>TF  <0>Preview  │ <enter>Load  <p>Process  <c>Copy  <s>Save  <r>Refresh  <q>Quit ")

        # Footer
        yield Footer()

    def on_mount(self):
        """Set up border titles and initial focus."""
        # Set border titles with panel jump indicators
        self.update_border_titles()

        # Focus on directory tree
        try:
            tree_container = self.query_one("#treecontainer", Container)
            for child in tree_container.children:
                if isinstance(child, DirectoryTree):
                    child.focus()
                    break
        except Exception:
            pass

    def update_border_titles(self):
        """Update border titles with Lazygit-style indicators."""
        try:
            file_panel = self.query_one("#filepanel", Vertical)
            file_panel.border_title = " Files"
            file_panel.border_subtitle = "input/"

            raw_panel = self.query_one("#rawpanel", Vertical)
            raw_panel.border_title = " Raw IPs"
            raw_panel.border_subtitle = f"{len(self.raw_ips)} items"

            norm_panel = self.query_one("#normpanel", Vertical)
            norm_panel.border_title = " Terraform /32"
            norm_panel.border_subtitle = f"{len(self.norm_ips)} items"

            preview_panel = self.query_one("#mainpreview", Vertical)
            preview_panel.border_title = " Preview"
            preview_panel.border_subtitle = "details"
        except Exception:
            pass

    # ===== PANEL JUMP ACTIONS =====
    def action_focus_files(self):
        """Jump to Files panel."""
        self.query_one("#filepanel").focus()

    def action_focus_raw(self):
        """Jump to Raw IPs panel."""
        self.query_one("#rawpanel").focus()

    def action_focus_norm(self):
        """Jump to Terraform /32 panel."""
        self.query_one("#normpanel").focus()

    def action_focus_preview(self):
        """Jump to Preview panel."""
        self.query_one("#mainpreview").focus()

    def action_next_panel(self):
        """Cycle to next panel."""
        focused = self.focused
        panels = ["#filepanel", "#rawpanel", "#normpanel", "#mainpreview"]
        if focused:
            for i, panel_id in enumerate(panels):
                if focused == self.query_one(panel_id):
                    next_panel = panels[(i + 1) % len(panels)]
                    self.query_one(next_panel).focus()
                    break

    # ===== ACTION SHORTCUTS =====
    def action_process_action(self):
        """Process IPs (shortcut: p)."""
        btn = self.query_one("#procbtn", Button)
        if not btn.disabled:
            self.process_to_cidr()
        else:
            self.notify("No raw IPs to process!")

    def action_copy_action(self):
        """Copy to clipboard (shortcut: c)."""
        btn = self.query_one("#copybtn", Button)
        if not btn.disabled:
            self.copy_terraform_list()
        else:
            self.notify("No Terraform list to copy!")

    def action_save_action(self):
        """Save JSON (shortcut: s)."""
        btn = self.query_one("#jsonbtn", Button)
        if not btn.disabled:
            self.export_json()
        else:
            self.notify("No data to save!")

    def action_refresh_action(self):
        """Refresh directory (shortcut: r)."""
        self.refresh_directory()

    def action_quit(self):
        """Quit application."""
        self.exit()

    # ===== EVENT HANDLERS =====
    def on_directory_tree_file_selected(self, event):
        """Auto load on file select."""
        self.input_file = event.path
        self.query_one("#manualpath").value = str(event.path)
        self.parse_csv_safe(event.path)

    @on(Button.Pressed, "#loadbtn")
    def load_button(self):
        """Load from tree cursor."""
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
            import time

            tree_container = self.query_one("#treecontainer", Container)

            cursor_path = None
            try:
                old_tree = self.query_one("#dirtree", DirectoryTree)
                if old_tree.cursor_node and old_tree.cursor_node.data:
                    cursor_path = str(old_tree.cursor_node.data.path)
                old_tree.remove()
            except Exception:
                pass

            unique_id = f"dirtree_{int(time.time() * 1000)}"
            new_tree = DirectoryTree(str(self.input_dir), id=unique_id)
            tree_container.mount(new_tree)

            if cursor_path and Path(cursor_path).exists():
                try:
                    new_tree.cursor_path = cursor_path
                except Exception:
                    pass

            file_count = len([f for f in self.input_dir.iterdir() if f.is_file()])
            self.notify(f"Directory refreshed: {file_count} files found")
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

            self.input_file = path

            valid_extensions = {'.csv', '.tsv', '.txt', '.log'}
            if path.suffix.lower() not in valid_extensions:
                self.call_from_thread(self.notify, "Unsupported file type!")
                return

            with open(path, 'r', newline='', encoding='utf-8-sig', errors='ignore') as f:
                sample = f.read(4096)
                f.seek(0)

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
                    delimiter_found = False
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
                                                delimiter_found = True
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
                            pass

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
        """Update the raw IPs table with zebra striping."""
        self.raw_ips = ips

        table = self.query_one("#rawtbl", DataTable)
        table.clear()
        table.add_columns("IPv4 Address")
        table.zebra_stripes = True

        for ip in ips:
            table.add_row(ip)

        self.update_border_titles()
        table.focus()

        self.query_one("#procbtn").disabled = False

    @on(Button.Pressed, "#procbtn")
    def process_to_cidr(self):
        """Process raw IPs to Terraform CIDR /32 format."""
        try:
            self.norm_ips = [f'"{ip}/32"' for ip in self.raw_ips]

            table = self.query_one("#normtbl", DataTable)
            table.clear()
            table.add_columns("Terraform CIDR /32")
            table.zebra_stripes = True

            for cidr in self.norm_ips:
                table.add_row(cidr)

            self.update_border_titles()
            table.focus()

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
        except Exception as e:
            self.notify(f"Copy error: {e}")

    @on(Button.Pressed, "#jsonbtn")
    def export_json(self):
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
            self.notify(f"JSON save error: {e}")

    @on(Button.Pressed, "#quitbtn")
    def quit(self):
        self.exit()

if __name__ == "__main__":
    app = IPNormalizer()
    app.run()
