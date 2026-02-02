import json
import os
import re
from datetime import datetime

import markdown
from flask import Flask, jsonify, redirect, render_template, request, url_for

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
    for filename in os.listdir(PROJECTS_DIR):
        if filename.endswith(".md"):
            project = load_project_data(filename)
            if project:
                projects.append(project)
    # Sort projects by a suitable key, e.g., title or date if available
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
        return render_template("404.html"), 404  # We'll create a 404 later
    return render_template("project_detail.html", project=project)


# Contact page (GET)
@app.route("/contact")
def contact_page():
    return render_template("contact.html")


# Contact form submit (POST) - accepts JSON or form-encoded
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

    # Basic validation
    name = data.get("name", "") or data.get("full_name", "")
    email = data.get("email", "")
    message = data.get("message", "")

    if not name or not message:
        return jsonify({"ok": False, "error": "Please provide name and message."}), 400

    # Normalize entry
    entry = {
        "name": name,
        "email": email,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    # Ensure data directory exists and append to contacts JSON
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)

    contacts_file = os.path.join(data_dir, "contacts.json")
    # Read existing entries, append, write back
    try:
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

    except Exception as e:
        app.logger.error("Failed to save contact entry: %s", e)
        return jsonify({"ok": False, "error": "Server error saving submission."}), 500

    # Respond JSON success (frontend will show message)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)
