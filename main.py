# main.py
import json
import os
import re
from datetime import datetime

import markdown
import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    current_app,
    jsonify,
    render_template,
    request,
)

load_dotenv()
app = Flask(__name__)

PROJECTS_DIR = "pages"


def load_project_data(filename):
    filepath = os.path.join(PROJECTS_DIR, filename)
    if not os.path.exists(filepath):
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split front-matter and content
    match = re.match(r"---\s*(.*?)\s*---\s*(.*)", content, re.DOTALL)
    if not match:
        return {
            "title": os.path.splitext(filename)[0].replace("-", " ").title(),
            "content": markdown.markdown(content),
        }

    front_matter_str, md_content = match.groups()
    metadata = {}
    for line in front_matter_str.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"')

    project_data = {
        "id": os.path.splitext(filename)[0],
        "title": metadata.get(
            "title", os.path.splitext(filename)[0].replace("-", " ").title()
        ),
        "short_description": metadata.get("short_description", ""),
        "image": metadata.get("image", ""),
        "tags": [tag.strip() for tag in metadata.get("tags", "").split(",")]
        if metadata.get("tags")
        else [],
        "content": markdown.markdown(md_content),
    }
    return project_data


def get_all_projects():
    projects = []
    if os.path.exists(PROJECTS_DIR):
        for filename in os.listdir(PROJECTS_DIR):
            if filename.endswith(".md"):
                project = load_project_data(filename)
                if project:
                    projects.append(project)
    # Sort projects by title lowercase
    projects.sort(key=lambda x: x.get("title", "").lower())
    return projects


@app.route("/")
def index():
    projects = get_all_projects()
    return render_template("index.html", projects=projects)


@app.route("/project/<project_id>")
def project_detail(project_id):
    project = load_project_data(f"{project_id}.md")
    if project is None:
        return render_template("404.html"), 404
    return render_template("project_detail.html", project=project)


# Contact page (GET)
@app.route("/contact")
def contact_page():
    return render_template("contact.html")


# --- Helper: Save contact entry (abstracted so you can swap storage later) ---
def save_contact_entry(entry):
    """
    Try Supabase first (if configured), then fallback to local file.
    Returns list of places where saved, e.g. ["supabase"] or ["file"].
    """
    saved = []

    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if supabase_url and supabase_key:
        try:
            url = f"{supabase_url.rstrip('/')}/rest/v1/contacts"
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            }
            # Supabase REST accepts object as JSON
            resp = requests.post(
                url, headers=headers, data=json.dumps(entry), timeout=8
            )
            if resp.ok:
                saved.append("supabase")
            else:
                current_app.logger.warning(
                    "Supabase insert failed: %s %s", resp.status_code, resp.text
                )
        except Exception as e:
            current_app.logger.warning("Supabase request error: %s", e)

    # fallback to file storage
    if not saved:
        try:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
            os.makedirs(data_dir, exist_ok=True)
            contacts_file = os.path.join(data_dir, "contacts.json")
            if os.path.exists(contacts_file):
                with open(contacts_file, "r", encoding="utf-8") as f:
                    try:
                        contacts = json.load(f)
                        if not isinstance(contacts, list):
                            contacts = []
                    except Exception:
                        contacts = []
            else:
                contacts = []
            contacts.append(entry)
            with open(contacts_file, "w", encoding="utf-8") as f:
                json.dump(contacts, f, ensure_ascii=False, indent=2)
            saved.append("file")
        except Exception as e:
            current_app.logger.error("Failed to save contact to file: %s", e)
            # If both fail, raise to caller
            raise

    return saved


# Contact form submit (POST)
@app.route("/submit_contact", methods=["POST"])
def submit_contact():
    # Accept JSON or form-encoded POSTs
    data = {}
    if request.is_json:
        data = request.get_json()
    else:
        data["name"] = request.form.get("name", "").strip()
        data["email"] = request.form.get("email", "").strip()
        data["message"] = request.form.get("message", "").strip()

    name = data.get("name", "")
    email = data.get("email", "")
    message = data.get("message", "")

    # Basic validation
    if not name or not email or not message:
        return jsonify(
            {"ok": False, "error": "Please provide name, email and message."}
        ), 400
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify(
            {"ok": False, "error": "Please provide a valid email address."}
        ), 400
        data["message"] = request.form.get("message", "").strip()

    name = data.get("name", "")
    email = data.get("email", "")
    message = data.get("message", "")

    # Basic validation
    if not name or not email or not message:
        return jsonify(
            {"ok": False, "error": "Please provide name, email and message."}
        ), 400
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify(
            {"ok": False, "error": "Please provide a valid email address."}
        ), 400

    entry = {
        "name": name,
        "email": email,
        "message": message,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    try:
        saved_places = save_contact_entry(entry)
    except Exception as e:
        current_app.logger.exception("Saving contact failed: %s", e)
        return jsonify({"ok": False, "error": "Server error saving submission."}), 500

    return jsonify({"ok": True, "saved": saved_places})


# Admin route to inspect contacts (protected by ADMIN_KEY env var)
@app.route("/admin/contacts")
def admin_contacts():
    ADMIN_KEY = os.environ.get("ADMIN_KEY")
    key = request.args.get("key")
    if ADMIN_KEY and key != ADMIN_KEY:
        return abort(403)

    results = []

    # Try Supabase first
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    if supabase_url and supabase_key:
        try:
            url = f"{supabase_url.rstrip('/')}/rest/v1/contacts?select=*&order=created_at.desc"
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
            }
            resp = requests.get(url, headers=headers, timeout=8)
            if resp.ok:
                results = resp.json()
        except Exception as e:
            current_app.logger.warning("Failed admin fetch from supabase: %s", e)

    # Merge file fallback entries (if any)
    try:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        contacts_file = os.path.join(data_dir, "contacts.json")
        if os.path.exists(contacts_file):
            with open(contacts_file, "r", encoding="utf-8") as f:
                file_entries = json.load(f)
                if isinstance(file_entries, list):
                    # prepend local entries if not present
                    # we'll not dedupe strongly; this is a simple merge
                    results = (results or []) + file_entries
    except Exception:
        pass

    return jsonify(results)


if __name__ == "__main__":
    # useful for local dev; Render will use gunicorn
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
