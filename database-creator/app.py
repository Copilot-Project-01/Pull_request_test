"""A simple web app for creating and managing SQLite databases."""

import os
import re
import sqlite3

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32).hex())

DATABASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databases")
os.makedirs(DATABASE_DIR, exist_ok=True)

# Strict allowlist for database names: letters, digits, hyphens, underscores only
DB_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
MAX_DB_NAME_LENGTH = 64


def _validate_db_name(name: str) -> str | None:
    """Return an error message if the name is invalid, or None if valid."""
    if not name or not name.strip():
        return "Database name cannot be empty."
    name = name.strip()
    if len(name) > MAX_DB_NAME_LENGTH:
        return f"Database name must be at most {MAX_DB_NAME_LENGTH} characters."
    if not DB_NAME_PATTERN.match(name):
        return "Database name may only contain letters, digits, hyphens, and underscores."
    return None


def _safe_db_path(name: str) -> str:
    """Return the full file path for a database, ensuring it stays inside DATABASE_DIR.

    The name must pass _validate_db_name() before calling this function.
    An additional realpath check prevents path traversal.
    """
    # Build the candidate path using only the basename
    candidate = os.path.join(DATABASE_DIR, f"{name}.db")
    # Resolve to an absolute, symlink-free path and verify it is inside DATABASE_DIR
    resolved = os.path.realpath(candidate)
    real_db_dir = os.path.realpath(DATABASE_DIR)
    if not resolved.startswith(real_db_dir + os.sep) and resolved != real_db_dir:
        raise ValueError("Invalid database path")
    return resolved


def _quote_identifier(name: str) -> str:
    """Safely quote a SQL identifier by doubling any embedded double quotes.

    The name must already be validated against DB_NAME_PATTERN (which disallows
    double quotes), but this provides defense-in-depth.
    """
    escaped = name.replace('"', '""')
    return f'"{escaped}"'


def _list_databases() -> list[dict]:
    """List all databases in the storage directory."""
    databases = []
    if not os.path.isdir(DATABASE_DIR):
        return databases
    for filename in sorted(os.listdir(DATABASE_DIR)):
        if filename.endswith(".db"):
            filepath = os.path.join(DATABASE_DIR, filename)
            name = filename[:-3]
            size_bytes = os.path.getsize(filepath)
            # Get table count
            try:
                conn = sqlite3.connect(filepath)
                cursor = conn.execute(
                    "SELECT count(*) FROM sqlite_master WHERE type='table'"
                )
                table_count = cursor.fetchone()[0]
                conn.close()
            except sqlite3.Error:
                table_count = 0
            databases.append(
                {
                    "name": name,
                    "filename": filename,
                    "size_kb": round(size_bytes / 1024, 2),
                    "table_count": table_count,
                }
            )
    return databases


@app.route("/")
def index():
    """Home page showing all databases."""
    databases = _list_databases()
    return render_template("index.html", databases=databases)


@app.route("/create", methods=["POST"])
def create_database():
    """Create a new SQLite database."""
    db_name = request.form.get("db_name", "").strip()

    error = _validate_db_name(db_name)
    if error:
        flash(error, "error")
        return redirect(url_for("index"))

    db_path = _safe_db_path(db_name)
    if os.path.exists(db_path):
        flash(f"Database '{db_name}' already exists.", "error")
        return redirect(url_for("index"))

    try:
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS _metadata (key TEXT, value TEXT)")
        conn.execute(
            "INSERT INTO _metadata (key, value) VALUES (?, ?)",
            ("created_by", "database-creator-app"),
        )
        conn.commit()
        conn.close()
        flash(f"Database '{db_name}' created successfully!", "success")
    except sqlite3.Error as e:
        flash(f"Error creating database: {e}", "error")

    return redirect(url_for("index"))


