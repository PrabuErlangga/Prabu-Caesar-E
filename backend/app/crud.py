from sqlmodel import Session, select
from .models import Mahasiswa, MahasiswaCreate, MahasiswaUpdate

def create_mahasiswa(session: Session, data: MahasiswaCreate) -> Mahasiswa:
    m = Mahasiswa.from_orm(data)
    session.add(m)
    session.commit()
    session.refresh(m)
    return m

def get_all_mahasiswa(session: Session):
    statement = select(Mahasiswa)
    return session.exec(statement).all()

def get_mahasiswa(session: Session, id: int):
    return session.get(Mahasiswa, id)

def update_mahasiswa(session: Session, id: int, data: MahasiswaUpdate):
    m = session.get(Mahasiswa, id)
    if not m:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(m, key, value)
    session.add(m)
    session.commit()
    session.refresh(m)
    return m

def delete_mahasiswa(session: Session, id: int):
    m = session.get(Mahasiswa, id)
    if not m:
        return False
    session.delete(m)
    session.commit()
    return True
