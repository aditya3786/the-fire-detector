from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
import urllib.request
import urllib.error
import mimetypes

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret!')
# Use instance folder for database on Render
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', f'sqlite:///{os.path.join(instance_path, "alerts.db")}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
db = SQLAlchemy(app)

# --- Models ---
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    severity = db.Column(db.String(20), nullable=False) # high, medium, low
    location = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(200), nullable=False) # Renamed from description
    acknowledged = db.Column(db.Boolean, default=False) # Replaces status string
    notification_sent = db.Column(db.Boolean, default=False) # New field
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    type = db.Column(db.String(50), nullable=False) # fire, smoke
    confidence = db.Column(db.Float, default=0.0)

    def to_dict(self):
        # Calculate duration
        end_time = self.resolved_at if self.resolved_at else datetime.utcnow()
        duration = end_time - self.timestamp
        # Format duration
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            duration_str = f"{hours}h {minutes}m"
        elif minutes > 0:
            duration_str = f"{minutes}m {seconds}s"
        else:
            duration_str = f"{seconds}s"

        # Determine computed status for frontend compatibility
        if self.resolved_at:
            status_str = 'resolved'
        elif self.acknowledged:
            status_str = 'acknowledged'
        else:
            status_str = 'active'

        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity,
            'location': self.location,
            'message': self.message,
            'description': self.message, # Backward compatibility alias
            'status': status_str, # Computed status
            'acknowledged': self.acknowledged,
            'notification_sent': self.notification_sent,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'type': self.type,
            'confidence': self.confidence,
            'duration': duration_str
        }

# --- Helpers ---
def simulate_notifications(alert):
    """
    Simulate sending notifications based on severity.
    Returns a list of simulated actions.
    """
    actions = []
    msg = f"ALERT: {alert.severity.upper()} severity {alert.type} detected at {alert.location}."
    
    # Web notification is implicit via SocketIO
    actions.append("Web Dashboard Updated")

    if alert.severity in ['high', 'medium']:
        # Simulate SMS
        print(f"[SMS SIMULATION] Sending to Emergency Contacts: {msg}")
        actions.append("SMS Sent to Emergency Contacts")
        
        # Simulate Email
        print(f"[EMAIL SIMULATION] Sending to Admin: {msg}")
        actions.append("Email Sent to Admin")
    
    if alert.severity == 'high':
        # Simulate Siren/Audio
        print(f"[AUDIO SIMULATION] Triggering Siren for {alert.location}")
        actions.append("On-site Siren Triggered")

    return actions

# --- Routes ---

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/alerts-feed')
def alerts_page():
    return render_template('alerts.html')

@app.route('/alerts/<int:alert_id>')
def alert_details(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    return render_template('alert_details.html', alert=alert.to_dict())

@app.route('/notifications')
def notifications_page():
    return render_template('notifications.html')

@app.route('/status')
def status_page():
    return render_template('status.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy', 'service': 'flask-dashboard'}), 200

FASTAPI_BASE = os.getenv('FASTAPI_BASE', 'http://127.0.0.1:8001')

def _fetch_fastapi(path):
    url = FASTAPI_BASE + path
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode('utf-8'))

