"""
CVE Explainer Web Application
Flask API serving a web interface for CVE analysis
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import markdown
import os
from pathlib import Path
import sys

from env import MISTRAL_API_KEY, PORT

from cve import fetch_cve_data
from dependencies import scan_dependencies
from llm_init import get_agent
from llm_prompt import explain

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

app = Flask(__name__)
CORS(app)

# Configure markdown with extensions
md = markdown.Markdown(extensions=[
    'extra',
    'nl2br',
    'sane_lists',
    'fenced_code',
    'tables'
])


@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('static', 'index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_cve():
    """
    Analyze a CVE with context information

    Expected JSON:
    {
        "cve_id": "CVE-2024-1234",
        "context": {
            "dev_os": "macOS, Ubuntu 22.04",
            "server_os": "Ubuntu 22.04 LTS",
            "deployment": "Docker, Kubernetes",
            "frameworks": "Flask, React, PostgreSQL",
            "custom_info": "Additional context..."
        },
        "codebase_path": "." (optional)
    }
    """
    try:
        data = request.json
        cve_id = data.get('cve_id', '').strip()
        context = data.get('context', {})
        codebase_path = data.get('codebase_path', '.')

        if not cve_id:
            return jsonify({'error': 'CVE ID is required'}), 400

        cve_data = fetch_cve_data(cve_id)
        if not cve_data:
            return jsonify({
                'error': f'Could not fetch data for {cve_id}. CVE may not exist or databases are unavailable.'
            }), 404

        dependencies = scan_dependencies(codebase_path)

        deps = scan_dependencies(codebase_path)

        agent = get_agent(codebase_path)

        explanation = explain(
            agent=agent,
            cve_data=cve_data,
            dependencies=deps,
            api_key=MISTRAL_API_KEY
        )

        # Convert markdown to HTML
        html_explanation = md.convert(explanation)

        return jsonify({
            'success': True,
            'cve_id': cve_data.get('id'),
            'severity': cve_data.get('severity', 'Unknown'),
            'summary': cve_data.get('summary', ''),
            'markdown': explanation,
            'html': html_explanation,
            'total_dependencies': len(dependencies),
        })

    except Exception as e:
        return jsonify({
            'error': f'Internal error: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("🚀 Starting CVE Explainer Web Application")
    print(f"📍 Open http://localhost:{PORT} in your browser")
    app.run(debug=True, host='0.0.0.0', port=PORT)
