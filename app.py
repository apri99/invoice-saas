import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import io
import textwrap
from datetime import datetime

st.set_page_config(page_title="Invoice Pro v2.6", page_icon="🧾", layout="wide")

# --- SISTEM PROTEKSI MEMORI ---
if 'items' not in st.session_state:
    st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]

# Fungsi pengaman untuk menambah baris
def add_item():
    st.session_state.items.append({"desc": "", "price": 0, "qty": 1})

# Fungsi pengaman untuk menghapus baris
def delete_item(index):
    if len(st.session_state.items) > 1:
        st.session_state.items.pop(index)
    else:
        st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]

st.title("🚀 Invoice Generator Pro")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🖼️ Branding")
    uploaded_logo = st.file_uploader("Logo", type=["png", "jpg", "jpeg"])
    st.divider()
    st.header("👤 Pengirim")
    my_name = st.text_input("Nama Bisnis", value="CV. MAJU JAYA")
    my_email = st.text_input("Email", value="kontak@majusaja.com")
    my_phone = st.text_input("WhatsApp", value="08123456789")
    my_address = st.text_area("Alamat", value="Jl. Utama No. 1, Jakarta")
    
    st.divider()
    # TOMBOL SAKTI UNTUK MENGHILANGKAN WARNA MERAH
    if st.button("🚨 HAPUS SEMUA ERROR / RESET", use_container_width=True, type="secondary"):
        st.session_state.clear()
        st.rerun()

# --- MAIN CONTENT ---
col_in, col_pre = st.columns([1.5, 1])

with col_in:
    st.subheader("🏢 Data Penerima")
    r1, r2 = st.columns([2, 1])
    c_name = r1.text_input("Nama Klien")
    c_type = r2.selectbox("Tipe", ["Perusahaan", "Perorangan"])
    
    c_addr = st.text_area("Alamat Klien")
    
    st.divider()
    st.subheader("💰 Daftar Barang / Jasa")
    
    subtotal_val = 0
    
    # Memastikan data items adalah list yang valid
    if not isinstance(st.session_state.items, list):
        st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]

    # Loop input dengan pengaman unik
    for i in range(len(st.session_state.items)):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 1.5, 1, 0.5])
            
            # Gunakan try-except per baris agar jika satu error, yang lain tidak ikut merah
            try:
                d = c1.text_input(f"Item #{i+1}", value=st.session_state.items[i]['desc'], key=f"d_{i}")
                p = c2.number_input(f"Harga", value=int(st.session_state.items[i]['price']), step=1000, key=f"p_{i}")
                q = c3.number_input(f"Qty", value=int(st.session_state.items[i]['qty']), min_value=1, key=f"q_{i}")
                
                st.session_state.items[i] = {"desc": d, "price": p, "qty": q}
                line_total = p * q
                subtotal_val += line_total
                
                if c4.button("🗑️", key=f"del_{i}"):
                    delete_item(i)
                    st.rerun()
            except:
                st.error("Gagal memuat baris ini. Klik Reset di sidebar.")

    st.button("➕ Tambah Baris", on_click=add_item)

    st.divider()
    use_tax = st.checkbox("Gunakan Pajak (PPN 11%)")
    tax_v = (0.11 * subtotal_val) if use_tax else 0
    grand_total = subtotal_val + tax_v
    
    st.success(f"### Total Akhir: Rp {grand_total:,.0f}")
    notes = st.text_area("Catatan Pembayaran", value=f"Transfer BCA 123456789 A/N {my_name}")

# --- PDF ENGINE ---
def create_pdf(logo, s_name, s_email, s_phone, s_addr, c_name, c_addr, items, sub, t_amt, total, note):
    buf = io.BytesIO()
    pdf = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    
    # Header
    pdf.setFillColor(HexColor("#1f538d")); pdf.rect(0, h-100, w, 100, fill=True, stroke=False)
    pdf.setFillColor(HexColor("#ffffff"))
    pdf.setFont("Helvetica-Bold", 26); pdf.drawString(50, h-65, "INVOICE")
    
    # Content Table
    pdf.setFillColor(HexColor("#000000"))
    y = h-150
    pdf.setFont("Helvetica-Bold", 10); pdf.drawString(50, y, "DESKRIPSI"); pdf.drawRightString(w-50, y, "TOTAL")
    pdf.line(50, y-5, w-50, y-5); y -= 25
    
    pdf.setFont("Helvetica", 10)
    for it in items:
        pdf.drawString(50, y, it['desc'])
        pdf.drawRightString(w-50, y, f"{(it['price']*it['qty']):,.0f}")
        y -= 20
        
    y -= 20
    pdf.drawRightString(w-50, y, f"SUBTOTAL: Rp {sub:,.0f}")
    if t_amt > 0:
        y -= 15
        pdf.drawRightString(w-50, y, f"PAJAK 11%: Rp {t_amt:,.0f}")
    
    y -= 30
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawRightString(w-50, y, f"TOTAL AKHIR: Rp {total:,.0f}")
    
    pdf.save(); buf.seek(0)
    return buf

with col_pre:
    st.subheader("👀 Preview")
    with st.container(border=True):
        st.write(f"**Penerima:** {c_name}")
        st.write(f"**Total:** Rp {grand_total:,.0f}")
        
        if st.button("🚀 DOWNLOAD PDF", type="primary", use_container_width=True):
            pdf_res = create_pdf(uploaded_logo, my_name, my_email, my_phone, my_address, c_name, c_addr, st.session_state.items, subtotal_val, tax_v, grand_total, notes)
            st.download_button("⬇️ Simpan PDF", data=pdf_res, file_name=f"Invoice_{c_name}.pdf", use_container_width=True)
