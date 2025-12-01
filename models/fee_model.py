# models/fee_model.py
from utils.db import engine
from sqlalchemy import text

class FeeModel:

    @staticmethod
    def get_all():
        with engine.connect() as conn:
            q = text("SELECT * FROM fees")
            return conn.execute(q).fetchall()

    @staticmethod
    def get_by_roll(roll):
        with engine.connect() as conn:
            q = text("SELECT * FROM fees WHERE roll = :roll")
            return conn.execute(q, {"roll": roll}).fetchone()

    @staticmethod
    def create(roll, semester, amount_due, amount_paid, due_date):
        with engine.connect() as conn:
            q = text("""
                INSERT INTO fees (roll, semester, amount_due, amount_paid, due_date)
                VALUES (:roll, :semester, :amount_due, :amount_paid, :due_date)
            """)
            conn.execute(q, {
                "roll": roll,
                "semester": int(semester or 1),
                "amount_due": float(amount_due or 0),
                "amount_paid": float(amount_paid or 0),
                "due_date": due_date
            })
            conn.commit()

    @staticmethod
    def delete(fid):
        with engine.connect() as conn:
            q = text("DELETE FROM fees WHERE id = :id")
            conn.execute(q, {"id": fid})
            conn.commit()

    @staticmethod
    def count():
        with engine.connect() as conn:
            q = text("SELECT COUNT(*) FROM fees")
            return conn.execute(q).scalar()
