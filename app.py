import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import io
import textwrap
from datetime import datetime

# --- VERSI UPDATE: 2.1 (Multi-Item Engine) ---
st.set_page_config(page_title="Invoice Generator Pro v2.1", page_icon="🧾", layout="wide")

# Inisialisasi State
if 'items' not in st.session_state:
    st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]

def add_item():
    st.session_state.items.append({"desc": "", "price": 0, "qty": 1})

def delete_item(index):
    if len(st.session_state.items) > 1:
        st.session_state.items.pop(index)

st.title("🚀 Invoice Generator Pro")
st.info("Versi 2.1 Aktif: Sistem Multi-Item & Kalkulasi Otomatis")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🖼️ Branding")
    uploaded_logo = st.file_uploader("Logo", type=["png", "jpg", "jpeg"])
    st.divider()
    my_name = st.text_input("Nama Anda/Bisnis", value="CV. MAJU JAYA")
    my_type = st.selectbox("Tipe", ["Perusahaan", "Perorangan"])
    my_email = st.text_input("Email", value="kontak@majusaja.com")
    my_phone = st.text_input("WhatsApp", value="08123456789")
    my_address = st.text_area("Alamat", value="Jl. Utama No. 1, Jakarta")

# --- MAIN LAYOUT ---
col_in, col_pre = st.columns([1.5, 1])

with col_in:
    st.subheader("🏢 Data Penerima")
    r1, r2 = st.columns([2, 1])
    c_name = r1.text_input("Nama Klien")
    c_type = r2.selectbox("Tipe Klien", ["Perusahaan", "Perorangan"])
    
    r3, r4 = st.columns(2)
    c_email = r3.text_input("Email Klien")
    c_phone = r4.text_input("Telp Klien")
    c_addr = st.text_area("Alamat Klien")
    
    st.divider()
    st.subheader("💰 Daftar Barang / Jasa")
    
    subtotal_total = 0
    for i, item in enumerate(st.session_state.items):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 1.5, 1, 0.5])
            
            # Update data langsung ke session state
            item['desc'] = c1.text_input(f"Deskripsi Item {i+1}", value=item['desc'], key=f"d_{i}")
            item['price'] = c2.number_input(f"Harga Satuan", value=item['price'], step=1000, key=f"p_{i}")
            item['qty'] = c3.number_input(f"Qty", value=item['qty'], min_value=1, key=f"q_{i}")
            
            line_total = item['price'] * item['qty']
            subtotal_total += line_total
            
            if c4.button("🗑️", key=f"btn_{i}"):
                delete_item(i)
                st.rerun()
            
            st.caption(f"Subtotal Item: Rp {line_total:,.0f}")

    st.button("➕ Tambah Baris Baru", on_click=add_item)

    st.divider()
    use_tax = st.checkbox("Gunakan Pajak (PPN)")
    tax_v = 0
    tax_r = 0
    if use_tax:
        tax_r = st.number_input("Persen Pajak (%)", value=11.0)
        tax_v = (tax_r/100) * subtotal_total
    
    grand_total = subtotal_total + tax_v
    st.markdown(f"### Grand Total: Rp {grand_total:,.0f}")
    notes = st.text_area("Catatan", value=f"Transfer BCA 123456789 A/N {my_name}")

# --- PDF ENGINE ---
def get_pdf(logo, s_name, s_email, s_phone, s_addr, c_name, c_email, c_phone, c_addr, items, sub, t_rate, t_amt, total, note):
    buf = io.BytesIO()
    pdf = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    
    # Header
    pdf.setFillColor(HexColor("#1f538d")); pdf.rect(0, h-100, w, 100, fill=True)
    if logo:
        pdf.drawImage(ImageReader(logo), w-130, h-80, width=70, height=50, preserveAspectRatio=True, mask='auto')
    
    pdf.setFillColor(HexColor("#ffffff"))
    pdf.setFont("Helvetica-Bold", 24); pdf.drawString(50, h-60, "INVOICE")
    
    # Content
    pdf.setFillColor(HexColor("#000000"))
    pdf.setFont("Helvetica-Bold", 10); pdf.drawString(50, h-130, "KEPADA:")
    pdf.setFont("Helvetica", 10); pdf.drawString(50, h-145, f"{c_name}")
    
    y = h-170
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(50, y, "DESKRIPSI"); pdf.drawString(300, y, "QTY"); pdf.drawString(380, y, "HARGA"); pdf.drawRightString(w-50, y, "TOTAL")
    pdf.line(50, y-5, w-50, y-5)
    
    y -= 20
    pdf.setFont("Helvetica", 9)
    for it in items:
        start_y = y
        for line in textwrap.wrap(it['desc'], width=40):
            pdf.drawString(50, y, line); y -= 12
        pdf.drawString(300, start_y, str(it['qty']))
        pdf.drawString(380, start_y, f"{it['price']:,.0f}")
        pdf.drawRightString(w-50, start_y, f"{(it['price']*it['qty']):,.0f}")
        y -= 5

    # Footer Total
    y -= 30
    pdf.drawRightString(w-120, y, "Subtotal:")
    pdf.drawRightString(w-50, y, f"Rp {sub:,.0f}")
    if t_amt > 0:
        y -= 15
        pdf.drawRightString(w-120, y, f"PPN {t_rate}%:")
        pdf.drawRightString(w-50, y, f"Rp {t_amt:,.0f}")
    
    y -= 30
    pdf.setFillColor(HexColor("#f4f4f4")); pdf.rect(w-220, y-10, 170, 30, fill=True, stroke=False)
    pdf.setFillColor(HexColor("#000000")); pdf.setFont("Helvetica-Bold", 12)
    pdf.drawRightString(w-60, y+2, f"TOTAL: Rp {total:,.0f}")
    
    pdf.save(); buf.seek(0)
    return buf

with col_pre:
    st.subheader("👀 Preview")
    st.write(f"**Penerima:** {c_name if c_name else '-'}")
    st.write(f"**Total Item:** {len(st.session_state.items)}")
    
    if st.button("🚀 CETAK SEKARANG", type="primary", use_container_width=True):
        res = get_pdf(uploaded_logo, my_name, my_email, my_phone, my_address, c_name, c_email, c_phone, c_addr, st.session_state.items, subtotal_total, tax_r, tax_v, grand_total, notes)
        st.download_button("⬇️ Download PDF", data=res, file_name="Invoice_Pro.pdf", use_container_width=True)
