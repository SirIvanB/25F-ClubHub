from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

admin_routes = Blueprint('admin_routes', __name__)



# GET /admin/audit-logs
@admin_routes.route('/audit-logs', methods=['GET'])
def get_audit_logs():
    """
    Return audit logs for authentication, event activity, and system actions.
    Uses EventLog + Servers tables.
    """
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                el.logID,
                el.logTimestamp,
                el.status,
                el.severity,
                el.serverID,
                s.ipAddress,
                s.status AS serverStatus,
                s.lastUpdated AS serverLastUpdated
            FROM EventLog el
            LEFT JOIN Servers s ON el.serverID = s.serverID
            ORDER BY el.logTimestamp DESC
            LIMIT 500
        """
        cursor.execute(query)
        logs = cursor.fetchall()
        return jsonify(logs), 200
    except Error as e:
        current_app.logger.error(f"Error fetching audit logs: {e}")
        return jsonify({"error": "Error fetching audit logs"}), 500
    finally:
        if cursor:
            cursor.close()



# GET /admin/alerts
@admin_routes.route('/alerts', methods=['GET'])
def get_unresolved_alerts():
    """
    Return unresolved alerts (isSolved = FALSE).
    Uses Alerts table.
    """
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                alertID,
                eventID,
                studentID,
                alertType,
                isSolved,
                description
            FROM Alerts
            WHERE isSolved = FALSE
            ORDER BY alertID DESC
        """
        cursor.execute(query)
        alerts = cursor.fetchall()
        return jsonify(alerts), 200
    except Error as e:
        current_app.logger.error(f"Error fetching alerts: {e}")
        return jsonify({"error": "Error fetching alerts"}), 500
    finally:
        if cursor:
            cursor.close()



# PUT /admin/alerts/<alert_id>
@admin_routes.route('/alerts/<int:alert_id>', methods=['PUT'])
def resolve_alert(alert_id):
    """
    Resolve an alert by setting isSolved = TRUE.
    """
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            UPDATE Alerts
            SET isSolved = TRUE
            WHERE alertID = %s
        """
        cursor.execute(query, (alert_id,))
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Alert not found"}), 404

        return jsonify({"message": "Alert resolved successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Error resolving alert {alert_id}: {e}")
        return jsonify({"error": "Error resolving alert"}), 500
    finally:
        if cursor:
            cursor.close()



# /admin/documentation (STUBS ONLY)
@admin_routes.route('/documentation', methods=['GET'])
def get_documentation_stub():
    """
    STUB: Documentation endpoint not implemented in current schema.
    """
    return jsonify({
        "error": "Documentation endpoint not implemented in current schema"
    }), 501  # 501 Not Implemented


@admin_routes.route('/documentation', methods=['POST'])
def create_documentation_stub():
    """
    STUB: Documentation endpoint not implemented in current schema.
    """
    return jsonify({
        "error": "Documentation creation not implemented in current schema"
    }), 501  # 501 Not Implemented


@admin_routes.route('/documentation/<doc_id>', methods=['PUT'])
def update_documentation_stub(doc_id):
    """
    STUB: Documentation endpoint not implemented in current schema.
    """
    return jsonify({
        "error": "Documentation update not implemented in current schema"
    }), 501  # 501 Not Implemented



# GET /admin/metrics
@admin_routes.route('/metrics', methods=['GET'])
def get_system_metrics():
    """
    Return system health metrics computed from Servers and EventLog.
    - Server counts (total / online / offline)
    - Log volume + error count in the last hour
    """
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)

        # 1) Server stats
        server_query = """
            SELECT 
                COUNT(*) AS total_servers,
                SUM(CASE WHEN status = 'online' THEN 1 ELSE 0 END) AS servers_online,
                SUM(CASE WHEN status != 'online' OR status IS NULL THEN 1 ELSE 0 END) AS servers_offline
            FROM Servers
        """
        cursor.execute(server_query)
        server_stats = cursor.fetchone() or {}

        # 2) Log stats for the last hour
        logs_query = """
            SELECT 
                COUNT(*) AS total_logs_last_hour,
                SUM(CASE WHEN severity = 'ERROR' THEN 1 ELSE 0 END) AS error_logs_last_hour
            FROM EventLog
            WHERE logTimestamp >= NOW() - INTERVAL 1 HOUR
        """
        cursor.execute(logs_query)
        log_stats = cursor.fetchone() or {}

        total_logs = log_stats.get("total_logs_last_hour") or 0
        error_logs = log_stats.get("error_logs_last_hour") or 0

        error_rate = None
        if total_logs > 0:
            error_rate = error_logs / float(total_logs)

        metrics = {
            "total_servers": server_stats.get("total_servers", 0),
            "servers_online": server_stats.get("servers_online", 0),
            "servers_offline": server_stats.get("servers_offline", 0),
            "total_logs_last_hour": total_logs,
            "error_logs_last_hour": error_logs,
            "error_rate_last_hour": error_rate,
        }

        return jsonify(metrics), 200

    except Error as e:
        current_app.logger.error(f"Error fetching system metrics: {e}")
        return jsonify({"error": "Error fetching system metrics"}), 500
    finally:
        if cursor:
            cursor.close()