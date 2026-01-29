from flask import Flask, render_template, url_for
import os
import markdown
import re

app = Flask(__name__)

PROJECTS_DIR = 'pages'

def load_project_data(filename):
    filepath = os.path.join(PROJECTS_DIR, filename)
    if not os.path.exists(filepath):
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split front-matter and content
    match = re.match(r'---\s*(.*?)\s*---\s*(.*)', content, re.DOTALL)
    if not match:
        return {'title': os.path.splitext(filename)[0].replace('-', ' ').title(), 'content': markdown.markdown(content)}

    front_matter_str, md_content = match.groups()
    metadata = {}
    for line in front_matter_str.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip().strip('"')

    project_data = {
        'id': os.path.splitext(filename)[0],
        'title': metadata.get('title', os.path.splitext(filename)[0].replace('-', ' ').title()),
        'short_description': metadata.get('short_description', ''),
        'image': metadata.get('image', ''),
        'tags': [tag.strip() for tag in metadata.get('tags', '').split(',')] if metadata.get('tags') else [],
        'content': markdown.markdown(md_content)
    }
    return project_data

def get_all_projects():
    projects = []
    for filename in os.listdir(PROJECTS_DIR):
        if filename.endswith('.md'):
            project = load_project_data(filename)
            if project:
                projects.append(project)
    # Sort projects by a suitable key, e.g., title or date if available
    projects.sort(key=lambda x: x.get('title', '').lower())
    return projects

@app.route('/')
def index():
    projects = get_all_projects()
    return render_template('index.html', projects=projects)

@app.route('/project/<project_id>')
def project_detail(project_id):
    project = load_project_data(f'{project_id}.md')
    if project is None:
        return render_template('404.html'), 404 # We'll create a 404 later
    return render_template('project_detail.html', project=project)

if __name__ == '__main__':
    app.run(debug=True)