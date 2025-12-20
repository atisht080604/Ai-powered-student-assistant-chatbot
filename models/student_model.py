# models/student_model.py
from utils.db import engine
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


class StudentModel:

    @staticmethod
    def get_by_roll(roll):
        with engine.connect() as conn:
            q = text("SELECT * FROM students WHERE roll = :roll")
            return conn.execute(q, {"roll": roll}).fetchone()


    @staticmethod
    def get_all():
        with engine.connect() as conn:
            q = text("SELECT id, roll, name, department, year, attendance, email FROM students")
            return conn.execute(q).fetchall()


    @staticmethod
    def create(roll, name, department, year, email, password, attendance=0):        
        try:
            with engine.connect() as conn:
                q = text("""
                    INSERT INTO students (roll, name, department, year, attendance, email, password)
                    VALUES (:roll, :name, :department, :year, :attendance, :email, :password)
                """)
                conn.execute(q, {
                    "roll": roll,
                    "name": name,
                    "department": department,
                    "year": int(year or 1),
                    "attendance": float(attendance or 0),
                    "email": email,
                    "password": password
                })
                conn.commit()
            return True

        except IntegrityError:
            return False


    @staticmethod
    def delete(student_id):
        with engine.connect() as conn:
            q = text("DELETE FROM students WHERE id = :id")
            conn.execute(q, {"id": student_id})
            conn.commit()


    @staticmethod
    def count():
        with engine.connect() as conn:
            q = text("SELECT COUNT(*) FROM students")
            return conn.execute(q).scalar()

    @staticmethod
    def get_by_email(email):
        with engine.connect() as conn:
            q = text("SELECT * FROM students WHERE email = :email")
            return conn.execute(q, {"email": email}).fetchone()

    @staticmethod
    def update_password(email, new_password):
        with engine.connect() as conn:
            q = text("UPDATE students SET password = :p WHERE email = :email")
            conn.execute(q, {"p": new_password, "email": email})
            conn.commit()
    @staticmethod
    def update_profile(roll, name, year, email=None):
        query = text("""
            UPDATE students 
            SET name = :name,
                year = :year
            WHERE roll = :roll
        """)
        with engine.connect() as conn:
            conn.execute(query, {"roll": roll, "name": name, "year": year})
            conn.commit()

    @staticmethod
    def update_email(roll, new_email):
        query = text("UPDATE students SET email = :email WHERE roll = :roll")
        with engine.connect() as conn:
            conn.execute(query, {"email": new_email, "roll": roll})
            conn.commit()
