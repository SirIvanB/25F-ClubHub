from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

student_routes = Blueprint('student_routes', __name__)

@student_routes.route('/students', methods=['GET'])
def get_students():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Students")
        students = cursor.fetchall()
        return jsonify(students), 200
    except Error as e:
        current_app.logger.error(f"Error fetching students: {e}")
        return jsonify({"error": "Error fetching students"}), 500
    finally:
        cursor.close()

@student_routes.route('/students/<int:student_id>/rsvps', methods=['GET'])
def get_student_rsvps(student_id):
    """
    Return all confirmed RSVPs for a specific student.
    
    :param student_id: Description
    """
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                r.rsvp_id,
                e.event_id,
                e.event_name,
                e.start_datetime,
                e.location,
                e.last_updated,
                c.club_name
                FROM RSVPs r
                    JOIN Events e ON r.event_id = e.event_id
                    JOIN Clubs c ON e.club_id = c.club_id
                WHERE r.student_id = %s
                    AND e.start_datetime > CURRENT_TIMESTAMP
                    AND r.status = 'confirmed'
                ORDER BY e.start_datetime ASC;

        """
        cursor.execute(query, (student_id,))
        rsvps = cursor.fetchall()
        return jsonify(rsvps), 200
    except Error as e:
        current_app.logger.error(f"Error fetching RSVPs for student {student_id}: {e}")
        return jsonify({"error": "Error fetching RSVPs"}), 500
    finally:
        cursor.close()

# Create RSVP
@student_routes.route('/students/<student_id>/rsvps', methods=['POST'])
def create_rsvp(student_id):
    try:
        data = request.get_json()
        cursor = db.cursor(dictionary=True)
        query = """
            INSERT INTO RSVPs 
                (studentID, eventID, status, timestamp)
            VALUES 
                (%s, %s, 'confirmed', CURRENT_TIMESTAMP)
        """
        cursor.execute(query, (data['event_id'], student_id))
        db.commit()
        return jsonify({"message": "RSVP created successfully"}), 201
    except Error as e:
        current_app.logger.error(f"Error creating RSVP: {e}")
        return jsonify({"error": "Error creating RSVP"}), 500
    finally:
        cursor.close()

# Get student invitations
@student_routes.route('/students/<student_id>/invitations', methods=['GET'])
def get_student_invitations(student_id):
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                ei.invitation_id,
                ei.event_id,
                e.event_name,
                e.start_datetime,
                ei.sender_student_id,
                s.first_name AS sender_first_name,
                s.last_name AS sender_last_name,
                ei.invitation_status,
                ei.sent_datetime
            FROM Event_Invitations ei
            JOIN Events e ON ei.event_id = e.event_id
            JOIN Students s ON ei.sender_student_id = s.student_id
            WHERE ei.recipient_student_id = %s
            ORDER BY ei.sent_datetime DESC
        """
        cursor.execute(query, (student_id,))
        invitations = cursor.fetchall()
        return jsonify(invitations), 200
    except Error as e:
        current_app.logger.error(f"Error fetching invitations: {e}")
        return jsonify({"error": "Error fetching invitations"}), 500
    finally:
        cursor.close()

# Update invitation status
@student_routes.route('/students/<student_id>/invitations/<invitation_id>', methods=['PUT'])
def update_invitation_status(student_id, invitation_id):
    try:
        data = request.get_json()
        cursor = db.cursor(dictionary=True)
        query = """
            UPDATE Event_Invitations 
            SET invitation_status = %s, updated_datetime = CURRENT_TIMESTAMP
            WHERE invitation_id = %s AND recipient_student_id = %s
        """
        cursor.execute(query, (data['status'], invitation_id, student_id))
        db.commit()
        return jsonify({"message": "Invitation status updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Error updating invitation: {e}")
        return jsonify({"error": "Error updating invitation"}), 500
    finally:
        cursor.close()