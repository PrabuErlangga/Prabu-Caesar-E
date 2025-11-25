from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from .database import init_db, get_session
from .models import MahasiswaCreate, MahasiswaRead, MahasiswaUpdate
from . import crud

app = FastAPI(title="CRUD Mahasiswa API")

# ---------- CORS: untuk development, gunakan ["*"]. Ganti ke origin spesifik di production ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # <-- ubah ke ["http://localhost:5173"] jika mau lebih ketat
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"message": "CRUD Mahasiswa API — gunakan /docs untuk dokumentasi atau /mahasiswa/ untuk operasi CRUD."}

@app.post("/mahasiswa/", response_model=MahasiswaRead)
def create_mahasiswa_endpoint(payload: MahasiswaCreate, session: Session = Depends(get_session)):
    return crud.create_mahasiswa(session, payload)

@app.get("/mahasiswa/", response_model=list[MahasiswaRead])
def list_mahasiswa(session: Session = Depends(get_session)):
    return crud.get_all_mahasiswa(session)

@app.get("/mahasiswa/{id}", response_model=MahasiswaRead)
def get_mahasiswa_endpoint(id: int, session: Session = Depends(get_session)):
    m = crud.get_mahasiswa(session, id)
    if not m:
        raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")
    return m

@app.put("/mahasiswa/{id}", response_model=MahasiswaRead)
def update_mahasiswa_endpoint(id: int, payload: MahasiswaUpdate, session: Session = Depends(get_session)):
    m = crud.update_mahasiswa(session, id, payload)
    if not m:
        raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")
    return m

@app.delete("/mahasiswa/{id}")
def delete_mahasiswa_endpoint(id: int, session: Session = Depends(get_session)):
    ok = crud.delete_mahasiswa(session, id)
    if not ok:
        raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")
    return {"ok": True}