@app.route("/delete/<db_name>", methods=["POST"])
def delete_database(db_name: str):
    """Delete an existing database."""
    error = _validate_db_name(db_name)
    if error:
        flash(error, "error")
        return redirect(url_for("index"))

    db_path = _safe_db_path(db_name)
    if not os.path.exists(db_path):
        flash(f"Database '{db_name}' not found.", "error")
        return redirect(url_for("index"))

    try:
        os.remove(db_path)
        flash(f"Database '{db_name}' deleted.", "success")
    except OSError as e:
        flash(f"Error deleting database: {e}", "error")

    return redirect(url_for("index"))


@app.route("/view/<db_name>")
def view_database(db_name: str):
    """View tables inside a database."""
    error = _validate_db_name(db_name)
    if error:
        flash(error, "error")
        return redirect(url_for("index"))

    db_path = _safe_db_path(db_name)
    if not os.path.exists(db_path):
        flash(f"Database '{db_name}' not found.", "error")
        return redirect(url_for("index"))

    tables = []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        for row in cursor.fetchall():
            table_name = row[0]
            count_cursor = conn.execute(
                f"SELECT count(*) FROM {_quote_identifier(table_name)}"  # noqa: S608
            )
            row_count = count_cursor.fetchone()[0]
            tables.append({"name": table_name, "row_count": row_count})
        conn.close()
    except sqlite3.Error as e:
        flash(f"Error reading database: {e}", "error")
        return redirect(url_for("index"))

    return render_template("view.html", db_name=db_name, tables=tables)


@app.route("/create-table/<db_name>", methods=["POST"])
def create_table(db_name: str):
    """Create a new table in an existing database."""
    error = _validate_db_name(db_name)
    if error:
        flash(error, "error")
        return redirect(url_for("index"))

    db_path = _safe_db_path(db_name)
    if not os.path.exists(db_path):
        flash(f"Database '{db_name}' not found.", "error")
        return redirect(url_for("index"))

    table_name = request.form.get("table_name", "").strip()
    columns_raw = request.form.get("columns", "").strip()

    if not table_name or not DB_NAME_PATTERN.match(table_name):
        flash(
            "Table name may only contain letters, digits, hyphens, and underscores.",
            "error",
        )
        return redirect(url_for("view_database", db_name=db_name))

    if not columns_raw:
        flash("Please provide at least one column definition.", "error")
        return redirect(url_for("view_database", db_name=db_name))

    # Parse columns: "name TEXT, age INTEGER, ..."
    # Validate each column definition
    allowed_types = {"TEXT", "INTEGER", "REAL", "BLOB", "NUMERIC"}
    column_defs = []
    for col_def in columns_raw.split(","):
        parts = col_def.strip().split()
        if len(parts) != 2:
            flash(
                f"Invalid column definition: '{col_def.strip()}'. "
                "Use format: column_name TYPE",
                "error",
            )
            return redirect(url_for("view_database", db_name=db_name))
        col_name, col_type = parts
        if not DB_NAME_PATTERN.match(col_name):
            flash(f"Invalid column name: '{col_name}'.", "error")
            return redirect(url_for("view_database", db_name=db_name))
        if col_type.upper() not in allowed_types:
            flash(
                f"Invalid column type: '{col_type}'. "
                f"Allowed types: {', '.join(sorted(allowed_types))}",
                "error",
            )
            return redirect(url_for("view_database", db_name=db_name))
        column_defs.append(f"{_quote_identifier(col_name)} {col_type.upper()}")

    try:
        conn = sqlite3.connect(db_path)
        columns_sql = ", ".join(column_defs)
        safe_table = _quote_identifier(table_name)
        conn.execute(f"CREATE TABLE {safe_table} ({columns_sql})")  # noqa: S608
        conn.commit()
        conn.close()
        flash(f"Table '{table_name}' created in '{db_name}'.", "success")
    except sqlite3.Error as e:
        flash(f"Error creating table: {e}", "error")

    return redirect(url_for("view_database", db_name=db_name))


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true", port=5000)
