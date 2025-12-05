from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

analytics_routes = Blueprint("analytics_routes", __name__)


# GET /analytics/engagement
@analytics_routes.route("/analytics/engagement", methods=["GET"])
def get_engagement_metrics():
    """
    Return the daily engagement metrics.

    Uses audit_logs table with columns like:
      - activity_date (DATE or DATETIME)
      - user_id
      - action_type  ('event_view', 'rsvp_created', 'search', 'check_in', etc.)
      - entity_id
      - log_id
    """
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                DATE(activity_date) AS date,
                COUNT(DISTINCT user_id) AS daily_active_users,
                COUNT(DISTINCT CASE WHEN action_type = 'event_view'
                      THEN entity_id END) AS events_viewed,
                COUNT(DISTINCT CASE WHEN action_type = 'rsvp_created'
                      THEN entity_id END) AS rsvps_created,
                COUNT(DISTINCT CASE WHEN action_type = 'search'
                      THEN log_id END) AS searches_performed,
                COUNT(DISTINCT CASE WHEN action_type = 'check_in'
                      THEN entity_id END) AS check_ins
            FROM audit_logs
            WHERE activity_date >= CURDATE() - INTERVAL 30 DAY
            GROUP BY DATE(activity_date)
            ORDER BY date DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f"Error fetching engagement metrics: {e}")
        return jsonify({"error": "Error fetching engagement metrics"}), 500
    finally:
        if cursor:
            cursor.close()



# GET /analytics/search-queries
@analytics_routes.route("/analytics/search-queries", methods=["GET"])
def get_search_query_analysis():
    """
    Return search query analytics based on search_logs:

    Expects search_logs to have columns:
      - search_query
      - results_count
      - search_datetime
    """
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                sl.search_query,
                COUNT(*) AS search_count,
                SUM(CASE WHEN sl.results_count = 0 THEN 1 ELSE 0 END) AS zero_results_count,
                AVG(sl.results_count) AS avg_results_count,
                MAX(sl.search_datetime) AS last_searched
            FROM search_logs sl
            WHERE sl.search_datetime >= NOW() - INTERVAL 30 DAY
            GROUP BY sl.search_query
            HAVING SUM(CASE WHEN sl.results_count = 0 THEN 1 ELSE 0 END) > 0
            ORDER BY search_count DESC, zero_results_count DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f"Error fetching search query analysis: {e}")
        return jsonify({"error": "Error fetching search query analysis"}), 500
    finally:
        if cursor:
            cursor.close()



# GET /analytics/demographics
@analytics_routes.route("/analytics/demographics", methods=["GET"])
def get_demographic_engagement():
    """
    Return engagement analysis by student demographics.

    Conceptually matches Part 3 SQL:

    FROM students s
      LEFT JOIN rsvps r ON s.student_id = r.student_id
      LEFT JOIN attendance a ON s.student_id = a.student_id
           AND r.event_id = a.event_id

    with fields like s.student_year, s.major, r.created_datetime, etc.
    """
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                s.student_year,
                s.major,
                COUNT(DISTINCT r.student_id) AS students_with_rsvps,
                COUNT(DISTINCT r.event_id) AS unique_events_rsvped,
                COUNT(r.rsvp_id) AS total_rsvps,
                COUNT(DISTINCT a.event_id) AS events_attended,
                ROUND(
                    COUNT(DISTINCT a.event_id) * 100.0 /
                    NULLIF(COUNT(DISTINCT r.event_id), 0),
                    2
                ) AS attendance_rate
            FROM students s
            LEFT JOIN rsvps r 
                ON s.student_id = r.student_id
            LEFT JOIN attendance a 
                ON s.student_id = a.student_id
               AND r.event_id = a.event_id
            WHERE r.created_datetime >= NOW() - INTERVAL 90 DAY
            GROUP BY s.student_year, s.major
            ORDER BY total_rsvps DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f"Error fetching demographic engagement: {e}")
        return jsonify({"error": "Error fetching demographic engagement"}), 500
    finally:
        if cursor:
            cursor.close()



# GET /analytics/reports
@analytics_routes.route("/analytics/reports", methods=["GET"])
def get_engagement_reports():
    """
    Return generated engagement reports.

    Expects engagement_reports table with columns:
      - report_id
      - report_period_start
      - report_period_end
      - total_active_users
      - total_events_created
      - total_rsvps
      - total_attendance
      - total_searches
      - generated_datetime
    """
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                report_id,
                report_period_start,
                report_period_end,
                total_active_users,
                total_events_created,
                total_rsvps,
                total_attendance,
                total_searches,
                generated_datetime
            FROM engagement_reports
            ORDER BY generated_datetime DESC
            LIMIT 50;
        """
        cursor.execute(query)
        reports = cursor.fetchall()
        return jsonify(reports), 200
    except Error as e:
        current_app.logger.error(f"Error fetching engagement reports: {e}")
        return jsonify({"error": "Error fetching engagement reports"}), 500
    finally:
        if cursor:
            cursor.close()



# POST /analytics/reports
@analytics_routes.route("/analytics/reports", methods=["POST"])
def generate_weekly_engagement_report():
    """
    Generate and save a weekly engagement report.

    This is a MySQL-ish adaptation of your Part 3 query.

    It summarizes the last 7 days of activity in audit_logs
    into a single row in engagement_reports.
    """
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)

        insert_query = """
            INSERT INTO engagement_reports 
                (report_period_start,
                 report_period_end,
                 total_active_users,
                 total_events_created,
                 total_rsvps,
                 total_attendance,
                 total_searches,
                 generated_datetime)
            SELECT
                DATE_SUB(CURDATE(), INTERVAL 7 DAY) AS report_period_start,
                CURDATE() AS report_period_end,
                COUNT(DISTINCT CASE 
                    WHEN al.action_type IN ('login', 'event_view', 'search')
                    THEN al.user_id
                END) AS total_active_users,
                COUNT(DISTINCT CASE 
                    WHEN al.action_type = 'event_created'
                    THEN al.entity_id
                END) AS total_events_created,
                COUNT(DISTINCT CASE 
                    WHEN al.action_type = 'rsvp_created'
                    THEN al.log_id
                END) AS total_rsvps,
                COUNT(DISTINCT CASE 
                    WHEN al.action_type = 'check_in'
                    THEN al.log_id
                END) AS total_attendance,
                COUNT(DISTINCT CASE 
                    WHEN al.action_type = 'search'
                    THEN al.log_id
                END) AS total_searches,
                NOW() AS generated_datetime
            FROM audit_logs al
            WHERE al.timestamp >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
              AND al.timestamp < CURDATE() + INTERVAL 1 DAY;
        """

        cursor.execute(insert_query)
        db.commit()

        return jsonify({"message": "Weekly engagement report generated"}), 201
    except Error as e:
        current_app.logger.error(f"Error generating engagement report: {e}")
        return jsonify({"error": "Error generating engagement report"}), 500
    finally:
        if cursor:
            cursor.close()