import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import multiprocessing as mp

MAX_PHOTOS = 100

LIGHT = {"bg": "#ffffff", "fg": "#000000", "box_bg": "#ffffff", "box_fg": "#000000"}
DARK = {"bg": "#1e1e1e", "fg": "#ffffff", "box_bg": "#2d2d2d", "box_fg": "#ffffff"}


def ocr_worker_process(paths, out_queue):
    """Runs in a separate OS process so it can never freeze the Tkinter window."""
    from paddleocr import PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang="en", enable_mkldnn=False)
    out_queue.put(("model_ready", None))
    for path in paths:
        try:
            result = ocr.predict(path)
            lines = result[0]["rec_texts"] if result else []
            text = "\n".join(lines)
        except Exception as e:
            text = f"[Error reading {path}: {e}]"
        out_queue.put(("result", (path, text)))
    out_queue.put(("done", None))


def pick_and_extract():
    paths = filedialog.askopenfilenames(
        title=f"Select up to {MAX_PHOTOS} photos",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp")],
    )
    if not paths:
        return
    paths = list(paths[:MAX_PHOTOS])

    select_btn.config(state=tk.DISABLED)
    text_box.delete("1.0", tk.END)
    progress["maximum"] = len(paths)
    progress["value"] = 0
    status_label.config(text="Loading OCR model (first run may take a while)...")

    queue = mp.Queue()
    process = mp.Process(target=ocr_worker_process, args=(paths, queue), daemon=True)
    process.start()

    poll_queue(queue, total=len(paths), done_count=0)


def poll_queue(queue, total, done_count):
    try:
        while True:
            kind, payload = queue.get_nowait()
            if kind == "model_ready":
                status_label.config(text=f"Processing 0/{total}...")
            elif kind == "result":
                path, text = payload
                text_box.insert(tk.END, f"--- {path} ---\n{text}\n\n")
                done_count += 1
                progress["value"] = done_count
                status_label.config(text=f"Processing {done_count}/{total}...")
            elif kind == "done":
                status_label.config(text=f"Done — extracted text from {total} photo(s).")
                select_btn.config(state=tk.NORMAL)
                return
    except Exception:
        pass  # queue empty for now, check again shortly

    root.after(100, poll_queue, queue, total, done_count)


def copy_text():
    root.clipboard_clear()
    root.clipboard_append(text_box.get("1.0", tk.END))
    messagebox.showinfo("Copied", "All extracted text copied to clipboard!")


def save_text():
    content = text_box.get("1.0", tk.END).strip()
    if not content:
        messagebox.showwarning("Nothing to save", "No extracted text yet.")
        return
    path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text file", "*.txt")],
        title="Save extracted text as",
    )
    if not path:
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    messagebox.showinfo("Saved", f"Text saved to:\n{path}")


def apply_theme(theme):
    root.configure(bg=theme["bg"])
    top_frame.configure(bg=theme["bg"])
    status_label.configure(bg=theme["bg"], fg=theme["fg"])
    text_box.configure(bg=theme["box_bg"], fg=theme["box_fg"], insertbackground=theme["fg"])


def toggle_theme():
    apply_theme(DARK if dark_mode.get() else LIGHT)


if __name__ == "__main__":
    mp.freeze_support()  # needed for Windows when packaging/multiprocessing

    root = tk.Tk()
    root.title("Photo OCR Extractor")
    root.geometry("700x650")

    dark_mode = tk.BooleanVar(value=False)

    top_frame = tk.Frame(root)
    top_frame.pack(fill=tk.X, pady=10)

    select_btn = tk.Button(top_frame, text="Select Photos & Extract Text", command=pick_and_extract)
    select_btn.pack(side=tk.LEFT, padx=10)
    tk.Checkbutton(top_frame, text="Dark Theme", variable=dark_mode, command=toggle_theme).pack(side=tk.LEFT)

    progress = ttk.Progressbar(root, mode="determinate")
    progress.pack(fill=tk.X, padx=10)

    status_label = tk.Label(root, text="No photos processed yet.", anchor="w")
    status_label.pack(fill=tk.X, padx=10, pady=5)

    text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD)
    text_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    button_row = tk.Frame(root)
    button_row.pack(pady=10)
    tk.Button(button_row, text="Copy Text", command=copy_text).pack(side=tk.LEFT, padx=5)
    tk.Button(button_row, text="Save as .txt", command=save_text).pack(side=tk.LEFT, padx=5)

    apply_theme(LIGHT)
    root.mainloop()
