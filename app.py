import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import io
import textwrap
from datetime import datetime

st.set_page_config(page_title="Invoice Generator Pro v2.2", page_icon="🧾", layout="wide")

# --- FIX: Inisialisasi Session State yang lebih aman ---
if 'items' not in st.session_state or not isinstance(st.session_state.items, list):
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

# --- MAIN CONTENT ---
col_in, col_pre = st.columns([1.5, 1])

with col_in:
    st.subheader("🏢 Data Penerima")
    r1, r2 = st.columns([2, 1])
    c_name = r1.text_input("Nama Klien", placeholder="PT. ABC / Bapak Slamet")
    c_type = r2.selectbox("Tipe Klien", ["Perusahaan", "Perorangan"], key="c_type_box")
    
    r3, r4 = st.columns(2)
    c_email = r3.text_input("Email Klien")
    c_phone = r4.text_input("Telp Klien")
    c_addr = st.text_area("Alamat Lengkap Klien")
    
    st.divider()
    st.subheader("💰 Daftar Barang / Jasa")
    
    # Perhitungan Total
    subtotal_val = 0
    
    # Loop Input Item (Dibuat lebih aman)
    current_items = list(st.session_state.items)
    for i, item in enumerate(current_items):
        with st.container(border=True):
            # Layout Grid per Baris
            c1, c2, c3, c4 = st.columns([3, 1.5, 1, 0.5])
            
            # Input Data
            desc = c1.text_input(f"Deskripsi #{i+1}", value=item['desc'], key=f"desc_fix_{i}")
            price = c2.number_input(f"Harga Satuan", value=int(item['price']), step=1000, key=f"price_fix_{i}")
            qty = c3.number_input(f"Qty", value=int(item['qty']), min_value=1, key=f"qty_fix_{i}")
            
            # Simpan kembali ke state
            st.session_state.items[i] = {"desc": desc, "price": price, "qty": qty}
            
            line_total = price * qty
            subtotal_val += line_total
            
            if c4.button("🗑️", key=f"del_fix_{i}"):
                delete_item(i)
                st.rerun()
            
            st.caption(f"Subtotal: Rp {line_total:,.0f}")

    st.button("➕ Tambah Baris Baru", on_click=add_item)

    st.divider()
    # Pajak Opsional
    use_tax = st.checkbox("Gunakan Pajak (PPN)")
    tax_value = 0
    tax_rate = 0
    if use_tax:
        tax_rate = st.number_input("PPN (%)", value=11.0, step=0.1)
        tax_value = (tax_rate/100) * subtotal_val
    
    grand_total = subtotal_val + tax_value
    st.success(f"### Total Akhir: Rp {grand_total:,.0f}")
    
    notes = st.text_area("Catatan Pembayaran", value=f"Transfer BCA 123456789\nA/N {my_name}")

# --- PDF GENERATOR ---
def create_pdf(logo, s_name, s_email, s_phone, s_addr, c_name, c_email, c_phone, c_addr, items, sub, t_rate, t_amt, total, note):
    buf = io.BytesIO()
    pdf = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    
    # Watermark
    pdf.saveState()
    pdf.setFont("Helvetica-Bold", 70); pdf.setFillColor(HexColor("#eeeeee"), alpha=0.3)
    pdf.translate(w/2, h/2); pdf.rotate(45); pdf.drawCentredString(0, 0, "ORIGINAL"); pdf.restoreState()
    
    # Header
    pdf.setFillColor(HexColor("#1f538d")); pdf.rect(0, h-100, w, 100, fill=True, stroke=False)
    if logo:
        pdf.drawImage(ImageReader(logo), w-130, h-80, width=80, height=60, preserveAspectRatio=True, mask='auto')
    
    pdf.setFillColor(HexColor("#ffffff"))
    pdf.setFont("Helvetica-Bold", 26); pdf.drawString(50, h-65, "INVOICE")
    pdf.setFont("Helvetica", 9)
    pdf.drawRightString(w-50, h-75, f"Telp: {s_phone} | {s_email}")
    
    # Content
    pdf.setFillColor(HexColor("#000000"))
    pdf.setFont("Helvetica-Bold", 10); pdf.drawString(50, h-130, "DITAGIHKAN KEPADA:")
    pdf.setFont("Helvetica-Bold", 12); pdf.drawString(50, h-148, str(c_name).upper() if c_name else "NAMA PENERIMA")
    
    y = h-165
    pdf.setFont("Helvetica", 9); pdf.drawString(50, y, f"Telp: {c_phone} | {c_email}"); y -= 12
    for line in textwrap.wrap(c_addr, width=60):
        pdf.drawString(50, y, line); y -= 12
    
    # Table Header
    y -= 25
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "DESKRIPSI"); pdf.drawString(320, y, "QTY"); pdf.drawString(390, y, "HARGA"); pdf.drawRightString(w-50, y, "TOTAL")
    pdf.line(50, y-5, w-50, y-5); y -= 20
    
    # Table Items
    pdf.setFont("Helvetica", 9)
    for it in items:
        curr_y = y
        wrapped_desc = textwrap.wrap(it['desc'], width=45)
        for line in wrapped_desc:
            pdf.drawString(50, y, line); y -= 12
        
        pdf.drawString(320, curr_y, str(it['qty']))
        pdf.drawString(390, curr_y, f"{it['price']:,.0f}")
        pdf.drawRightString(w-50, curr_y, f"{(it['price']*it['qty']):,.0f}")
        y = min(y, curr_y - 15)
        
    # Kalkulasi Akhir
    y -= 30
    pdf.line(w-200, y, w-50, y); y -= 15
    pdf.setFont("Helvetica", 10); pdf.drawRightString(w-130, y, "Subtotal:")
    pdf.drawRightString(w-50, y, f"Rp {sub:,.0f}"); y -= 15
    
    if t_amt > 0:
        pdf.drawRightString(w-130, y, f"Pajak ({t_rate}%):")
        pdf.drawRightString(w-50, y, f"Rp {t_amt:,.0f}"); y -= 20
    
    pdf.setFillColor(HexColor("#f4f4f4")); pdf.rect(w-220, y-10, 170, 30, fill=True, stroke=False)
    pdf.setFillColor(HexColor("#000000")); pdf.setFont("Helvetica-Bold", 12)
    pdf.drawRightString(w-60, y+2, f"TOTAL: Rp {total:,.0f}")
    
    # Footer
    y -= 60
    pdf.setFont("Helvetica-Bold", 9); pdf.drawString(50, y, "Catatan Pembayaran:"); y -= 15
    pdf.setFont("Helvetica", 9)
    for line in note.split('\n'):
        pdf.drawString(50, y, line); y -= 12
    
    pdf.save(); buf.seek(0)
    return buf

with col_pre:
    st.subheader("👀 Preview")
    # Preview Simpel
    with st.container(border=True):
        st.markdown(f"**{my_name}**")
        st.write(f"Klien: {c_name if c_name else '-'}")
        st.write(f"Total Item: {len(st.session_state.items)}")
        st.divider()
        st.write(f"**Grand Total: Rp {grand_total:,.0f}**")
        
        if st.button("🚀 CETAK INVOICE SEKARANG", type="primary", use_container_width=True):
            pdf_res = create_pdf(uploaded_logo, my_name, my_email, my_phone, my_address, c_name, c_email, c_phone, c_addr, st.session_state.items, subtotal_val, tax_rate, tax_value, grand_total, notes)
            st.download_button("⬇️ Download PDF", data=pdf_res, file_name=f"Invoice_{c_name}.pdf", use_container_width=True)
