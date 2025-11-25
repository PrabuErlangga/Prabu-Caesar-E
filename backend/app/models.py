from typing import Optional
from sqlmodel import SQLModel, Field

class MahasiswaBase(SQLModel):
    nim: str
    nama: str
    jurusan: Optional[str] = None
    angkatan: Optional[int] = None

class Mahasiswa(MahasiswaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class MahasiswaCreate(MahasiswaBase):
    pass

class MahasiswaRead(MahasiswaBase):
    id: int

class MahasiswaUpdate(SQLModel):
    nama: Optional[str] = None
    jurusan: Optional[str] = None
    angkatan: Optional[int] = None
