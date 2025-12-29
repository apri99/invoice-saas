import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import io
import textwrap
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="Invoice Generator Pro v2.3", page_icon="🧾", layout="wide")

# --- SISTEM KEAMANAN SESSION STATE ---
if 'items' not in st.session_state or st.session_state.items is None:
    st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]

def add_item():
    st.session_state.items.append({"desc": "", "price": 0, "qty": 1})

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
    st.header("👤 Identitas Pengirim")
    my_name = st.text_input("Nama Bisnis", value="CV. MAJU JAYA")
    my_type = st.selectbox("Tipe", ["Perusahaan", "Perorangan"])
    my_email = st.text_input("Email", value="kontak@majusaja.com")
    my_phone = st.text_input("No. WhatsApp", value="08123456789")
    my_address = st.text_area("Alamat Lengkap", value="Jl. Utama No. 1, Jakarta")
    if st.button("Reset Aplikasi (Clear Error)"):
        st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]
        st.rerun()

# --- MAIN LAYOUT ---
col_in, col_pre = st.columns([1.4, 1])

with col_in:
    st.subheader("🏢 Data Penerima")
    r1, r2 = st.columns([2, 1])
    c_name = r1.text_input("Nama Klien", placeholder="Contoh: PT. Maju Terus")
    c_type = r2.selectbox("Tipe Klien", ["Perusahaan", "Perorangan"])
    
    r3, r4 = st.columns(2)
    c_email = r3.text_input("Email Klien")
    c_phone = r4.text_input("Telp Klien")
    c_addr = st.text_area("Alamat Lengkap Klien")
    
    st.divider()
    st.subheader("💰 Daftar Barang / Jasa")
    
    subtotal_val = 0
    # Loop Input Item dengan pengaman try-except
    try:
        for i in range(len(st.session_state.items)):
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3, 1.5, 1, 0.5])
                
                desc = c1.text_input(f"Deskripsi #{i+1}", value=st.session_state.items[i]['desc'], key=f"f_desc_{i}")
                price = c2.number_input(f"Harga", value=int(st.session_state.items[i]['price']), step=1000, key=f"f_price_{i}")
                qty = c3.number_input(f"Qty", value=int(st.session_state.items[i]['qty']), min_value=1, key=f"f_qty_{i}")
                
                # Simpan data
                st.session_state.items[i] = {"desc": desc, "price": price, "qty": qty}
                
                line_total = price * qty
                subtotal_val += line_total
                
                if c4.button("🗑️", key=f"f_del_{i}"):
                    delete_item(i)
                    st.rerun()
                st.caption(f"Subtotal Item: Rp {line_total:,.0f}")
    except Exception as e:
        st.error("Terjadi sinkronisasi data. Silakan klik tombol 'Reset Aplikasi' di sidebar.")

    st.button("➕ Tambah Baris Barang/Jasa", on_click=add_item)

    st.divider()
    use_tax = st.checkbox("Gunakan Pajak (PPN 11%)")
    tax_v = 0
    if use_tax:
        tax_v = 0.11 * subtotal_val
    
    grand_total = subtotal_val + tax_v
    st.info(f"Subtotal: Rp {subtotal_val:,.0f} | Pajak: Rp {tax_v:,.0f}")
    st.success(f"### Total Akhir: Rp {grand_total:,.0f}")
    
    notes = st.text_area("Catatan Pembayaran", value=f"Transfer BCA 123456789\nA/N {my_name}")

# --- PDF ENGINE ---
def create_pdf(logo, s_name, s_email, s_phone, s_addr, c_name, c_email, c_phone, c_addr, items, sub, t_amt, total, note):
    buf = io.BytesIO()
    pdf = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    
    # Header Biru
    pdf.setFillColor(HexColor("#1f538d")); pdf.rect(0, h-100, w, 100, fill=True, stroke=False)
    if logo:
        pdf.drawImage(ImageReader(logo), w-130, h-80, width=80, height=60, preserveAspectRatio=True, mask='auto')
    
    pdf.setFillColor(HexColor("#ffffff"))
    pdf.setFont("Helvetica-Bold", 26); pdf.drawString(50, h-65, "INVOICE")
    pdf.setFont("Helvetica", 9); pdf.drawRightString(w-50, h-80, f"{s_phone} | {s_email}")
    
    # Body
    pdf.setFillColor(HexColor("#000000"))
    pdf.setFont("Helvetica-Bold", 10); pdf.drawString(50, h-130, "DITAGIHKAN KEPADA:")
    pdf.setFont("Helvetica-Bold", 12); pdf.drawString(50, h-148, str(c_name).upper() if c_name else "NAMA PENERIMA")
    
    y = h-165
    pdf.setFont("Helvetica", 9); pdf.drawString(50, y, f"Telp: {c_phone} | {c_email}"); y -= 12
    for line in textwrap.wrap(c_addr, width=60):
        pdf.drawString(50, y, line); y -= 12
    
    # Table
    y -= 30
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
    pdf.drawRightString(w-130, y, "Subtotal:"); pdf.drawRightString(w-50, y, f"Rp {sub:,.0f}"); y -= 15
    if t_amt > 0:
        pdf.drawRightString(w-130, y, "PPN 11%:"); pdf.drawRightString(w-50, y, f"Rp {t_amt:,.0f}"); y -= 20
    
    pdf.setFillColor(HexColor("#f4f4f4")); pdf.rect(w-220, y-10, 170, 30, fill=True, stroke=False)
    pdf.setFillColor(HexColor("#000000")); pdf.setFont("Helvetica-Bold", 12)
    pdf.drawRightString(w-60, y+2, f"TOTAL: Rp {total:,.0f}")
    
    pdf.save(); buf.seek(0)
    return buf

with col_pre:
    st.subheader("👀 Preview")
    with st.container(border=True):
        st.markdown(f"**{my_name}** ({my_type})")
        st.write(f"Klien: {c_name}")
        st.divider()
        st.write(f"**Total Akhir: Rp {grand_total:,.0f}**")
        
        if st.button("🚀 DOWNLOAD PDF", type="primary", use_container_width=True):
            pdf_res = create_pdf(uploaded_logo, my_name, my_email, my_phone, my_address, c_name, c_email, c_phone, c_addr, st.session_state.items, subtotal_val, tax_v, grand_total, notes)
            st.download_button("⬇️ Simpan File", data=pdf_res, file_name=f"Invoice_{c_name}.pdf", use_container_width=True)
