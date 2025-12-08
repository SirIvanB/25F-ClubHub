import datetime
from flask import Blueprint, jsonify, request
from backend.db_connection import cursor, db
from mysql.connector import Error
from flask import current_app
from datetime import datetime, timedelta

club_routes = Blueprint('club_routes', __name__)

# Get all clubs
@club_routes.route('/clubs', methods=['GET'])
def get_clubs():
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                c.clubID as club_id,
                c.name as club_name,
                c.budget,
                c.competitiveness_level
            FROM Clubs c
            LEFT JOIN club_memberships cm ON c.clubID = cm.club_id
            GROUP BY c.clubID, c.name, c.budget, c.competitiveness_level
            ORDER BY c.name ASC
        """
        cursor.execute(query)
        clubs = cursor.fetchall()
        return jsonify(clubs), 200
    except Error as e:
        current_app.logger.error(f"Error fetching clubs: {e}")
        return jsonify({"error": "Error fetching clubs"}), 500
    finally:
        cursor.close()

# Create new club
@club_routes.route('/clubs', methods=['POST'])
def create_club():
    try:
        data = request.get_json()
        cursor = db.cursor(dictionary=True)
        query = """
            INSERT INTO Clubs 
                (club_id, club_name, description, category, budget, 
                 contact_email, created_datetime)
            VALUES 
                (UUID(), %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """
        cursor.execute(query, (
            data['club_name'], data['description'], data['category'],
            data.get('budget', 0), data['contact_email']
        ))
        db.commit()
        return jsonify({"message": "Club created successfully"}), 201
    except Error as e:
        current_app.logger.error(f"Error creating club: {e}")
        return jsonify({"error": "Error creating club"}), 500
    finally:
        cursor.close()

# Get club details
@club_routes.route('/clubs/<club_id>', methods=['GET'])
def get_club_details(club_id):
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                c.clubID as club_id,
                c.name as club_name,
                c.adviser,
                c.categoryID as category,
                c.budget,
                c.type,
                c.competitiveness_level,
                c.email as contact_email,
                COUNT(DISTINCT e.eventID) AS event_count
            FROM Clubs c
            LEFT JOIN Events e ON c.clubID = e.clubID
            WHERE c.clubID = %s
            GROUP BY c.clubID, c.name, c.adviser, c.categoryID, 
                     c.budget, c.type, c.competitiveness_level, c.email
        """
        cursor.execute(query, (club_id,))
        club = cursor.fetchone()
        if club:
            return jsonify(club), 200
        else:
            return jsonify({"error": "Club not found"}), 404
    except Error as e:
        current_app.logger.error(f"Error fetching club details: {e}")
        return jsonify({"error": "Error fetching club details"}), 500
    finally:
        cursor.close()

# Update club
@club_routes.route('/clubs/<club_id>', methods=['PUT'])
def update_club(club_id):
    try:
        data = request.get_json()
        cursor = db.cursor(dictionary=True)
        query = """
            UPDATE Clubs 
            SET club_name = %s, description = %s, category = %s, 
                budget = %s, contact_email = %s, last_updated = CURRENT_TIMESTAMP
            WHERE club_id = %s
        """
        cursor.execute(query, (
            data['club_name'], data['description'], data['category'],
            data['budget'], data['contact_email'], club_id
        ))
        db.commit()
        return jsonify({"message": "Club updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Error updating club: {e}")
        return jsonify({"error": "Error updating club"}), 500
    finally:
        cursor.close()

# Deactivate club
@club_routes.route('/clubs/<club_id>', methods=['DELETE'])
def deactivate_club(club_id):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "UPDATE Clubs SET active = FALSE WHERE club_id = %s", 
            (club_id,)
        )
        db.commit()
        return jsonify({"message": "Club deactivated successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Error deactivating club: {e}")
        return jsonify({"error": "Error deactivating club"}), 500
    finally:
        cursor.close()

# [NewStudent-1.2] Compare clubs
@club_routes.route('/clubs/compare', methods=['GET'])
def compare_clubs():
    try:
        club_ids = request.args.get('ids')
        if not club_ids:
            return jsonify({"error": "Club IDs required"}), 400
        
        ids = tuple(club_ids.split(','))
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                c.clubID as club_id,
                c.name as club_name,
                c.adviser as curriculum,
                c.budget,
                c.competitiveness_level,
                COUNT(DISTINCT cm.student_id) AS number_of_members
            FROM Clubs c
            LEFT JOIN club_memberships cm ON c.clubID = cm.club_id
            WHERE c.clubID IN (%s)
            GROUP BY c.clubID, c.name, c.adviser, c.budget, c.competitiveness_level
        """ % ','.join(['%s'] * len(ids))
        cursor.execute(query, ids)
        comparison = cursor.fetchall()
        return jsonify(comparison), 200
    except Error as e:
        current_app.logger.error(f"Error comparing clubs: {e}")
        return jsonify({"error": "Error comparing clubs"}), 500
    finally:
        cursor.close()

# [NewStudent-1.6] Get club rankings
@club_routes.route('/rankings', methods=['GET'])
def get_club_rankings():
    try:
        period = request.args.get('period', '2025-Q4')
        
        # Parse period (e.g., "2025-Q4" -> year=2025, quarter=4)
        year, quarter = period.split('-Q')
        year = int(year)
        quarter = int(quarter)
        
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                c.clubID as club_id,
                c.name as club_name,
                c.budget,
                c.competitiveness_level,
                r.rankingValue as ranking_score,
                r.rankingType as ranking_type
            FROM Clubs c
            LEFT JOIN Rankings r ON c.clubID = r.clubID 
                AND r.rankingYear = %s 
                AND r.rankingQuarter = %s
            ORDER BY r.rankingValue DESC
        """
        cursor.execute(query, (year, quarter))
        rankings = cursor.fetchall()
        return jsonify(rankings), 200
    except Error as e:
        current_app.logger.error(f"Error fetching club rankings: {e}")
        return jsonify({"error": "Error fetching club rankings"}), 500
    finally:
        cursor.close()

# [EventsCoord-2.2] Get club events with RSVP stats
@club_routes.route('/clubs/<club_id>/events', methods=['GET'])
def get_club_events(club_id):
    try:
        upcoming = request.args.get('upcoming', 'true').lower() == 'true'
        cursor = db.cursor(dictionary=True)
        
        time_condition = ">=" if upcoming else "<"
        query = f"""
            SELECT 
                e.event_id,
                e.event_name,
                e.capacity,
                COUNT(r.rsvp_id) AS total_rsvps,
                SUM(CASE WHEN r.status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed_count,
                SUM(CASE WHEN r.status = 'waitlisted' THEN 1 ELSE 0 END) AS waitlist_count,
                (e.capacity - COUNT(r.rsvp_id)) AS remaining_capacity,
                e.start_datetime
            FROM Events e
            LEFT JOIN RSVPs r ON e.event_id = r.event_id
            WHERE e.club_id = %s
                AND e.start_datetime {time_condition} CURRENT_TIMESTAMP
            GROUP BY e.event_id, e.event_name, e.capacity, e.start_datetime
            ORDER BY e.start_datetime ASC
        """
        cursor.execute(query, (club_id,))
        events = cursor.fetchall()
        return jsonify(events), 200
    except Error as e:
        current_app.logger.error(f"Error fetching club events: {e}")
        return jsonify({"error": "Error fetching club events"}), 500
    finally:
        cursor.close()

# [EventsCoord-2.5] Get club analytics
@club_routes.route('/clubs/<club_id>/analytics', methods=['GET'])
def get_club_analytics(club_id):
    try:
        period = request.args.get('period', 'past')
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                e.event_id,
                e.event_name,
                e.event_type,
                e.start_datetime,
                e.capacity,
                COUNT(DISTINCT r.rsvp_id) AS total_rsvps,
                COUNT(DISTINCT a.attendance_id) AS actual_attendance,
                ROUND(COUNT(DISTINCT a.attendance_id) * 100.0 / 
                      NULLIF(COUNT(DISTINCT r.rsvp_id), 0), 2) AS attendance_rate,
                ROUND(COUNT(DISTINCT a.attendance_id) * 100.0 / 
                      NULLIF(e.capacity, 0), 2) AS capacity_utilization
            FROM Events e
            LEFT JOIN RSVPs r ON e.event_id = r.event_id
            LEFT JOIN attendance a ON e.event_id = a.event_id
            WHERE e.club_id = %s
                AND e.end_datetime < CURRENT_TIMESTAMP
            GROUP BY e.event_id, e.event_name, e.event_type, 
                     e.start_datetime, e.capacity
            ORDER BY e.start_datetime DESC
        """
        cursor.execute(query, (club_id,))
        analytics = cursor.fetchall()
        return jsonify(analytics), 200
    except Error as e:
        current_app.logger.error(f"Error fetching club analytics: {e}")
        return jsonify({"error": "Error fetching club analytics"}), 500
    finally:
        cursor.close()

# [EventsCoord-2.6] Find similar clubs
@club_routes.route('/clubs/<club_id>/similar', methods=['GET'])
def get_similar_clubs(club_id):
    try:
        min_events = request.args.get('minEvents', 5, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                c.club_id,
                c.club_name,
                c.category,
                COUNT(DISTINCT e.event_id) AS total_events,
                AVG(ea.attendance_count) AS avg_attendance,
                c.contact_email
            FROM Clubs c
            JOIN Events e ON c.club_id = e.club_id
            LEFT JOIN (
                SELECT event_id, COUNT(*) AS attendance_count
                FROM Attendance
                GROUP BY event_id
            ) ea ON e.event_id = ea.event_id
            WHERE c.club_id != %s
                AND c.category IN (
                    SELECT category 
                    FROM Clubs 
                    WHERE club_id = %s
                )
            GROUP BY c.club_id, c.club_name, c.category, c.contact_email
            HAVING COUNT(DISTINCT e.event_id) >= %s
            ORDER BY avg_attendance DESC
            LIMIT %s
        """
        cursor.execute(query, (club_id, club_id, min_events, limit))
        similar_clubs = cursor.fetchall()
        return jsonify(similar_clubs), 200
    except Error as e:
        current_app.logger.error(f"Error fetching similar clubs: {e}")
        return jsonify({"error": "Error fetching similar clubs"}), 500
    finally:
        cursor.close()

# [DataAnalyst-4.5] Get club performance metrics
@club_routes.route('/performance', methods=['GET'])
def get_club_performance():
    try:
        days = request.args.get('days', 90, type=int)
        start_date_str = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        min_events = 1 
        
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                c.clubID as club_id,
                c.name as club_name,
                COUNT(DISTINCT e.eventID) AS total_events,
                COUNT(DISTINCT r.rsvpID) AS total_rsvps,
                COUNT(DISTINCT sea.attendanceID) AS total_attendance,
                ROUND(AVG(event_attendance.attendance_count), 2) AS avg_attendance_per_event,
                ROUND(AVG(event_attendance.attendance_count) * 100.0 / 
                    NULLIF(AVG(e.capacity), 0), 2) AS avg_capacity_utilization
            FROM Clubs c
            JOIN Events e ON c.clubID = e.clubID
            LEFT JOIN RSVPs r ON e.eventID = r.eventID
                AND r.timestamp >= %s
            LEFT JOIN Students_Event_Attendees sea ON e.eventID = sea.eventID
                AND sea.timestamp >= %s
            LEFT JOIN (
                SELECT eventID, COUNT(*) AS attendance_count
                FROM Students_Event_Attendees
                WHERE timestamp >= %s
                GROUP BY eventID
            ) event_attendance ON e.eventID = event_attendance.eventID
            WHERE e.startDateTime >= %s
            GROUP BY c.clubID, c.name
            HAVING COUNT(DISTINCT e.eventID) >= %s
            ORDER BY avg_attendance_per_event DESC
        """

        cursor.execute(query, (start_date_str, start_date_str, start_date_str, start_date_str, min_events))
        performance = cursor.fetchall()
        return jsonify(performance), 200
    except Error as e:
        current_app.logger.error(f"Error fetching club performance: {e}")
        return jsonify({"error": "Error fetching club performance"}), 500
    finally:
        cursor.close()