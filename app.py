from flask import Flask, render_template, send_from_directory, abort
from urllib.parse import quote
import os
import json

app = Flask(__name__)

NOTES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "notes")

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".pptx", ".txt", ".zip"}

# On Vercel the filesystem is read-only except /tmp.
# Locally we use data/counts.json so counts survive restarts.
IS_VERCEL = os.environ.get("VERCEL") == "1"
COUNTS_FILE = (
    "/tmp/counts.json"
    if IS_VERCEL
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "counts.json")
)


# ── Count helpers ──────────────────────────────────────────────

def load_counts() -> dict:
    """Load download counts from disk."""
    try:
        with open(COUNTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_counts(counts: dict) -> None:
    """Persist download counts to disk."""
    os.makedirs(os.path.dirname(COUNTS_FILE), exist_ok=True)
    with open(COUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(counts, f)


def increment_count(filename: str) -> int:
    """Increment the download count for a file and return the new value."""
    counts = load_counts()
    counts[filename] = counts.get(filename, 0) + 1
    save_counts(counts)
    return counts[filename]


# ── Note listing ───────────────────────────────────────────────

def get_notes():
    """Scan static/notes/ and return metadata for every allowed file."""
    notes = []
    counts = load_counts()

    if not os.path.exists(NOTES_FOLDER):
        return notes

    for filename in sorted(os.listdir(NOTES_FOLDER)):
        name, ext = os.path.splitext(filename)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            continue

        filepath = os.path.join(NOTES_FOLDER, filename)
        size_bytes = os.path.getsize(filepath)
        size_str = (
            f"{size_bytes / 1024:.0f} KB"
            if size_bytes < 1024 * 1024
            else f"{size_bytes / (1024 * 1024):.1f} MB"
        )

        icon_map = {
            ".pdf":  "fa-file-pdf",
            ".docx": "fa-file-word",
            ".doc":  "fa-file-word",
            ".pptx": "fa-file-powerpoint",
            ".txt":  "fa-file-lines",
            ".zip":  "fa-file-zipper",
        }

        notes.append({
            "filename": filename,
            "title":    name.replace("_", " ").replace("-", " "),
            "ext":      ext.upper().lstrip("."),
            "size":     size_str,
            "icon":     icon_map.get(ext.lower(), "fa-file"),
            "downloads": counts.get(filename, 0),
            "download_url": "/dl/" + quote(filename),
        })

    return notes


# ── Routes ─────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", notes=get_notes())


@app.route("/dl/<path:filename>")
def download(filename):
    """Track the download, then serve the file."""
    safe_name = os.path.basename(filename)
    file_path  = os.path.join(NOTES_FOLDER, safe_name)

    if not os.path.isfile(file_path):
        abort(404)

    # Increment counter BEFORE sending the file
    increment_count(safe_name)

    return send_from_directory(NOTES_FOLDER, safe_name, as_attachment=True)


if __name__ == "__main__":
    os.makedirs(NOTES_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)
