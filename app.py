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
    counts[filename] = counts.get(filename, 111) + 1
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
            "downloads": counts.get(filename, 111),
            "download_url": "/dl/" + quote(filename),
            "view_url": "/view/" + quote(filename),
        })

    return notes


# ── Routes ─────────────────────────────────────────────────────

@app.route("/")
def index():
    cheatsheets_content = [
        {
            "title": "1. Variables & Basic Types",
            "code": "# Integer, Float, String, Boolean\nx = 10\ny = 3.14\nname = \"Python\"\nis_active = True\n\n# Type conversion\nstr_x = str(x)\nint_y = int(y)"
        },
        {
            "title": "2. Strings",
            "code": "text = \"Hello World\"\n\n# Slicing\ntext[0]       # 'H'\ntext[0:5]     # 'Hello'\n\n# Methods\ntext.lower()  # 'hello world'\ntext.upper()  # 'HELLO WORLD'\ntext.split()  # ['Hello', 'World']\ntext.replace(\"World\", \"Python\")"
        },
        {
            "title": "3. Lists (Mutable)",
            "code": "nums = [1, 2, 3]\n\nnums.append(4)       # [1, 2, 3, 4]\nnums.insert(0, 0)    # [0, 1, 2, 3, 4]\nnums.pop()           # Removes last item\nnums[0] = 10         # Update item\n\n# List comprehension\nsquares = [x**2 for x in nums]"
        },
        {
            "title": "4. Dictionaries",
            "code": "user = {\"name\": \"Alice\", \"age\": 25}\n\n# Access & Update\nuser[\"name\"]          # 'Alice'\nuser[\"age\"] = 26      # Update\nuser[\"city\"] = \"NY\"   # Add new key\n\n# Methods\nuser.keys()\nuser.values()\nuser.items()"
        },
        {
            "title": "5. Conditionals",
            "code": "age = 18\n\nif age < 18:\n    print(\"Minor\")\nelif age == 18:\n    print(\"Exactly 18\")\nelse:\n    print(\"Adult\")\n\n# Ternary operator\nstatus = \"Adult\" if age >= 18 else \"Minor\""
        },
        {
            "title": "6. Loops",
            "code": "# For Loop\nfor i in range(3):\n    print(i)  # 0, 1, 2\n\n# Iterating over list\nfor item in [\"a\", \"b\"]:\n    print(item)\n\n# While Loop\ncount = 0\nwhile count < 3:\n    count += 1"
        },
        {
            "title": "7. Functions",
            "code": "def greet(name, msg=\"Hello\"):\n    return f\"{msg}, {name}!\"\n\nprint(greet(\"Alice\"))\n# Output: Hello, Alice!\n\n# Lambda functions\nadd = lambda x, y: x + y\nprint(add(5, 3)) # Output: 8"
        },
        {
            "title": "8. Classes (OOP)",
            "code": "class Dog:\n    def __init__(self, name):\n        self.name = name\n        \n    def bark(self):\n        return f\"{self.name} says Woof!\"\n\nmy_dog = Dog(\"Rex\")\nprint(my_dog.bark())"
        },
        {
            "title": "9. Exception Handling",
            "code": "try:\n    result = 10 / 0\nexcept ZeroDivisionError:\n    print(\"Cannot divide by zero!\")\nexcept Exception as e:\n    print(f\"Error: {e}\")\nfinally:\n    print(\"Cleanup code here\")"
        },
        {
            "title": "10. File Handling",
            "code": "# Writing to a file\nwith open(\"data.txt\", \"w\") as f:\n    f.write(\"Hello Python\")\n\n# Reading from a file\nwith open(\"data.txt\", \"r\") as f:\n    content = f.read()\n    print(content)"
        },
        {
            "title": "11. Tuples (Immutable)",
            "code": "coords = (10, 20)\n\n# Accessing elements\nx = coords[0]\n\n# Unpacking\nx, y = coords\n\n# Note: coords[0] = 15 will throw an error!"
        },
        {
            "title": "12. Sets (Unique)",
            "code": "nums = {1, 2, 2, 3}\nprint(nums)  # Output: {1, 2, 3}\n\n# Adding/Removing\nnums.add(4)\nnums.remove(1)\n\n# Set operations\na = {1, 2}\nb = {2, 3}\na | b  # Union: {1, 2, 3}\na & b  # Intersection: {2}"
        },
        {
            "title": "13. Modules & Imports",
            "code": "# Import entire module\nimport math\nprint(math.pi)\n\n# Import specific functions\nfrom datetime import datetime\nprint(datetime.now())\n\n# Alias\nimport numpy as np"
        },
        {
            "title": "14. *args & **kwargs",
            "code": "def my_func(*args, **kwargs):\n    for arg in args:\n        print(\"Positional:\", arg)\n    for k, v in kwargs.items():\n        print(f\"Keyword: {k}={v}\")\n\nmy_func(1, 2, name=\"Alice\", age=25)"
        }
    ]
    return render_template("index.html", notes=get_notes(), cheatsheets_content=cheatsheets_content)


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


@app.route("/view/<path:filename>")
def view(filename):
    """Serve the file inline for viewing."""
    safe_name = os.path.basename(filename)
    file_path  = os.path.join(NOTES_FOLDER, safe_name)

    if not os.path.isfile(file_path):
        abort(404)

    ext = os.path.splitext(safe_name)[1].lower()
    if ext in [".docx", ".doc"]:
        return render_template("view_docx.html", filename=safe_name, file_url="/dl/" + quote(safe_name))

    return send_from_directory(NOTES_FOLDER, safe_name, as_attachment=False)


@app.route("/exam")
def exam_portal():
    mcqs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "mcqs.json")
    try:
        with open(mcqs_path, "r", encoding="utf-8") as f:
            mcqs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        mcqs = []
    return render_template("exam.html", questions=mcqs)


if __name__ == "__main__":
    os.makedirs(NOTES_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)
