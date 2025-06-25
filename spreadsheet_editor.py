#spreadsheet_editor
#Created on 24/6/2025 by Zixin Zhang
#The source code of this project is available on GitHub @SilverShadowed



import tkinter as tk
from tkinter import filedialog
import pandas as pd
import locale

class SpreadsheetEditor:
    def __init__(self, root):
        self.root = root
        self.lang = self.detect_language()
        self.texts = self.get_texts()
        self.root.title(self.texts["title"])

        self.symbol_toggle = tk.StringVar(value='⬤')
        self.mode_toggle = tk.StringVar(value=self.texts["mode_add"])
        self.df = None
        self.filepath = None
        self.button_refs = {}

        self.create_widgets()
        self.root.bind("<Configure>", self.on_resize)

    def detect_language(self):
        lang_code = locale.getdefaultlocale()[0]
        if lang_code and lang_code.startswith("zh"):
            return "zh"
        return "en"

    def get_texts(self):
        return {
            "title": "CSV 星星/圆圈编辑器" if self.lang == "zh" else "CSV Star/Circle Editor",
            "import_csv": "导入CSV" if self.lang == "zh" else "Load CSV",
            "pattern": "图案:" if self.lang == "zh" else "Symbol:",
            "mode": "模式:" if self.lang == "zh" else "Mode:",
            "mode_add": "添加" if self.lang == "zh" else "Add",
            "mode_delete": "删除" if self.lang == "zh" else "Delete",
            "file_prompt": "选择CSV文件" if self.lang == "zh" else "Select CSV File",
        }

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, pady=5)

        tk.Button(top_frame, text=self.texts["import_csv"], command=self.load_csv).pack(side=tk.LEFT, padx=5)
        tk.Label(top_frame, text=self.texts["pattern"]).pack(side=tk.LEFT)
        tk.Button(top_frame, textvariable=self.symbol_toggle, width=3, command=self.toggle_symbol).pack(side=tk.LEFT, padx=5)
        tk.Label(top_frame, text=self.texts["mode"]).pack(side=tk.LEFT)
        tk.Button(top_frame, textvariable=self.mode_toggle, command=self.toggle_mode).pack(side=tk.LEFT, padx=5)

        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(expand=True, fill=tk.BOTH)
        # Footer label
        footer = tk.Label(self.root, text="Made in June 2025", fg="grey", font=("Arial", 8))
        footer.pack(side=tk.BOTTOM, pady=2)


    def load_csv(self):
        filepath = filedialog.askopenfilename(title=self.texts["file_prompt"], filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return
        self.filepath = filepath
        self.df = pd.read_csv(self.filepath, header=None, dtype=str)
        self.df.fillna("", inplace=True)
        self.render_table()

    def toggle_symbol(self):
        self.symbol_toggle.set('★' if self.symbol_toggle.get() == '⬤' else '⬤')

    def toggle_mode(self):
        current = self.mode_toggle.get()
        if current == self.texts["mode_add"]:
            self.mode_toggle.set(self.texts["mode_delete"])
        else:
            self.mode_toggle.set(self.texts["mode_add"])

    def render_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.button_refs.clear()

        if self.df is None:
            return

        rows, cols = self.df.shape
        for r in range(rows):
            self.table_frame.grid_rowconfigure(r, weight=1)
            for c in range(cols):
                self.table_frame.grid_columnconfigure(c, weight=1)
                cell_value = self.df.iat[r, c]

                is_row_header = r == 0
                is_col_header = c == 0

                if is_row_header:
                    bg_color = '#A9A9A9'
                elif is_col_header:
                    bg_color = 'lightgrey'
                else:
                    bg_color = 'white'

                common_cell_style = {
                    "relief": "flat",
                    "bd": 1,
                    "highlightthickness": 0,
                    "activebackground": bg_color,
                    "bg": bg_color,
                    "wraplength": 1
                }

                if is_row_header or is_col_header:
                    btn = tk.Button(self.table_frame, text=cell_value, state="disabled",
                                    disabledforeground="black", **common_cell_style)
                else:
                    btn = tk.Button(self.table_frame, text=cell_value,
                                    command=lambda r=r, c=c: self.on_cell_click(r, c),
                                    **common_cell_style)

                btn.grid(row=r, column=c, sticky="nsew")
                self.button_refs[(r, c)] = btn

        self.on_resize()

    def on_cell_click(self, row, col):
        if row == 0 or col == 0 or self.df is None:
            return

        current_value = self.df.iat[row, col]
        mode = self.mode_toggle.get()
        symbol = self.symbol_toggle.get()

        if mode == self.texts["mode_add"] and current_value == "":
            self.df.iat[row, col] = symbol
        elif mode == self.texts["mode_delete"] and current_value in ['⬤', '★']:
            self.df.iat[row, col] = ""
        else:
            return

        self.save_and_refresh()

    def save_and_refresh(self):
        self.df.to_csv(self.filepath, index=False, header=False)
        self.render_table()

    def on_resize(self, event=None):
        if not self.button_refs or self.df is None:
            return

        rows, cols = self.df.shape
        total_width = self.table_frame.winfo_width()
        total_height = self.table_frame.winfo_height()

        cell_width = total_width // cols if cols > 0 else 100
        cell_height = total_height // rows if rows > 0 else 30

        for (r, c), btn in self.button_refs.items():
            font_size = max(min(cell_height, cell_width) // 3, 8)
            btn.config(font=("Arial", font_size))
            btn.config(wraplength=cell_width - 10)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = SpreadsheetEditor(root)
    root.mainloop()
