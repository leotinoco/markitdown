import os
import sys
import threading
import queue
from pathlib import Path
from typing import List
from datetime import datetime

import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

# Import MarkItDown
try:
    from markitdown import MarkItDown
except ImportError:
    # If not installed, try to add the source to path (for development)
    sys.path.append(str(Path(__file__).parent.parent / "markitdown" / "src"))
    from markitdown import MarkItDown

class RedirectText(object):
    def __init__(self, queue_obj, tag="stdout"):
        self.queue = queue_obj
        self.tag = tag

    def write(self, string):
        if string.strip():
            self.queue.put(("log_raw", string + "\n"))

    def flush(self):
        pass

# Supported extensions grouped for filters
SUPPORTED_EXTENSIONS = [
    ("Documentos", "*.pdf *.docx *.pptx *.epub *.msg"),
    ("Hojas de Cálculo", "*.xlsx *.xls *.csv"),
    ("Imágenes", "*.jpg *.jpeg *.png"),
    ("Audio/Video", "*.wav *.mp3 *.m4a *.mp4"),
    ("Web/Datos", "*.html *.htm *.json *.jsonl *.xml *.rss *.atom"),
    ("Texto/Código", "*.txt *.text *.md *.markdown *.ipynb"),
    ("Archivos", "*.zip"),
    ("Todos los soportados", "*.pdf *.docx *.pptx *.epub *.msg *.xlsx *.xls *.csv *.jpg *.jpeg *.png *.wav *.mp3 *.m4a *.mp4 *.html *.htm *.json *.jsonl *.xml *.rss *.atom *.txt *.text *.md *.markdown *.ipynb *.zip"),
    ("Todos los archivos", "*.*")
]

