from flask import Blueprint, jsonify, request
from backend.db_connection import db
from mysql.connector import Error
from flask import current_app
from pymysql.cursors import DictCursor

# Create a Blueprint for Events routes
events = Blueprint("events", __name__)

# GET /events - Return all upcoming events [Ruth-1]
@events.route("/events", methods=["GET"])
def get_all_events():
    """Return all upcoming events with info, ordered by date"""
    try:
        cursor = db.cursor(dictionary=True)

        query = """
        SELECT
            e.eventID,
            e.name,
            e.description,
            e.startDateTime,
            e.endDateTime,
            e.location,
            e.buildingName,
            e.roomNumber,
            e.capacity,
            c.name AS club_name,
            c.clubID,
            c.type AS club_type
        FROM Events e
        JOIN Clubs c ON e.clubID = c.clubID
        WHERE e.startDateTime >= CURRENT_TIMESTAMP
        ORDER BY e.startDateTime ASC
        """

        cursor.execute(query)
        events_list = cursor.fetchall()
        return jsonify(events_list), 200
    except Error as e:
        current_app.logger.error(f'Error in get_all_events: {str(e)}')
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()


# POST /events - Create and publish events [Sofia-1]
@events.route("/events", methods=["POST"])
def create_event():
    """Create and publish events to ClubHub"""
    cursor = None
    try:
        data = request.get_json()

        required_fields = ["name", "startDateTime", "clubID"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        cursor = db.cursor(dictionary=True)

        query = """
        INSERT INTO Events
        (name, description, startDateTime, endDateTime, location, capacity, clubID, eventType)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            data["name"],
            data.get("description"),
            data["startDateTime"],
            data.get("endDateTime"),
            data.get("location"),
            data.get("capacity"),
            data["clubID"],
            data.get("eventType")
        ))

        db.commit()
        event_id = cursor.lastrowid

        return jsonify({"message": "Event created successfully", "event_id": event_id}), 201
    except Error as e:
        current_app.logger.error(f'Error in create_event: {str(e)}')
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()


# GET /events/{id} - Returns info on a particular event [Ruth-4]
@events.route("/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    """Returns all information on a particular event"""
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)

        query = """
        SELECT
            e.*,
            c.name AS club_name,
            c.email AS club_email
        FROM Events e
        JOIN Clubs c ON e.clubID = c.clubID
        WHERE e.eventID = %s
        """

        cursor.execute(query, (event_id,))
        event = cursor.fetchone()
        cursor.close()

        if not event:
            return jsonify({"error": "Event not found"}), 404

        return jsonify(event), 200
    except Error as e:
        current_app.logger.error(f'Error in get_event: {str(e)}')
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()


# GET /events/{id}/rsvps - Return RSVP summary [Sofia-2]
@events.route("/events/<int:event_id>/rsvps", methods=["GET"])
def get_event_rsvps(event_id):
    """Return the RSVP summary for an event"""
    try:
        cursor = db.cursor(dictionary=True)

        query = """
        SELECT
            COUNT(*) as total_rsvps,
            SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
            SUM(CASE WHEN status = 'waitlisted' THEN 1 ELSE 0 END) as waitlisted,
            e.capacity,
            (e.capacity - COUNT(*)) as remaining_capacity
        FROM RSVPs r
        JOIN Events e ON r.eventID = e.eventID
        WHERE r.eventID = %s
        GROUP BY e.capacity
        """

        cursor.execute(query, (event_id,))
        summary = cursor.fetchone()
        cursor.close()

        if not summary:
            return jsonify({"total_rsvps": 0, "confirmed": 0, "waitlisted": 0}), 200

        return jsonify(summary), 200
    except Error as e:
        current_app.logger.error(f'Error in get_event_rsvps: {str(e)}')
        return jsonify({"error": str(e)}), 500


# GET /events/{id}/attendance - Return attendance records [Sofia-3]
@events.route("/events/<int:event_id>/attendance", methods=["GET"])
def get_event_attendance(event_id):
    """Return attendance records for a particular event"""
    try:
        cursor = db.cursor(dictionary=True)

        query = """
        SELECT
            sea.attendanceID,
            sea.studentID,
            s.firstName,
            s.lastName,
            s.email,
            sea.timestamp as check_in_time
        FROM Students_Event_Attendees sea
        JOIN Students s ON sea.studentID = s.studentID
        WHERE sea.eventID = %s
        ORDER BY sea.timestamp DESC
        """

        cursor.execute(query, (event_id,))
        attendance = cursor.fetchall()
        return jsonify(attendance), 200
    except Error as e:
        current_app.logger.error(f'Error in get_event_attendance: {str(e)}')
        return jsonify({"error": str(e)}), 500


# POST /events/{id}/attendance - Check in a student [Sofia-3]
@events.route("/events/<int:event_id>/attendance", methods=["POST"])
def check_in_student(event_id):
    """Check in a student digitally"""
    try:
        data = request.get_json()

        if "student_id" not in data:
            return jsonify({"error": "student_id is required"}), 400

        cursor = db.cursor(dictionary=True)

        query = """
        INSERT INTO Students_Event_Attendees (studentID, eventID, timestamp, status)
        VALUES (%s, %s, CURRENT_TIMESTAMP, 'present')
        """

        cursor.execute(query, (data["student_id"], event_id))
        db.commit()
        attendance_id = cursor.lastrowid
        return jsonify({"message": "Check-in successful", "attendance_id": attendance_id}), 201
    except Error as e:
        current_app.logger.error(f'Error in check_in_student: {str(e)}')
        return jsonify({"error": str(e)}), 500


# GET /events/{id}/keywords - Return keywords with search frequency [Marcus-4]
@events.route("/events/<int:event_id>/keywords", methods=["GET"])
def get_event_keywords(event_id):
    """Return keywords associated with an event, along with their search frequency"""
    try:
        cursor = db.cursor(dictionary=True)

        query = """
        SELECT
            k.keywordID,
            k.keyword,
            COUNT(sl.searchLogID) as search_count
        FROM Events_Event_Keywords eek
        JOIN Keywords k ON eek.keywordID = k.keywordID
        LEFT JOIN Search_Logs sl ON sl.searchQuery LIKE CONCAT('%%', k.keyword, '%%')
        WHERE eek.eventID = %s
        GROUP BY k.keywordID, k.keyword
        ORDER BY search_count DESC
        """

        cursor.execute(query, (event_id,))
        keywords = cursor.fetchall()
        return jsonify(keywords), 200
    except Error as e:
        current_app.logger.error(f'Error in get_event_keywords: {str(e)}')
        return jsonify({"error": str(e)}), 500


# POST /events/{id}/keywords - Add new keywords [Marcus-4]
@events.route("/events/<int:event_id>/keywords", methods=["POST"])
def add_event_keyword(event_id):
    """Add new keywords to events"""
    try:
        data = request.get_json()

        if "keyword" not in data:
            return jsonify({"error": "keyword is required"}), 400

        cursor = db.cursor(dictionary=True)

        # First, insert keyword if it doesn't exist
        cursor.execute("INSERT IGNORE INTO Keywords (keyword) VALUES (%s)", (data["keyword"],))
        cursor.execute("SELECT keywordID FROM Keywords WHERE keyword = %s", (data["keyword"],))
        keyword_id = cursor.fetchone()["keywordID"]

        # Then associate it with the event
        cursor.execute(
            "INSERT IGNORE INTO Events_Event_Keywords (eventID, keywordID) VALUES (%s, %s)",
            (event_id, keyword_id)
        )

        db.commit()
        return jsonify({"message": "Keyword added successfully"}), 201
    except Error as e:
        current_app.logger.error(f'Error in add_event_keyword: {str(e)}')
        return jsonify({"error": str(e)}), 500


# PUT /events/{id}/keywords - Update keywords [Marcus-4]
@events.route("/events/<int:event_id>/keywords", methods=["PUT"])
def update_event_keywords(event_id):
    """Update keywords for events"""
    try:
        data = request.get_json()

        if "keywords" not in data or not isinstance(data["keywords"], list):
            return jsonify({"error": "keywords array is required"}), 400

        cursor = db.cursor(dictionary=True)

        # Delete existing keywords for this event
        cursor.execute("DELETE FROM Events_Event_Keywords WHERE eventID = %s", (event_id,))

        # Add new keywords
        for keyword in data["keywords"]:
            cursor.execute("INSERT IGNORE INTO Keywords (keyword) VALUES (%s)", (keyword,))
            cursor.execute("SELECT keywordID FROM Keywords WHERE keyword = %s", (keyword,))
            keyword_id = cursor.fetchone()["keywordID"]
            cursor.execute(
                "INSERT INTO Events_Event_Keywords (eventID, keywordID) VALUES (%s, %s)",
                (event_id, keyword_id)
            )

        db.commit()
        return jsonify({"message": "Keywords updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f'Error in update_event_keywords: {str(e)}')
        return jsonify({"error": str(e)}), 500


# DELETE /events/{id}/keywords - Remove keywords [Marcus-4]
@events.route("/events/<int:event_id>/keywords", methods=["DELETE"])
def delete_event_keyword(event_id):
    """Remove keywords from events"""
    try:
        keyword_id = request.args.get("keyword_id")

        if not keyword_id:
            return jsonify({"error": "keyword_id query parameter is required"}), 400

        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "DELETE FROM Events_Event_Keywords WHERE eventID = %s AND keywordID = %s",
            (event_id, keyword_id)
        )

        db.commit()
        rows_affected = cursor.rowcount
        cursor.close()

        if rows_affected == 0:
            return jsonify({"error": "Keyword not found for this event"}), 404

        return jsonify({"message": "Keyword removed successfully"}), 200
    except Error as e:
        current_app.logger.error(f'Error in delete_event_keyword: {str(e)}')
        return jsonify({"error": str(e)}), 500


# GET /events/conflicts - Return events that conflict [Sofia-4]
@events.route("/events/conflicts", methods=["GET"])
def get_event_conflicts():
    """Return events that conflict with each other"""
    try:
        cursor = db.cursor(dictionary=True)

        query = """
        SELECT
            e1.eventID as event1_id,
            e1.name as event1_name,
            e1.startDateTime as event1_start,
            e1.endDateTime as event1_end,
            e2.eventID as event2_id,
            e2.name as event2_name,
            e2.startDateTime as event2_start,
            e2.endDateTime as event2_end
        FROM Events e1
        JOIN Events e2 ON e1.eventID < e2.eventID
        WHERE e1.startDateTime < e2.endDateTime
        AND e1.endDateTime > e2.startDateTime
        AND e1.startDateTime >= CURRENT_TIMESTAMP
        ORDER BY e1.startDateTime
        """

        cursor.execute(query)
        conflicts = cursor.fetchall()
        return jsonify(conflicts), 200
    except Error as e:
        current_app.logger.error(f'Error in get_event_conflicts: {str(e)}')
        return jsonify({"error": str(e)}), 500


# GET /events/validation - Return recent events with validation status [David-4]
@events.route("/events/validation", methods=["GET"])
def get_event_validation():
    """Return recent events with validation status and errors"""
    try:
        cursor = db.cursor(dictionary=True)

        query = """
        SELECT
            e.eventID,
            e.name,
            e.clubID,
            e.startDateTime,
            CASE
                WHEN e.name IS NULL OR e.name = '' THEN 'Missing event name'
                WHEN e.startDateTime IS NULL THEN 'Missing start datetime'
                WHEN e.startDateTime >= e.endDateTime THEN 'Invalid datetime range'
                WHEN e.capacity < 0 THEN 'Invalid capacity'
                ELSE 'Valid'
            END AS validation_status
        FROM Events e
        WHERE e.startDateTime >= DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 HOUR)
        ORDER BY e.startDateTime DESC
        """

        cursor.execute(query)
        validation_results = cursor.fetchall()
        return jsonify(validation_results), 200
    except Error as e:
        current_app.logger.error(f'Error in get_event_validation: {str(e)}')
        return jsonify({"error": str(e)}), 500
