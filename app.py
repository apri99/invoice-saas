import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import io
import textwrap
from datetime import datetime

st.set_page_config(page_title="Invoice Generator Pro v2.5", page_icon="🧾", layout="wide")

# --- INISIALISASI DATA (SESSION STATE) ---
if 'items' not in st.session_state:
    st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]

st.title("🚀 Invoice Generator Pro")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🖼️ Branding")
    uploaded_logo = st.file_uploader("Upload Logo", type=["png", "jpg", "jpeg"])
    st.divider()
    st.header("👤 Identitas Pengirim")
    my_name = st.text_input("Nama Bisnis", value="CV. MAJU JAYA")
    my_email = st.text_input("Email", value="kontak@majusaja.com")
    my_phone = st.text_input("WhatsApp", value="08123456789")
    my_address = st.text_area("Alamat Lengkap", value="Jl. Utama No. 1, Jakarta")
    
    st.divider()
    # Tombol Reset Total jika macet
    if st.button("🔄 Reset / Bersihkan Error", use_container_width=True):
        st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]
        st.rerun()

# --- MAIN CONTENT ---
col_in, col_pre = st.columns([1.5, 1])

with col_in:
    st.subheader("🏢 Data Penerima")
    r1, r2 = st.columns([2, 1])
    c_name = r1.text_input("Nama Klien", placeholder="Contoh: PT. Maju Terus")
    c_type = r2.selectbox("Tipe", ["Perusahaan", "Perorangan"])
    
    r3, r4 = st.columns(2)
    c_email = r3.text_input("Email Klien")
    c_phone = r4.text_input("Telp Klien")
    c_addr = st.text_area("Alamat Klien")
    
    st.divider()
    st.subheader("💰 Daftar Barang / Jasa")
    
    # Loop untuk input barang
    new_items = []
    subtotal_val = 0
    
    for i, item in enumerate(st.session_state.items):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 1.5, 1, 0.5])
            
            d = c1.text_input(f"Deskripsi #{i+1}", value=item['desc'], key=f"d_key_{i}")
            p = c2.number_input(f"Harga", value=int(item['price']), step=1000, key=f"p_key_{i}")
            q = c3.number_input(f"Qty", value=int(item['qty']), min_value=1, key=f"q_key_{i}")
            
            line_total = p * q
            subtotal_val += line_total
            
            # Simpan data yang diupdate
            new_items.append({"desc": d, "price": p, "qty": q})
            
            # Tombol Hapus Baris
            if c4.button("🗑️", key=f"del_key_{i}"):
                if len(st.session_state.items) > 1:
                    st.session_state.items.pop(i)
                    st.rerun()
            
            st.caption(f"Subtotal Item: Rp {line_total:,.0f}")

    st.session_state.items = new_items

    # Tombol Tambah Baris (Tanpa fungsi luar agar lebih stabil)
    if st.button("➕ Tambah Baris Barang/Jasa"):
        st.session_state.items.append({"desc": "", "price": 0, "qty": 1})
        st.rerun()

    st.divider()
    use_tax = st.checkbox("Gunakan Pajak (PPN 11%)")
    tax_v = (0.11 * subtotal_val) if use_tax else 0
    grand_total = subtotal_val + tax_v
    
    st.success(f"### Total Akhir: Rp {grand_total:,.0f}")
    notes = st.text_area("Catatan Pembayaran", value=f"Transfer BCA 123456789\nA/N {my_name}")

# --- PDF ENGINE ---
def create_pdf(logo, s_name, s_email, s_phone, s_addr, c_name, c_email, c_phone, c_addr, items, sub, t_amt, total, note):
    buf = io.BytesIO()
    pdf = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    
    # Header
    pdf.setFillColor(HexColor("#1f538d")); pdf.rect(0, h-100, w, 100, fill=True, stroke=False)
    if logo:
        pdf.drawImage(ImageReader(logo), w-130, h-80, width=80, height=60, preserveAspectRatio=True, mask='auto')
    
    pdf.setFillColor(HexColor("#ffffff"))
    pdf.setFont("Helvetica-Bold", 26); pdf.drawString(50, h-65, "INVOICE")
    pdf.setFont("Helvetica", 9); pdf.drawRightString(w-50, h-80, f"{s_phone} | {s_email}")
    
    # Table
    pdf.setFillColor(HexColor("#000000"))
    y = h-170
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "DESKRIPSI"); pdf.drawString(320, y, "QTY"); pdf.drawString(390, y, "HARGA"); pdf.drawRightString(w-50, y, "TOTAL")
    pdf.line(50, y-5, w-50, y-5); y -= 20
    
    pdf.setFont("Helvetica", 9)
    for it in items:
        start_y = y
        for line in textwrap.wrap(it['desc'], width=45):
            pdf.drawString(50, y, line); y -= 12
        pdf.drawString(320, start_y, str(it['qty']))
        pdf.drawString(390, start_y, f"{it['price']:,.0f}")
        pdf.drawRightString(w-50, start_y, f"{(it['price']*it['qty']):,.0f}")
        y = min(y, start_y - 15)
        
    y -= 30
    pdf.drawRightString(w-120, y, "Subtotal:"); pdf.drawRightString(w-50, y, f"Rp {sub:,.0f}"); y -= 15
    if t_amt > 0:
        pdf.drawRightString(w-120, y, "PPN 11%:"); pdf.drawRightString(w-50, y, f"Rp {t_amt:,.0f}"); y -= 20
    
    pdf.setFillColor(HexColor("#f4f4f4")); pdf.rect(w-220, y-10, 170, 30, fill=True, stroke=False)
    pdf.setFillColor(HexColor("#000000")); pdf.setFont("Helvetica-Bold", 12)
    pdf.drawRightString(w-60, y+2, f"TOTAL: Rp {total:,.0f}")
    
    pdf.save(); buf.seek(0)
    return buf

with col_preview:
    st.subheader("👀 Preview")
    with st.container(border=True):
        st.markdown(f"**Penerima:** {c_name if c_name else '-'}")
        st.write(f"Total Item: {len(st.session_state.items)}")
        st.write(f"**Grand Total: Rp {grand_total:,.0f}**")
        st.divider()
        
        if st.button("🚀 CETAK & DOWNLOAD PDF", type="primary", use_container_width=True):
            if not c_name:
                st.error("Nama Klien tidak boleh kosong!")
            else:
                pdf_res = create_pdf(uploaded_logo, my_name, my_email, my_phone, my_address, c_name, c_email, c_phone, c_addr, st.session_state.items, subtotal_val, tax_v, grand_total, notes)
                st.download_button("⬇️ Simpan File PDF", data=pdf_res, file_name=f"Invoice_{c_name}.pdf", use_container_width=True)
