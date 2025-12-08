from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

invitation_routes = Blueprint("invitation_routes", __name__)

@invitation_routes.route("/invitations", methods=["POST"])
def create_invitation():
    try:
        data = request.get_json()
        event_id = data.get("event_id")
        sender_id = data.get("sender_student_id")
        recipient_id = data.get("recipient_student_id")

        cursor = db.cursor(dictionary=True)

        # INSERT using correct column names
        insert_query = """
            INSERT INTO Event_Invitations
                (eventID, senderStudentID, recipientStudentID, status, sentAt)
            VALUES (%s, %s, %s, 'pending', CURRENT_TIMESTAMP)
        """
        cursor.execute(insert_query, (event_id, sender_id, recipient_id))
        db.commit()

        new_id = cursor.lastrowid

        # (Optional but nice) return the created invitation row
        select_query = """
            SELECT
                ei.invitationID       AS invitation_id,
                ei.eventID            AS event_id,
                ei.senderStudentID    AS sender_student_id,
                ei.recipientStudentID AS recipient_student_id,
                ei.status             AS invitation_status,
                ei.sentAt             AS sent_datetime
            FROM Event_Invitations ei
            WHERE ei.invitationID = %s
        """
        cursor.execute(select_query, (new_id,))
        invitation = cursor.fetchone()

        return jsonify(invitation), 201

    except Error as e:
        current_app.logger.error(f"Error creating invitation: {e}")
        return jsonify({"error": "Error creating invitation"}), 500
    finally:
        cursor.close()