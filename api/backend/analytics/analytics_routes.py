from flask import Blueprint, jsonify, request
from backend.db_connection import db
from pymysql import Error
from flask import current_app
from pymysql.cursors import DictCursor
from datetime import datetime, timedelta

analytics_routes = Blueprint("analytics_routes", __name__)


# GET /analytics/engagement/current-metrics
@analytics_routes.route("/engagement/current-metrics", methods=["GET"])
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
                    SELECT COUNT(DISTINCT invitationID)
                    FROM Event_Invitations
                    WHERE status = 'accepted'
                      AND sentAt >= %s
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
@analytics_routes.route("/engagement/previous-metrics", methods=["GET"])
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
                    SELECT COUNT(DISTINCT invitationID)
                    FROM Event_Invitations
                    WHERE status = 'accepted'
                      AND sentAt >= %s
                      AND sentAt < %s
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
@analytics_routes.route("/engagement/events-by-month", methods=["GET"])
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
@analytics_routes.route("/engagement/top-clubs", methods=["GET"])
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

# GET /engagement/engagement-rate
@analytics_routes.route("/engagement/engagement-rate", methods=["GET"])
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

# GET /search/summary
@analytics_routes.route("/search/summary", methods=["GET"])
def get_search_summary():
    """Get search summary metrics (last 90 days)"""
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        query = """
            SELECT
                COUNT(*) as total_searches,
                COUNT(DISTINCT searchQuery) as unique_queries,
                (SELECT COUNT(DISTINCT s.searchID) 
                 FROM Searches s
                 LEFT JOIN Searches_Search_Results ssr ON s.searchID = ssr.searchID
                 WHERE DATE(s.timestamp) >= %s 
                   AND ssr.resultID IS NULL) as no_result_searches
            FROM Searches
            WHERE DATE(timestamp) >= %s
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

# GET /search/top-keywords
@analytics_routes.route("/search/top-keywords", methods=["GET"])
def get_top_keywords():
    """Get most searched keywords with CTR data"""
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        query = """
            SELECT
                s.searchQuery as query,
                COUNT(DISTINCT s.searchID) as search_count,
                COUNT(DISTINCT ssr.resultID) as total_results,
                ROUND(COUNT(DISTINCT ssr.resultID) * 1.0 / COUNT(DISTINCT s.searchID), 1) as avg_results,
                SUM(sr.clicks) as clicks,
                ROUND(SUM(sr.clicks) * 100.0 / COUNT(DISTINCT s.searchID), 1) as ctr
            FROM Searches s
            LEFT JOIN Searches_Search_Results ssr ON s.searchID = ssr.searchID
            LEFT JOIN Search_Result sr ON ssr.resultID = sr.resultID
            WHERE DATE(s.timestamp) >= %s
            GROUP BY s.searchQuery
            HAVING search_count > 0
            ORDER BY search_count DESC
            LIMIT 20
        """
        
        cursor.execute(query, (start_date,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching top keywords: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()

# GET /search/no-results
@analytics_routes.route("/search/no-results", methods=["GET"])
def get_no_result_searches():
    """Get searches that returned no results"""
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        query = """
            SELECT
                s.searchQuery as query,
                COUNT(*) as search_count
            FROM Searches s
            LEFT JOIN Searches_Search_Results ssr ON s.searchID = ssr.searchID
            WHERE DATE(s.timestamp) >= %s
              AND ssr.resultID IS NULL
            GROUP BY s.searchQuery
            ORDER BY search_count DESC
            LIMIT 20
        """
        
        cursor.execute(query, (start_date,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching no-result searches: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()

# GET /analytics/demographics
@analytics_routes.route("/demographics/overview", methods=["GET"])
def get_demographic_overview():
    """
    Return engagement analysis by student demographics (year and major).
    """
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        query = """
            SELECT 
                s.year as student_year,
                s.major,
                COUNT(DISTINCT s.studentID) as total_students,
                COUNT(DISTINCT r.rsvpID) as total_rsvps,
                COUNT(DISTINCT sea.attendanceID) as total_attendance,
                COUNT(DISTINCT sea.eventID) as unique_events_attended,
                ROUND(
                    COUNT(DISTINCT sea.studentID) * 100.0 / COUNT(DISTINCT s.studentID),
                    1
                ) as engagement_rate
            FROM Students s
            LEFT JOIN RSVPs r 
                ON s.studentID = r.studentID
                AND r.timestamp >= %s
            LEFT JOIN Students_Event_Attendees sea 
                ON s.studentID = sea.studentID
                AND sea.timestamp >= %s
            GROUP BY s.year, s.major
            ORDER BY engagement_rate DESC
        """
        
        cursor.execute(query, (start_date, start_date))
        rows = cursor.fetchall()
        return jsonify(rows), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching demographic overview: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()

# GET /demographics/by-year
@analytics_routes.route("/demographics/by-year", methods=["GET"])
def get_engagement_by_year():
    """Engagement breakdown by student year"""
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        query = """
            SELECT 
                s.year,
                COUNT(DISTINCT s.studentID) as total_students,
                COUNT(DISTINCT sea.studentID) as active_students,
                COUNT(DISTINCT sea.attendanceID) as total_attendance,
                ROUND(
                    COUNT(DISTINCT sea.studentID) * 100.0 / COUNT(DISTINCT s.studentID),
                    1
                ) as participation_rate
            FROM Students s
            LEFT JOIN Students_Event_Attendees sea 
                ON s.studentID = sea.studentID
                AND sea.timestamp >= %s
            GROUP BY s.year
            ORDER BY s.year
        """
        
        cursor.execute(query, (start_date,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching engagement by year: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()


# GET /demographics/by-major
@analytics_routes.route("/demographics/by-major", methods=["GET"])
def get_engagement_by_major():
    """Engagement breakdown by major"""
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        query = """
            SELECT 
                s.major,
                COUNT(DISTINCT s.studentID) as total_students,
                COUNT(DISTINCT sea.studentID) as active_students,
                COUNT(DISTINCT sea.attendanceID) as total_attendance,
                ROUND(AVG(attendance_per_student.attendance_count), 1) as avg_attendance_per_student,
                ROUND(
                    COUNT(DISTINCT sea.studentID) * 100.0 / COUNT(DISTINCT s.studentID),
                    1
                ) as participation_rate
            FROM Students s
            LEFT JOIN Students_Event_Attendees sea 
                ON s.studentID = sea.studentID
                AND sea.timestamp >= %s
            LEFT JOIN (
                SELECT studentID, COUNT(*) as attendance_count
                FROM Students_Event_Attendees
                WHERE timestamp >= %s
                GROUP BY studentID
            ) as attendance_per_student ON s.studentID = attendance_per_student.studentID
            GROUP BY s.major
            ORDER BY participation_rate DESC
        """
        
        cursor.execute(query, (start_date, start_date))
        rows = cursor.fetchall()
        return jsonify(rows), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching engagement by major: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()


# GET /demographics/event-preferences
@analytics_routes.route("/demographics/event-preferences", methods=["GET"])
def get_event_preferences_by_demographic():
    """Show which demographics attend which event categories"""
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        query = """
            SELECT 
                s.major,
                s.year,
                cat.name as category_name,
                COUNT(DISTINCT sea.attendanceID) as attendance_count,
                COUNT(DISTINCT sea.studentID) as unique_students
            FROM Students s
            JOIN Students_Event_Attendees sea ON s.studentID = sea.studentID
            JOIN Events e ON sea.eventID = e.eventID
            JOIN Clubs c ON e.clubID = c.clubID
            JOIN Categories cat ON c.categoryID = cat.categoryID
            WHERE sea.timestamp >= %s
            GROUP BY s.major, s.year, cat.name
            ORDER BY s.major, attendance_count DESC
        """
        
        cursor.execute(query, (start_date,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching event preferences: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()


# GET /demographics/underserved
@analytics_routes.route("/demographics/underserved", methods=["GET"])
def get_underserved_populations():
    """Identify demographics with low engagement"""
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)
        
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        query = """
            SELECT 
                s.major,
                s.year,
                COUNT(DISTINCT s.studentID) as total_students,
                COUNT(DISTINCT sea.studentID) as active_students,
                ROUND(
                    COUNT(DISTINCT sea.studentID) * 100.0 / COUNT(DISTINCT s.studentID),
                    1
                ) as participation_rate,
                (SELECT AVG(participation_rate)
                 FROM (
                     SELECT 
                         COUNT(DISTINCT sea2.studentID) * 100.0 / COUNT(DISTINCT s2.studentID) as participation_rate
                     FROM Students s2
                     LEFT JOIN Students_Event_Attendees sea2 
                         ON s2.studentID = sea2.studentID
                         AND sea2.timestamp >= %s
                     GROUP BY s2.major, s2.year
                 ) as avg_calc
                ) as overall_avg_rate
            FROM Students s
            LEFT JOIN Students_Event_Attendees sea 
                ON s.studentID = sea.studentID
                AND sea.timestamp >= %s
            GROUP BY s.major, s.year
            HAVING participation_rate < overall_avg_rate
            ORDER BY participation_rate ASC
        """
        
        cursor.execute(query, (start_date, start_date))
        rows = cursor.fetchall()
        return jsonify(rows), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching underserved populations: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()



# GET /reports
@analytics_routes.route("/reports", methods=["GET"])
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
                reportID,
                reportPeriodStart,
                reportPeriodEnd,
                totalActiveUsers,
                totalEventsCreated,
                totalRSVPs,
                totalAttendance,
                totalSearches,
                generatedAt
            FROM Engagement_Reports
            ORDER BY generatedAt DESC
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



# POST /reports
@analytics_routes.route("/reports", methods=["POST"])
def generate_weekly_engagement_report():
    """
    Generate and save a weekly engagement report.

    It summarizes the last 7 days of activity in audit_logs
    into a single row in engagement_reports.
    """
    cursor = None
    try:
        cursor = db.get_db().cursor(DictCursor)

        # Calculate dates in Python
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        end_date_str = end_date.strftime('%Y-%m-%d')
        start_date_str = start_date.strftime('%Y-%m-%d')

        insert_query = """
            INSERT INTO Engagement_Reports 
                (reportPeriodStart,
                 reportPeriodEnd,
                 totalActiveUsers,
                 totalEventsCreated,
                 totalRSVPs,
                 totalAttendance,
                 totalSearches,
                 generatedAt)
            VALUES (
                %s,
                %s,
                (SELECT COUNT(DISTINCT userID) 
                 FROM Audit_Logs 
                 WHERE actionType IN ('login', 'event_view', 'search')
                   AND timestamp >= %s
                   AND timestamp < %s),
                (SELECT COUNT(DISTINCT entityID) 
                 FROM Audit_Logs 
                 WHERE actionType = 'event_created'
                   AND timestamp >= %s
                   AND timestamp < %s),
                (SELECT COUNT(DISTINCT logID) 
                 FROM Audit_Logs 
                 WHERE actionType = 'rsvp_created'
                   AND timestamp >= %s
                   AND timestamp < %s),
                (SELECT COUNT(DISTINCT logID) 
                 FROM Audit_Logs 
                 WHERE actionType = 'check_in'
                   AND timestamp >= %s
                   AND timestamp < %s),
                (SELECT COUNT(DISTINCT logID) 
                 FROM Audit_Logs 
                 WHERE actionType = 'search'
                   AND timestamp >= %s
                   AND timestamp < %s),
                NOW()
            )
        """

        cursor.execute(insert_query, (
            start_date_str, end_date_str,  # reportPeriodStart, reportPeriodEnd
            start_date_str, end_date_str,  # totalActiveUsers
            start_date_str, end_date_str,  # totalEventsCreated
            start_date_str, end_date_str,  # totalRSVPs
            start_date_str, end_date_str,  # totalAttendance
            start_date_str, end_date_str   # totalSearches
        ))
        db.commit()

        return jsonify({"message": "Weekly engagement report generated"}), 201
    except Error as e:
        current_app.logger.error(f"Error generating engagement report: {e}")
        return jsonify({"error": "Error generating engagement report"}), 500
    finally:
        if cursor:
            cursor.close()