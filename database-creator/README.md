# Database Creator

A simple web app for creating and managing SQLite databases from your browser.

## Features

- **Create databases** — Spin up new SQLite databases with one click
- **View databases** — Browse tables and row counts
- **Create tables** — Define columns with supported SQLite types (TEXT, INTEGER, REAL, BLOB, NUMERIC)
- **Delete databases** — Remove databases you no longer need

## Quick Start

```bash
cd database-creator
pip install -r requirements.txt
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

## Project Structure

```
database-creator/
├── app.py               # Flask application
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── databases/           # Created databases stored here (auto-created)
├── static/
│   └── style.css        # Stylesheet
└── templates/
    ├── index.html       # Home page (list & create databases)
    └── view.html        # Database detail page (list & create tables)
```

## Tech Stack

- **Backend:** Python / Flask
- **Database Engine:** SQLite
- **Frontend:** HTML, CSS (no JavaScript frameworks)
