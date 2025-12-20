# models/timetable_model.py
from utils.db import engine
from sqlalchemy import text

class TimetableModel:

    @staticmethod
    def get_all():
        with engine.connect() as conn:
            q = text("""
                    SELECT * FROM timetable
                    ORDER BY class_date, start_time
            """)

            return conn.execute(q).fetchall()


    @staticmethod
    def create(day, class_date, start_time, end_time, subject, instructor, location):
        with engine.connect() as conn:
            q = text("""
                INSERT INTO timetable 
                (day, class_date, start_time, end_time, subject, instructor, location)
                VALUES (:day, :class_date, :start_time, :end_time, :subject, :instructor, :location)
            """)
            conn.execute(q, {
                "day": day,
                "class_date": class_date,
                "start_time": start_time,
                "end_time": end_time,
                "subject": subject,
                "instructor": instructor,
                "location": location
            })
            conn.commit()

    @staticmethod
    def has_time_clash(class_date, start_time, end_time, exclude_id=None):
        with engine.connect() as conn:
            query = """
                SELECT COUNT(*) FROM timetable
                WHERE class_date = :class_date
                AND start_time < :end_time
                AND end_time > :start_time
            """

            params = {
                "class_date": class_date,
                "start_time": start_time,
                "end_time": end_time
            }

            # Used during EDIT (exclude current row)
            if exclude_id:
                query += " AND id != :id"
                params["id"] = exclude_id

            result = conn.execute(text(query), params).scalar()
            return result > 0



    @staticmethod
    def delete(tid):
        with engine.connect() as conn:
            q = text("DELETE FROM timetable WHERE id = :id")
            conn.execute(q, {"id": tid})
            conn.commit()

    @staticmethod
    def update(tid, day, class_date, start_time, end_time, subject, instructor, location):
        with engine.connect() as conn:
            q = text("""
                UPDATE timetable
                SET day = :day,
                    class_date = :class_date,
                    start_time = :start_time,
                    end_time = :end_time,
                    subject = :subject,
                    instructor = :instructor,
                    location = :location
                WHERE id = :id
            """)
            conn.execute(q, {
                "id": tid,
                "day": day,
                "class_date": class_date,
                "start_time": start_time,
                "end_time": end_time,
                "subject": subject,
                "instructor": instructor,
                "location": location
            })
            conn.commit()
        
        

    @staticmethod
    def count():
        with engine.connect() as conn:
            q = text("SELECT COUNT(*) FROM timetable")
            return conn.execute(q).scalar()

    @staticmethod
    def get_by_id(tid):
        with engine.connect() as conn:
            q = text("SELECT * FROM timetable WHERE id = :id")
            return conn.execute(q, {"id": tid}).fetchone()
