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
    def delete(tid):
        with engine.connect() as conn:
            q = text("DELETE FROM timetable WHERE id = :id")
            conn.execute(q, {"id": tid})
            conn.commit()
        

    @staticmethod
    def count():
        with engine.connect() as conn:
            q = text("SELECT COUNT(*) FROM timetable")
            return conn.execute(q).scalar()
