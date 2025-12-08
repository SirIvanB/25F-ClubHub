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
                r.rsvpID as rsvp_id,
                e.eventID as event_id,
                e.name as event_name,
                e.startDateTime as start_datetime,
                e.location,
                e.lastUpdated as last_updated,
                c.name as club_name
            FROM RSVPs r
            JOIN Events e ON r.eventID = e.eventID
            JOIN Clubs c ON e.clubID = c.clubID
            WHERE r.studentID = %s
                AND e.startDateTime > CURRENT_TIMESTAMP
                AND r.status = 'confirmed'
            ORDER BY e.startDateTime ASC
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
        cursor.execute(query, (student_id, data['event_id']))
        db.commit()
        return jsonify({"message": "RSVP created successfully"}), 201
    except Error as e:
        current_app.logger.error(f"Error creating RSVP: {e}")
        return jsonify({"error": "Error creating RSVP"}), 500
    finally:
        cursor.close()

# Cancel RSVP
@student_routes.route('/students/<student_id>/rsvps/<int:rsvp_id>', methods=['DELETE'])
def cancel_rsvp(student_id, rsvp_id):
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            DELETE FROM RSVPs
            WHERE rsvpID = %s AND studentID = %s
        """
        cursor.execute(query, (rsvp_id, student_id))
        db.commit()

        if cursor.rowcount > 0:
            return jsonify({"message": "RSVP cancelled successfully"}), 200
        else:
            return jsonify({"error": "RSVP not found"}), 404

    except Error as e:
        current_app.logger.error(f"Error cancelling RSVP: {e}")
        return jsonify({"error": "Error cancelling RSVP"}), 500
    finally:
        cursor.close()

# Get student invitations
@student_routes.route('/students/<student_id>/invitations', methods=['GET'])
def get_student_invitations(student_id):
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                ei.invitationID as invitation_id,
                ei.eventID as event_id,
                e.name as event_name,
                e.startDateTime as start_datetime,
                ei.senderStudentID as sender_student_id,
                s.firstName AS sender_first_name,
                s.lastName AS sender_last_name,
                ei.status as invitation_status,
                ei.sentAt as sent_datetime
            FROM Event_Invitations ei
            JOIN Events e ON ei.eventID = e.eventID
            JOIN Students s ON ei.senderStudentID = s.studentID
            WHERE ei.recipientStudentID = %s
            ORDER BY ei.sentAt DESC
        """
        cursor.execute(query, (student_id,))
        invitations = cursor.fetchall()
        return jsonify(invitations), 200
    except Error as e:
        current_app.logger.error(f"Error fetching invitations: {e}")
        return jsonify({"error": "Error fetching invitations"}), 500
    finally:
        cursor.close()

# Get student invitations (sent + received)
@student_routes.route('/students/<student_id>/invitations/all', methods=['GET'])
def get_all_student_invitations(student_id):
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT 
                ei.invitationID AS invitation_id,
                ei.eventID AS event_id,
                e.name AS event_name,
                e.startDateTime AS start_datetime,
                ei.senderStudentID AS sender_student_id,
                ei.recipientStudentID AS recipient_student_id,
                s.firstName AS sender_first_name,
                s.lastName AS sender_last_name,
                ei.status AS invitation_status,
                ei.sentAt AS sent_datetime
            FROM Event_Invitations ei
            JOIN Events e ON ei.eventID = e.eventID
            JOIN Students s ON ei.senderStudentID = s.studentID
            WHERE ei.senderStudentID = %s
               OR ei.recipientStudentID = %s
            ORDER BY ei.sentAt DESC
        """
        cursor.execute(query, (student_id, student_id))
        invitations = cursor.fetchall()
        return jsonify(invitations), 200
    except Error as e:
        current_app.logger.error(f"Error fetching all invitations: {e}")
        return jsonify({"error": "Error fetching invitations"}), 500
    finally:
        cursor.close()

# Update invitation status
@student_routes.route('/students/<student_id>/invitations/<int:invitation_id>', methods=['PUT'])
def update_invitation_status(student_id, invitation_id):
    try:
        data = request.get_json()
        cursor = db.cursor(dictionary=True)
        query = """
            UPDATE Event_Invitations 
            SET status = %s
            WHERE invitationID = %s
              AND recipientStudentID = %s
        """
        cursor.execute(query, (data['status'], invitation_id, student_id))
        db.commit()

        if cursor.rowcount > 0:
            return jsonify({"message": "Invitation status updated successfully"}), 200
        else:
            return jsonify({"error": "Invitation not found"}), 404

    except Error as e:
        current_app.logger.error(f"Error updating invitation: {e}")
        return jsonify({"error": "Error updating invitation"}), 500
    finally:
        cursor.close()