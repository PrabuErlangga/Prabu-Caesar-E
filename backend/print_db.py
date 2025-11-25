from sqlmodel import Session, select, create_engine
from app.models import Mahasiswa
import os

DB = os.getenv("DATABASE_URL", "sqlite:///./mahasiswa.db")
engine = create_engine(DB, echo=False)

def list_students():
    with Session(engine) as session:
        students = session.exec(select(Mahasiswa)).all()
        if not students:
            print("No students found in database.")
        for s in students:
            print(s.id, s.nim, s.nama, s.jurusan, s.angkatan)

if __name__ == "__main__":
    list_students()
