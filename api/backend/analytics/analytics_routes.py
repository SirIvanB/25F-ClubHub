from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app
from pymysql.cursors import DictCursor
from datetime import datetime, timedelta

analytics_routes = Blueprint("analytics_routes", __name__)

# GET /analytics/engagement/current-metrics
@analytics_routes.route("/analytics/engagement/current-metrics", methods=["GET"])
def get_current_period_metrics():
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        
        query = """
            SELECT
                COUNT(DISTINCT e.eventID) AS total_events,
                (
                    SELECT COUNT(DISTINCT invitation_id)
                    FROM event_invitations
                    WHERE invitation_status = 'accepted'
                      AND sent_datetime >= %s
                ) AS total_rsvps,
                COUNT(DISTINCT sea.attendanceID) AS total_checkins,
                COUNT(DISTINCT sea.studentID) AS active_users
            FROM Events e
            LEFT JOIN Students_Event_Attendees sea 
                ON e.eventID = sea.eventID 
                AND sea.timestamp >= %s
            WHERE e.startDateTime >= %s
        """
        
        cursor.execute(query, (start_date_str, start_date_str, start_date_str))
        result = cursor.fetchone()
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Error fetching current metrics: {e}")
        return jsonify({"error": "Error fetching current metrics"}), 500
    finally:
        if cursor:
            cursor.close()


# GET /analytics/engagement/previous-metrics
@analytics_routes.route("/analytics/engagement/previous-metrics", methods=["GET"])
def get_previous_period_metrics():
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        # 30-60 days ago
        end_date = datetime.now() - timedelta(days=30)
        start_date = datetime.now() - timedelta(days=60)

        end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
        start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        
        query = """
            SELECT
                COUNT(DISTINCT e.eventID) AS total_events,
                (
                    SELECT COUNT(DISTINCT invitation_id)
                    FROM event_invitations
                    WHERE invitation_status = 'accepted'
                      AND sent_datetime >= %s
                      AND sent_datetime < %s
                ) AS total_rsvps,
                COUNT(DISTINCT sea.attendanceID) AS total_checkins,
                COUNT(DISTINCT sea.studentID) AS active_users
            FROM Events e
            LEFT JOIN Students_Event_Attendees sea 
                ON e.eventID = sea.eventID 
                AND sea.timestamp >= %s
                AND sea.timestamp < %s
            WHERE e.startDateTime >= %s
              AND e.startDateTime < %s
        """
        
        cursor.execute(query, (start_date_str, end_date_str, start_date_str, end_date_str, start_date_str, end_date_str))
        result = cursor.fetchone()
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Error fetching previous metrics: {e}")
        return jsonify({"error": "Error fetching previous metrics"}), 500
    finally:
        if cursor:
            cursor.close()

# GET /analytics/engagement/events-by-month
@analytics_routes.route("/analytics/engagement/events-by-month", methods=["GET"])
def get_events_by_month():
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        # Last 6 months
        start_date = datetime.now() - timedelta(days=180)
        start_date_str = start_date.strftime('%Y-%m-%d')
        
        query = """
            SELECT
                DATE_FORMAT(startDateTime, '%%Y-%%m') AS month,
                DATE_FORMAT(startDateTime, '%%M %%Y') AS month_name,
                COUNT(DISTINCT eventID) AS event_count
            FROM Events
            WHERE DATE(startDateTime) >= %s
            GROUP BY 
                DATE_FORMAT(startDateTime, '%%Y-%%m'),
                DATE_FORMAT(startDateTime, '%%M %%Y')
            ORDER BY month ASC;
        """
        
        cursor.execute(query, (start_date_str,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f"Error fetching events by month: {e}")
        return jsonify({"error": "Error fetching events by month"}), 500
    finally:
        if cursor:
            cursor.close()

# GET /analytics/engagement/top-clubs
@analytics_routes.route("/analytics/engagement/top-clubs", methods=["GET"])
def get_top_clubs_by_engagement():
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = datetime.now() - timedelta(days=30)
        
        query = """
            SELECT
                c.clubID,
                c.name AS club_name,
                COUNT(DISTINCT sea.attendanceID) AS total_checkins,
                COUNT(DISTINCT e.eventID) AS events_hosted,
                COUNT(DISTINCT sea.studentID) AS unique_attendees
            FROM Clubs c
            JOIN Events e ON c.clubID = e.clubID
            LEFT JOIN Students_Event_Attendees sea 
                ON e.eventID = sea.eventID
                AND sea.timestamp >= %s
            WHERE e.startDateTime >= %s
            GROUP BY c.clubID, c.name
            HAVING events_hosted > 0
            ORDER BY total_checkins DESC
            LIMIT 10
        """
        
        cursor.execute(query, (start_date, start_date))
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Error as e:
        current_app.logger.error(f"Error fetching top clubs: {e}")
        return jsonify({"error": "Error fetching top clubs"}), 500
    finally:
        if cursor:
            cursor.close()

# GET /analytics/engagement/engagement-rate
@analytics_routes.route("/analytics/engagement/engagement-rate", methods=["GET"])
def get_engagement_rate():
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = datetime.now() - timedelta(days=30)
        
        query = """
            SELECT
                COUNT(DISTINCT sea.studentID) AS active_students,
                (SELECT COUNT(*) FROM Students) AS total_students,
                ROUND(
                    (COUNT(DISTINCT sea.studentID) / (SELECT COUNT(*) FROM Students)) * 100,
                    2
                ) AS engagement_rate
            FROM Students_Event_Attendees sea
            WHERE sea.timestamp >= %s
        """
        
        cursor.execute(query, (start_date,))
        result = cursor.fetchone()
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f"Error calculating engagement rate: {e}")
        return jsonify({"error": "Error calculating engagement rate"}), 500
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
        cursor = db.get_db().cursor(DictCursor)
        query = """
            SELECT 
                sl.search_query,
                COUNT(*) AS search_count,
                SUM(CASE WHEN sl.results_count = 0 THEN 1 ELSE 0 END) AS zero_results_count,
                AVG(sl.results_count) AS avg_results_count,
                MAX(sl.search_datetime) AS last_searched
            FROM Search_Logs sl
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

# GET /analytics/search/summary
@analytics_routes.route("/analytics/search/summary", methods=["GET"])
def get_search_summary():
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        query = """
            SELECT
                COUNT(*) as total_searches,
                COUNT(DISTINCT search_query) as unique_queries,
                (SELECT COUNT(*) 
                 FROM SearchLogs 
                 WHERE search_date >= %s AND results_count = 0) as no_result_searches
            FROM SearchLogs
            WHERE search_date >= %s
        """
        
        cursor.execute(query, (start_date, start_date))
        result = cursor.fetchone()
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching search summary: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()



# GET /analytics/demographics
@analytics_routes.route("/analytics/demographics", methods=["GET"])
def get_demographic_engagement():
    """
    Return engagement analysis by student demographics.

    Conceptually matches Part 3 SQL:

    FROM Students s
      LEFT JOIN RSVPs r ON s.student_id = r.student_id
      LEFT JOIN Attendance a ON s.student_id = a.student_id
           AND r.event_id = a.event_id

    with fields like s.student_year, s.major, r.created_datetime, etc.
    """
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
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
            FROM Students s
            LEFT JOIN RSVPs r 
                ON s.student_id = r.student_id
            LEFT JOIN Attendance a 
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
        cursor = db.get_db().cursor(DictCursor)
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
            FROM Engagement_Reports
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
        cursor = db.get_db().cursor(DictCursor)

        insert_query = """
            INSERT INTO Engagement_Reports 
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
            FROM Audit_Logs al
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