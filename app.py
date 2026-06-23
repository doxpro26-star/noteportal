from flask import Flask, render_template, send_from_directory, abort
import os

app = Flask(__name__)

NOTES_FOLDER = os.path.join(os.path.dirname(__file__), "notes")

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".pptx", ".txt", ".zip"}

def get_notes():
    """Scan the notes/ folder and return a list of files."""
    notes = []
    if not os.path.exists(NOTES_FOLDER):
        return notes

    for filename in sorted(os.listdir(NOTES_FOLDER)):
        name, ext = os.path.splitext(filename)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            continue

        filepath = os.path.join(NOTES_FOLDER, filename)
        size_bytes = os.path.getsize(filepath)
        size_str = f"{size_bytes / 1024:.0f} KB" if size_bytes < 1024 * 1024 else f"{size_bytes / (1024*1024):.1f} MB"

        # Pick an icon based on extension
        icon_map = {
            ".pdf":  "fa-file-pdf",
            ".docx": "fa-file-word",
            ".doc":  "fa-file-word",
            ".pptx": "fa-file-powerpoint",
            ".txt":  "fa-file-lines",
            ".zip":  "fa-file-zipper",
        }
        icon = icon_map.get(ext.lower(), "fa-file")

        notes.append({
            "filename": filename,
            "title": name.replace("_", " ").replace("-", " "),
            "ext": ext.upper().lstrip("."),
            "size": size_str,
            "icon": icon,
        })

    return notes


@app.route("/")
def index():
    notes = get_notes()
    return render_template("index.html", notes=notes)


@app.route("/download/<filename>")
def download(filename):
    """Serve a file from the notes/ folder as a download."""
    # Basic security: strip any path separators
    safe_name = os.path.basename(filename)
    filepath = os.path.join(NOTES_FOLDER, safe_name)
    if not os.path.exists(filepath):
        abort(404)
    return send_from_directory(NOTES_FOLDER, safe_name, as_attachment=True)


if __name__ == "__main__":
    os.makedirs(NOTES_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)
