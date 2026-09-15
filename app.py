# app.py
# MODULE 1: Main Flask server — routes and request handling.
# This file is now clean and small — it just coordinates.
# All the real logic lives in the other modules.

from flask import Flask, render_template, request, jsonify
import os
import datetime

# Import our modules — this is what makes it multi-module
from database   import init_db, insert_report, get_all_reports, get_stats, get_reports_by_ward
from priority   import get_full_severity
from department import get_routing_info
from trust      import process_verification, get_trust_label
from clustering import cluster_reports, get_ward_health_report

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# ── Routes ──────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_report():
    issue_type  = request.form.get('issue_type', '')
    description = request.form.get('description', '')
    location    = request.form.get('location', '')
    ward        = request.form.get('ward', 'Unknown')
    submitted_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Module 3 — get priority + severity prediction
    severity    = get_full_severity(issue_type)

    # Module 4 — get government department routing
    routing     = get_routing_info(issue_type)

    # Save photo if uploaded
    photo_path = None
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename:
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
            photo.save(photo_path)

    # Module 2 — save to database
    new_id = insert_report(
        issue_type          = issue_type,
        description         = description,
        location            = location,
        priority            = severity['priority'],
        photo_path          = photo_path,
        submitted_at        = submitted_at,
        ward                = ward,
        department          = routing['department'],
        severity_score      = severity['severity_score'],
        predicted_worsening = severity['predicted_worsening']
    )

    return jsonify({
        'success':            True,
        'id':                 new_id,
        'issue_type':         issue_type,
        'priority':           severity['priority'],
        'severity_score':     severity['severity_score'],
        'predicted_worsening':severity['predicted_worsening'],
        'department':         routing['department'],
        'contact_email':      routing['contact_email'],
        'sla_days':           routing['sla_days'],
        'location':           location,
        'submitted_at':       submitted_at
    })

@app.route('/reports')
def get_reports():
    return jsonify(get_all_reports())

@app.route('/stats')
def get_stats_route():
    return jsonify(get_stats())

@app.route('/heatmap')
def get_heatmap():
    """Returns clustered issue data for the heat map."""
    reports  = get_all_reports()
    clusters = cluster_reports(reports)
    return jsonify(clusters)

@app.route('/ward-health')
def get_ward_health():
    """Returns civic health scores per ward — for urban planning."""
    ward_data = get_reports_by_ward()
    return jsonify(get_ward_health_report(ward_data))

@app.route('/verify/<int:report_id>', methods=['POST'])
def verify_report(report_id):
    """Community verification endpoint."""
    is_confirmed       = request.json.get('confirmed', True)
    reporter_score     = request.json.get('reporter_trust_score', 5.0)
    verifier_score     = request.json.get('verifier_trust_score', 5.0)
    result = process_verification(report_id, reporter_score, verifier_score, is_confirmed)
    return jsonify(result)

# ── Start ────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True)