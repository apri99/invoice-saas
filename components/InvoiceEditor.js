'use client'
import { useState, useEffect } from 'react'
import jsPDF from 'jspdf'
import { Download, Coffee, Receipt, Plus, Trash2, Moon, Sun, Eye, MessageCircle, CreditCard } from 'lucide-react'

export default function InvoiceEditor() {
  const [items, setItems] = useState([{ desc: '', qty: 1, price: 0 }])
  const [client, setClient] = useState('')
  const [clientPhone, setClientPhone] = useState('')
  const [bankInfo, setBankInfo] = useState('')
  const [note, setNote] = useState('Terima kasih atas kepercayaan Anda!')
  const [darkMode, setDarkMode] = useState(false)

  useEffect(() => {
    const saved = {
      items: localStorage.getItem('inv_items'),
      client: localStorage.getItem('inv_client'),
      bank: localStorage.getItem('inv_bank'),
      note: localStorage.getItem('inv_note')
    }
    if (saved.items) setItems(JSON.parse(saved.items))
    if (saved.client) setClient(saved.client)
    if (saved.bank) setBankInfo(saved.bank)
    if (saved.note) setNote(saved.note)
  }, [])

  useEffect(() => {
    localStorage.setItem('inv_items', JSON.stringify(items))
    localStorage.setItem('inv_client', client)
    localStorage.setItem('inv_bank', bankInfo)
    localStorage.setItem('inv_note', note)
  }, [items, client, bankInfo, note])

  const total = items.reduce((sum, item) => sum + (Number(item.qty) * Number(item.price)), 0)

  const generatePDF = () => {
    const doc = new jsPDF()
    doc.setFont("helvetica", "bold"); doc.text('INVOICE', 105, 20, {align: 'center'})
    
    doc.setFontSize(10); doc.setFont("helvetica", "normal")
    doc.text(Kepada: \, 20, 40)
    
    let y = 60
    doc.setFont("helvetica", "bold"); doc.text('Deskripsi', 20, y); doc.text('Total', 160, y)
    doc.line(20, y+2, 190, y+2)
    
    y += 10
    doc.setFont("helvetica", "normal")
    items.forEach((item, i) => {
      doc.text(\ (x\), 20, y)
      doc.text(Rp \, 160, y)
      y += 8
    })
    
    doc.line(20, y, 190, y)
    doc.setFont("helvetica", "bold"); doc.text(TOTAL BAYAR: Rp \, 190, y + 10, {align: 'right'})
    
    y += 30
    doc.setFontSize(10)
    doc.text('PEMBAYARAN VIA:', 20, y)
    doc.setFont("helvetica", "normal"); doc.text(bankInfo, 20, y + 5)
    
    doc.setFont("helvetica", "italic"); doc.text(note, 105, y + 25, {align: 'center'})
    doc.save(Invoice-\.pdf)
  }

  return (
    <div className={\ min-h-screen transition-all pb-20 font-sans}>
      <nav className="flex justify-between items-center p-6 max-w-6xl mx-auto">
        <div className="flex items-center gap-2 text-2xl font-black text-indigo-500 italic"><Receipt /> QUICK-INV</div>
        <div className="flex gap-3">
          <button onClick={() => setDarkMode(!darkMode)} className="p-2 rounded-xl bg-slate-200 dark:bg-slate-700 text-amber-500 transition-transform active:scale-90">
            {darkMode ? <Sun size={20}/> : <Moon size={20}/>}
          </button>
          <a href="https://saweria.co/apri99" target="_blank" className="bg-orange-500 text-white px-5 py-2 rounded-xl text-sm font-bold flex items-center gap-2 shadow-lg">
            <Coffee size={18} /> Kopi
          </a>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 px-6">
        {/* PANEL INPUT */}
        <div className={lg:col-span-7 p-8 rounded-3xl shadow-xl \ border}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <input type="text" value={client} placeholder="Nama Pelanggan" className="p-4 border-2 rounded-2xl bg-transparent outline-none focus:border-indigo-500" onChange={(e) => setClient(e.target.value)} />
            <input type="text" value={clientPhone} placeholder="WA (0812...)" className="p-4 border-2 rounded-2xl bg-transparent outline-none focus:border-indigo-500" onChange={(e) => setClientPhone(e.target.value)} />
          </div>

          <div className="space-y-4 mb-8">
            {items.map((item, index) => (
              <div key={index} className="flex gap-2">
                <input type="text" value={item.desc} placeholder="Item" className="flex-1 p-2 border-b-2 bg-transparent outline-none" onChange={(e) => { const n = [...items]; n[index].desc = e.target.value; setItems(n); }} />
                <input type="number" value={item.price} placeholder="Harga" className="w-32 p-2 border-b-2 bg-transparent outline-none text-right" onChange={(e) => { const n = [...items]; n[index].price = e.target.value; setItems(n); }} />
                <button onClick={() => setItems(items.filter((_, i) => i !== index))} className="text-red-400 p-2"><Trash2 size={18}/></button>
              </div>
            ))}
            <button onClick={() => setItems([...items, {desc:'', qty:1, price:0}])} className="text-indigo-500 font-bold text-sm">+ TAMBAH ITEM</button>
          </div>

          <div className="space-y-4 border-t pt-6">
            <div className="flex items-center gap-2 text-indigo-500 font-bold mb-2"><CreditCard size={18}/> Informasi Pembayaran</div>
            <textarea value={bankInfo} placeholder="Contoh: BCA 1234567 a/n Apri" className="w-full p-4 border-2 rounded-2xl bg-transparent h-20 outline-none focus:border-indigo-500" onChange={(e) => setBankInfo(e.target.value)} />
            <input type="text" value={note} placeholder="Catatan (Terima kasih...)" className="w-full p-4 border-2 rounded-2xl bg-transparent outline-none focus:border-indigo-500" onChange={(e) => setNote(e.target.value)} />
          </div>
        </div>

        {/* PANEL AKSI */}
        <div className="lg:col-span-5 space-y-6">
          <div className={p-8 rounded-3xl text-center shadow-xl \ border}>
            <div className="text-sm uppercase tracking-widest text-indigo-400 font-bold mb-2">Total Tagihan</div>
            <div className="text-4xl font-black text-indigo-600 mb-8">Rp {total.toLocaleString('id-ID')}</div>
            <button onClick={generatePDF} className="w-full bg-indigo-600 text-white py-4 rounded-2xl font-bold flex justify-center items-center gap-3 shadow-xl hover:bg-indigo-700 transition-all mb-4">
              <Download /> DOWNLOAD PDF
            </button>
            <button onClick={() => window.open(https://wa.me/\?text=Halo \, tagihan Anda Rp \, '_blank')} className="w-full bg-green-500 text-white py-4 rounded-2xl font-bold flex justify-center items-center gap-3 shadow-lg hover:bg-green-600 transition-all">
              <MessageCircle /> TAGIH WHATSAPP
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
