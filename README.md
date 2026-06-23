# Python Notes Portal

![Python](https://img.shields.io/badge/Python-Flask-FCC206?style=for-the-badge&logo=python&logoColor=black)
![Vercel](https://img.shields.io/badge/Deploy-Vercel-black?style=for-the-badge&logo=vercel)

A simple, clean notes portal where students can download Python notes in one click. No login required.

## 🚀 How to Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py

# 3. Open in browser
# http://localhost:5000
```

## 📁 How to Add Notes

Just drop any file into the `notes/` folder:

```
notes/
├── Python_Coding_Tasks.docx
├── Python_Basics.pdf
└── any-other-file.pptx
```

The portal auto-detects and lists all files. No code changes needed.

**Supported formats:** `.pdf`, `.docx`, `.doc`, `.pptx`, `.txt`, `.zip`

## 🌐 Deploy on Vercel

1. Push this repo to GitHub
2. Go to [vercel.com](https://vercel.com) → Import Project
3. Select your GitHub repo → Deploy

> **Note:** For Vercel, store large files (PDFs, DOCX) in the repo `notes/` folder and commit them. Vercel serves them directly.

## 📂 Project Structure

```
noteportal/
├── app.py              # Flask app
├── requirements.txt    # Dependencies
├── vercel.json         # Vercel config
├── .gitignore
├── README.md
├── notes/              # 👈 Drop your files here
│   └── Python_Coding_Tasks (1).docx
└── templates/
    └── index.html      # UI
```