def _post_fastapi(path, payload):
    url = FASTAPI_BASE + path
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def _post_fastapi_multipart(path, filename, content_bytes):
    url = FASTAPI_BASE + path
    boundary = '----TraeBoundary7d9e3c6c'
    content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    lines = []
    lines.append(f'--{boundary}')
    lines.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"')
    lines.append(f'Content-Type: {content_type}')
    lines.append('')
    body_start = '\r\n'.join(lines).encode('utf-8') + b'\r\n'
    body_end = f'\r\n--{boundary}--\r\n'.encode('utf-8')
    body = body_start + content_bytes + body_end
    req = urllib.request.Request(url, data=body, headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def _transform_alert(a):
    status = 'acknowledged' if a.get('acknowledged') else 'active'
    a['status'] = status
    a['description'] = a.get('message')
    return a

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    try:
        items = _fetch_fastapi('/alerts')
        return jsonify([_transform_alert(x) for x in items])
    except Exception:
        alerts = Alert.query.order_by(Alert.timestamp.desc()).all()
        return jsonify([a.to_dict() for a in alerts])

# --- Alias endpoints to match expected external API ---
@app.route('/alerts', methods=['GET'])
def alerts_get_alias():
    try:
        items = _fetch_fastapi('/alerts')
        return jsonify([_transform_alert(x) for x in items])
    except Exception:
        alerts = Alert.query.order_by(Alert.timestamp.desc()).all()
        return jsonify([a.to_dict() for a in alerts])

@app.route('/api/alerts', methods=['POST'])
def create_alert():
    data = request.json or {}
    payload = {
        'severity': data.get('severity', 'low'),
        'location': data.get('location', 'Unknown'),
        'message': data.get('message') or data.get('description') or '',
        'type': data.get('type', 'fire'),
        'confidence': float(data.get('confidence', 0.0)),
    }
    try:
        created = _post_fastapi('/alerts', payload)
        transformed = _transform_alert(created)
        socketio.emit('new_alert', transformed)
        return jsonify(transformed), 201
    except Exception:
        msg = payload['message']
        new_alert = Alert(
            severity=payload['severity'],
            location=payload['location'],
            message=msg,
            type=payload['type'],
            confidence=payload['confidence'],
            acknowledged=False,
            notification_sent=False
        )
        db.session.add(new_alert)
        db.session.commit()
        notifications = simulate_notifications(new_alert)
        if new_alert.severity in ['high', 'medium']:
            new_alert.notification_sent = True
            db.session.commit()
        alert_data = new_alert.to_dict()
        alert_data['notifications_list'] = notifications
        socketio.emit('new_alert', alert_data)
        return jsonify(alert_data), 201

@app.route('/alerts', methods=['POST'])
def create_alert_alias():
    # Mirror create_alert behavior for expected POST /alerts
    return create_alert()

@app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['PUT'])
def acknowledge_alert(alert_id):
    try:
        updated = _post_fastapi(f'/alerts/{alert_id}/acknowledge', {})
        transformed = _transform_alert(updated)
        socketio.emit('alert_updated', transformed)
        return jsonify(transformed)
    except Exception:
        alert = Alert.query.get_or_404(alert_id)
        if not alert.acknowledged:
            alert.acknowledged = True
            alert.acknowledged_at = datetime.utcnow()
            db.session.commit()
            data = alert.to_dict()
            socketio.emit('alert_updated', data)
            return jsonify(data)
        return jsonify({'message': 'Alert already acknowledged'}), 400

@app.route('/upload-detect', methods=['POST'])
def upload_detect():
    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'file required'}), 400
    try:
        content = f.read()
        result = _post_fastapi_multipart('/detect/upload', f.filename or 'upload', content)
        # Emit alert if created
        alert = result.get('alert')
        if alert:
            socketio.emit('new_alert', _transform_alert(alert))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'upload failed', 'detail': str(e)}), 500

@app.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert_alias(alert_id):
    # Mirror acknowledge_alert behavior for expected POST /alerts/{id}/acknowledge
    return acknowledge_alert(alert_id)

@app.route('/api/alerts/<int:alert_id>/resolve', methods=['PUT'])
def resolve_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    # Check if already resolved
    if not alert.resolved_at:
        alert.resolved_at = datetime.utcnow()
        # Implicitly acknowledge if resolved? Usually yes.
        if not alert.acknowledged:
            alert.acknowledged = True
            alert.acknowledged_at = datetime.utcnow()
            
        db.session.commit()
        
        data = alert.to_dict()
        socketio.emit('alert_updated', data)
        return jsonify(data)
    return jsonify({'message': 'Alert already resolved'}), 400

@app.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert_alias(alert_id):
    # Provide alias for resolving via POST to match external style
    return resolve_alert(alert_id)

# Endpoint to clear db for testing
@app.route('/api/debug/clear', methods=['POST'])
def clear_db():
    db.session.query(Alert).delete()
    db.session.commit()
    socketio.emit('alerts_cleared')
    return jsonify({'message': 'Database cleared'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port)
