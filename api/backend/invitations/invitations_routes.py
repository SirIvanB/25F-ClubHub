from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app

invitation_routes = Blueprint("invitation_routes", __name__)

@invitation_routes.route("/invitations", methods=["POST"])
def send_invitation():
    """
    Send event invitation to another student.
    Expects JSON body with: event_id, sender_student_id, recipient_student_id
    """
    try:
        data = request.get_json()
        required_fields = ["event_id", "sender_student_id", "recipient_student_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        cursor = db.cursor(dictionary=True)
        query = """
            INSERT INTO event_invitations (
                invitation_id,
                event_id,
                sender_student_id,
                recipient_student_id,
                invitation_status,
                sent_datetime
            )
            VALUES (
                UUID(),
                %s,
                %s,
                %s,
                'pending',
                CURRENT_TIMESTAMP
            )
        """
        cursor.execute(
            query,
            (
                data["event_id"],
                data["sender_student_id"],
                data["recipient_student_id"],
            ),
        )
        db.commit()

        return jsonify(
            {
                "message": "Invitation sent successfully",
                "invitation_id": cursor.lastrowid,  # or just return 201 without id if UUID
            }
        ), 201

    except Error as e:
        current_app.logger.error(f"Error sending invitation: {e}")
        return jsonify({"error": "Error sending invitation"}), 500
    finally:
        cursor.close()