# models/timetable_model.py
from utils.db import engine
from sqlalchemy import text

class TimetableModel:

    @staticmethod
    def get_all():
        with engine.connect() as conn:
            q = text("""
                SELECT * FROM timetable
                ORDER BY FIELD(day, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'),
                         start_time
            """)
            return conn.execute(q).fetchall()


    @staticmethod
    def create(day, start_time, end_time, subject, instructor, location):
        with engine.connect() as conn:
            q = text("""
                INSERT INTO timetable (day, start_time, end_time, subject, instructor, location)
                VALUES (:day, :start_time, :end_time, :subject, :instructor, :location)
            """)
            conn.execute(q, {
                "day": day,
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
