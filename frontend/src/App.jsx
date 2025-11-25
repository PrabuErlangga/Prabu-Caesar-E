import React, { useEffect, useState } from 'react'

export default function App(){
  const [list, setList] = useState([])
  const [form, setForm] = useState({ nim:'', nama:'', jurusan:'', angkatan:'' })
  const [editing, setEditing] = useState(null)
  const [loading, setLoading] = useState(false)

  const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  useEffect(()=>{ fetchAll() }, [])

  async function fetchAll(){
    try {
      setLoading(true)
      const res = await fetch(`${API}/mahasiswa/`)
      if(!res.ok) throw new Error('Failed to fetch list: ' + res.status)
      const data = await res.json()
      setList(data)
    } catch (err){
      console.error('fetchAll error', err)
      alert('Error memuat data: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  async function submit(e){
    e.preventDefault()
    try {
      const payload = {
        nim: form.nim,
        nama: form.nama,
        jurusan: form.jurusan || undefined,
        angkatan: form.angkatan ? Number(form.angkatan) : undefined
      }

      const url = editing ? `${API}/mahasiswa/${editing}` : `${API}/mahasiswa/`
      const method = editing ? 'PUT' : 'POST'

      const res = await fetch(url, {
        method,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      })

      if (!res.ok) {
        const err = await res.json().catch(()=>({detail: 'No JSON response'}))
        alert('Server error: ' + (err.detail || JSON.stringify(err)))
        return
      }

      const saved = await res.json().catch(()=>null)
      if (!saved) {
        alert('Server tidak mengembalikan data yang valid.')
        return
      }

      // refresh list from server
      await fetchAll()

      setForm({ nim:'', nama:'', jurusan:'', angkatan:'' })
      setEditing(null)
    } catch (err) {
      alert('Fetch error: ' + err.message)
    }
  }

  async function remove(id){
    if(!confirm('Hapus data?')) return
    try {
      const res = await fetch(`${API}/mahasiswa/${id}`, { method:'DELETE' })
      if(!res.ok) {
        const err = await res.json().catch(()=>({detail:'no json'}))
        alert('Gagal hapus: ' + (err.detail || JSON.stringify(err)))
        return
      }
      await fetchAll()
    } catch (err) {
      alert('Fetch error: ' + err.message)
    }
  }

  function startEdit(m){
    setEditing(m.id)
    setForm({ nim:m.nim, nama:m.nama, jurusan:m.jurusan || '', angkatan:m.angkatan || '' })
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">CRUD Mahasiswa</h1>
      <form onSubmit={submit} className="space-y-2 mb-6">
        <input placeholder="NIM" value={form.nim} onChange={e=>setForm({...form,nim:e.target.value})} className="w-full p-2 border rounded" />
        <input placeholder="Nama" value={form.nama} onChange={e=>setForm({...form,nama:e.target.value})} className="w-full p-2 border rounded" />
        <input placeholder="Jurusan" value={form.jurusan} onChange={e=>setForm({...form,jurusan:e.target.value})} className="w-full p-2 border rounded" />
        <input placeholder="Angkatan" value={form.angkatan} onChange={e=>setForm({...form,angkatan:e.target.value})} className="w-full p-2 border rounded" />
        <div>
          <button className="px-4 py-2 bg-blue-600 text-white rounded mr-2">{editing? 'Update':'Tambah'}</button>
          {editing && <button type="button" onClick={()=>{setEditing(null); setForm({nim:'',nama:'',jurusan:'',angkatan:''})}} className="px-4 py-2 border rounded">Batal</button>}
        </div>
      </form>

      {loading ? <div>Loading...</div> : null}

      <table className="w-full table-auto">
        <thead>
          <tr className="text-left">
            <th>NIM</th><th>Nama</th><th>Jurusan</th><th>Angkatan</th><th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          {list.map(m=> (
            <tr key={m.id}>
              <td>{m.nim}</td>
              <td>{m.nama}</td>
              <td>{m.jurusan}</td>
              <td>{m.angkatan}</td>
              <td>
                <button onClick={()=>startEdit(m)} className="mr-2">Edit</button>
                <button onClick={()=>remove(m.id)}>Hapus</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