class MarkItDownGUI(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("MarkItDown GUI — Conversor Universal a Markdown")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize MarkItDown
        self.md = MarkItDown()
        
        # State
        self.selected_files = []
        self.is_converting = False
        self.queue = queue.Queue()

        # Redirect standard output
        sys.stdout = RedirectText(self.queue, "stdout")
        sys.stderr = RedirectText(self.queue, "stderr")

        # UI Layout
        self.setup_ui()
        
        # Check queue for updates
        self.after(100, self.process_queue)
        self.log_msg("Aplicación iniciada correctamente.")

    def log_msg(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.queue.put(("log", f"[{timestamp}] {msg}\n"))

    def setup_ui(self):
        # Configure Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, height=80)
        self.header_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.header_frame.grid_propagate(False)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="MarkItDown GUI", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(side="left", padx=20, pady=20)

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame, 
            text="Convierte cualquier archivo a Markdown de forma masiva", 
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.subtitle_label.pack(side="left", padx=0, pady=25)

        # --- Main Content ---
        self.main_content = ctk.CTkFrame(self)
        self.main_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)

        # - Toolbar -
        self.toolbar = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.add_btn = ctk.CTkButton(
            self.toolbar, 
            text="📂 Seleccionar Archivos", 
            command=self.browse_files,
            width=200,
            height=40,
            font=ctk.CTkFont(weight="bold")
        )
        self.add_btn.pack(side="left", padx=5)

        self.clear_btn = ctk.CTkButton(
            self.toolbar, 
            text="🗑️ Limpiar Todo", 
            command=self.clear_list,
            fg_color="#333333",
            hover_color="#444444",
            width=120,
            height=40
        )
        self.clear_btn.pack(side="left", padx=5)

        self.overwrite_var = ctk.BooleanVar(value=True)
        self.overwrite_check = ctk.CTkCheckBox(
            self.toolbar, 
            text="Sobrescribir archivos si existen", 
            variable=self.overwrite_var
        )
        self.overwrite_check.pack(side="right", padx=10)

        # - File List Area -
        self.list_frame = ctk.CTkFrame(self.main_content)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Use a standard Treeview for better column mapping, but style it to fit
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2a2d2e", 
                        foreground="white", 
                        fieldbackground="#2a2d2e", 
                        borderwidth=0)
        style.map("Treeview", background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#333333", foreground="white", borderwidth=0)

        self.tree = ttk.Treeview(
            self.list_frame, 
            columns=("name", "type", "size", "status"), 
            show="headings",
            selectmode="extended"
        )
        
        self.tree.heading("name", text="Nombre del Archivo")
        self.tree.heading("type", text="Tipo")
        self.tree.heading("size", text="Tamaño")
        self.tree.heading("status", text="Estado")
        
        self.tree.column("name", width=400)
        self.tree.column("type", width=80, anchor="center")
        self.tree.column("size", width=100, anchor="center")
        self.tree.column("status", width=150, anchor="center")
        
        self.tree.pack(side="left", fill="both", expand=True)

        self.scrollbar = ctk.CTkScrollbar(self.list_frame, command=self.tree.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Drag & Drop registration
        self.tree.drop_target_register(DND_FILES)
        self.tree.dnd_bind('<<Drop>>', self.handle_drop)

        # Hint text
        self.hint_label = ctk.CTkLabel(
            self.main_content, 
            text="💡 Tip: Puedes arrastrar y soltar archivos aquí.", 
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray"
        )
        self.hint_label.grid(row=2, column=0, sticky="w", padx=15, pady=2)

        # --- Bottom Panel ---
        self.bottom_panel = ctk.CTkFrame(self, corner_radius=0)
        self.bottom_panel.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        self.bottom_panel.grid_columnconfigure(0, weight=1)
        
        # Log Box Area
        self.log_textbox = ctk.CTkTextbox(self.bottom_panel, height=100, state="disabled", font=ctk.CTkFont(family="Consolas", size=12))
        self.log_textbox.grid(row=0, column=0, sticky="ew", padx=30, pady=(10, 0))
        
        self.progress_frame = ctk.CTkFrame(self.bottom_panel, fg_color="transparent")
        self.progress_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=10)
        
        self.status_label = ctk.CTkLabel(self.progress_frame, text="Listo.")
        self.status_label.pack(side="left")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(side="right", fill="x", expand=True, padx=(20, 0))
        self.progress_bar.set(0)

        self.action_frame = ctk.CTkFrame(self.bottom_panel, fg_color="transparent")
        self.action_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 20))
        
        self.convert_btn = ctk.CTkButton(
            self.action_frame, 
            text="🚀 Iniciar Conversión", 
            command=self.start_conversion,
            height=50,
            width=250,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.convert_btn.pack(side="right")
        
        self.open_folder_btn = ctk.CTkButton(
            self.action_frame, 
            text="📁 Abrir Carpeta de Resultados", 
            command=self.open_last_folder,
            fg_color="#333333",
            hover_color="#444444",
            height=50,
            state="disabled"
        )
        self.open_folder_btn.pack(side="left")

        # Context Menu
        self.context_menu = ctk.CTkScrollableFrame(self, width=150, height=80) 
        # (Implementing a real context menu is easier with standard tkinter Menu)
        self.menu = os_menu = ctk.CTkOptionMenu(self, values=["Eliminar", "Abrir Carpeta"]) # No, let's use standard Menu
        from tkinter import Menu
        self.right_click_menu = Menu(self, tearoff=0)
        self.right_click_menu.add_command(label="Eliminar de la lista", command=self.remove_selected)
        self.right_click_menu.add_command(label="Abrir ubicación", command=self.open_selected_location)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.right_click_menu.post(event.x_root, event.y_root)

    def remove_selected(self):
        selected_items = self.tree.selection()
        for item in selected_items:
            path = self.tree.item(item, "values")[4] if len(self.tree.item(item, "values")) > 4 else None
            if path in self.selected_files:
                self.selected_files.remove(path)
            self.tree.delete(item)
        self.update_list_state()

    def open_selected_location(self):
        selected_items = self.tree.selection()
        if selected_items:
            path = self.tree.item(selected_items[0], "values")[4]
            folder = os.path.dirname(path)
            os.startfile(folder)

    def handle_drop(self, event):
        files = self.split_dnd_files(event.data)
        self.add_files(files)

    def split_dnd_files(self, data):
        # Handle Windows explorer drop format (brace quoted paths)
        import re
        if '{' in data:
            return re.findall(r'\{(.*?)\}', data)
        return data.split()

    def browse_files(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos para convertir",
            filetypes=SUPPORTED_EXTENSIONS
        )
        if files:
            self.add_files(files)

    def add_files(self, files):
        for file in files:
            if file not in self.selected_files:
                path = Path(file)
                if path.is_file():
                    size_kb = f"{path.stat().st_size / 1024:.1f} KB"
                    # We store the full path in a hidden column or attached to the item ID
                    self.tree.insert("", "end", values=(path.name, path.suffix.upper(), size_kb, "⏳ Pendiente", str(path)))
                    self.selected_files.append(str(path))
        self.update_list_state()

    def update_list_state(self):
        count = len(self.selected_files)
        if count > 0:
            self.status_label.configure(text=f"{count} archivos seleccionados.")
            self.convert_btn.configure(state="normal")
        else:
            self.status_label.configure(text="Listo.")
            self.convert_btn.configure(state="disabled")

    def clear_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.selected_files = []
        self.update_list_state()
        self.progress_bar.set(0)
        self.open_folder_btn.configure(state="disabled")
        
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        self.log_msg("Lista limpiada.")

    def start_conversion(self):
        if not self.selected_files or self.is_converting:
            return
        
        self.is_converting = True
        self.convert_btn.configure(state="disabled", text="⌛ Procesando...")
        self.add_btn.configure(state="disabled")
        self.clear_btn.configure(state="disabled")
        
        # Start work in thread
        threading.Thread(target=self.conversion_worker, daemon=True).start()

    def conversion_worker(self):
        total = len(self.selected_files)
        items = self.tree.get_children()
        
        for i, item_id in enumerate(items):
            file_path = self.tree.item(item_id, "values")[4]
            name = self.tree.item(item_id, "values")[0]
            size_str = self.tree.item(item_id, "values")[2]
            
            self.queue.put(("status", item_id, "🔄 Convirtiendo..."))
            self.queue.put(("progress", (i) / total))
            
            self.log_msg(f"Procesando ({i+1}/{total}): {name} ({size_str})")
            
            # Additional hint for large files
            size_mb = Path(file_path).stat().st_size / (1024 * 1024)
            if file_path.lower().endswith('.pdf') and size_mb > 5:
                self.log_msg(f"    ⏳ Nota: Archivo PDF grande ({size_mb:.1f} MB). Esto puede tardar varios minutos y requerir mucha CPU/memoria.")
            
            try:
                # Actual conversion logic
                result = self.md.convert(file_path)
                
                output_path = Path(file_path).with_suffix(".md")
                
                # Check overwrite
                if output_path.exists() and not self.overwrite_var.get():
                    counter = 1
                    while output_path.exists():
                        output_path = Path(file_path).parent / f"{Path(file_path).stem}_{counter}.md"
                        counter += 1
                
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result.text_content)
                
                self.queue.put(("status", item_id, "✅ Completado"))
                self.log_msg(f"✅ Completado: {output_path.name}")
            except Exception as e:
                self.queue.put(("status", item_id, f"❌ Error: {str(e)[:50]}..."))
                self.log_msg(f"❌ Error en {name}: {str(e)}")
        
        self.queue.put(("progress", 1.0))
        self.queue.put(("done", None))

    def process_queue(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                msg_type = msg[0]
                
                if msg_type == "status":
                    self.tree.set(msg[1], column="status", value=msg[2])
                elif msg_type == "progress":
                    self.progress_bar.set(msg[1])
                    self.status_label.configure(text=f"Procesando: {int(msg[1]*100)}%")
                elif msg_type == "log":
                    self.log_textbox.configure(state="normal")
                    self.log_textbox.insert("end", msg[1])
                    self.log_textbox.see("end")
                    self.log_textbox.configure(state="disabled")
                elif msg_type == "log_raw":
                    # For intercepted stdout/stderr
                    self.log_textbox.configure(state="normal")
                    self.log_textbox.insert("end", "> " + msg[1])
                    self.log_textbox.see("end")
                    self.log_textbox.configure(state="disabled")
                elif msg_type == "done":
                    self.is_converting = False
                    self.convert_btn.configure(state="normal", text="🚀 Iniciar Conversión")
                    self.add_btn.configure(state="normal")
                    self.clear_btn.configure(state="normal")
                    self.status_label.configure(text="Conversión terminada.")
                    self.open_folder_btn.configure(state="normal")
                    self.log_msg("Conversión total terminada.")
                    
                    # messagebox.showinfo("Completado", "La conversión de archivos ha finalizado.")
        except queue.Empty:
            pass
        self.after(100, self.process_queue)

    def open_last_folder(self):
        if self.selected_files:
            folder = os.path.dirname(self.selected_files[0])
            os.startfile(folder)

if __name__ == "__main__":
    app = MarkItDownGUI()
    app.mainloop()
