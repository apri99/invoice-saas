import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import io
import textwrap
from datetime import datetime

st.set_page_config(page_title="Invoice Generator Pro", page_icon="🧾", layout="wide")

# --- INISIALISASI MEMORI (SESSION STATE) ---
if 'items' not in st.session_state:
    st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]

def add_item():
    st.session_state.items.append({"desc": "", "price": 0, "qty": 1})

def delete_item(index):
    if len(st.session_state.items) > 1:
        st.session_state.items.pop(index)

st.title("🚀 Invoice Generator Pro")
st.markdown("Fitur: **Multi-Item & Kalkulator Otomatis**")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🖼️ Branding")
    uploaded_logo = st.file_uploader("Logo", type=["png", "jpg", "jpeg"])
    st.divider()
    my_name = st.text_input("Nama Anda/Bisnis", value="CV. MAJU JAYA")
    my_email = st.text_input("Email", value="kontak@majusaja.com")
    my_phone = st.text_input("WhatsApp", value="08123456789")
    my_address = st.text_area("Alamat", value="Jl. Utama No. 1, Jakarta")

# --- MAIN LAYOUT ---
col_input, col_preview = st.columns([1.5, 1])

with col_input:
    st.subheader("🏢 Data Penerima")
    r1_1, r1_2 = st.columns([2, 1])
    client_name = r1_1.text_input("Nama Klien")
    client_type = r1_2.selectbox("Tipe", ["Perusahaan", "Perorangan"])
    
    r2_1, r2_2 = st.columns(2)
    client_email = r2_1.text_input("Email Klien")
    client_phone = r2_2.text_input("Telp Klien")
    client_address = st.text_area("Alamat Klien")
    
    st.divider()
    st.subheader("💰 Detail Barang / Jasa")
    
    # --- INPUT MULTI ITEM ---
    grand_subtotal = 0
    for i, item in enumerate(st.session_state.items):
        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([3, 2, 1, 2, 0.5])
            
            st.session_state.items[i]['desc'] = c1.text_input(f"Deskripsi #{i+1}", value=item['desc'], key=f"desc_{i}")
            st.session_state.items[i]['price'] = c2.number_input(f"Harga Satuan", value=item['price'], min_value=0, step=1000, key=f"price_{i}")
            st.session_state.items[i]['qty'] = c3.number_input(f"Qty", value=item['qty'], min_value=1, key=f"qty_{i}")
            
            row_total = st.session_state.items[i]['price'] * st.session_state.items[i]['qty']
            grand_subtotal += row_total
            
            c4.markdown(f"**Total Item:** \nRp {row_total:,.0f}")
            if c5.button("🗑️", key=f"del_{i}"):
                delete_item(i)
                st.rerun()

    st.button("➕ Tambah Barang/Jasa", on_click=add_item)

    # --- HITUNG PAJAK ---
    st.divider()
    use_tax = st.checkbox("Tambahkan Pajak (PPN)")
    tax_amt = 0
    tax_rate = 0
    if use_tax:
        tax_rate = st.number_input("PPN (%)", value=11.0)
        tax_amt = (tax_rate/100) * grand_subtotal
    
    total_akhir = grand_subtotal + tax_amt
    st.success(f"### Grand Total: Rp {total_akhir:,.0f}")
    notes = st.text_area("Catatan Pembayaran", value=f"Transfer BCA 123456789 A/N {my_name}")

def create_pdf(logo, name, email, phone, addr, c_name, c_email, c_phone, c_addr, items, sub, t_rate, t_amt, total, note):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    
    # Header & Logo
    c.setFillColor(HexColor("#1f538d")); c.rect(0, h-100, w, 100, fill=True)
    if logo:
        img = ImageReader(logo)
        c.drawImage(img, w-140, h-80, width=80, height=60, preserveAspectRatio=True, mask='auto')
    
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 24); c.drawString(50, h-60, "INVOICE")
    
    # Client Info
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 10); c.drawString(50, h-130, "KEPADA:")
    c.setFont("Helvetica", 10); c.drawString(50, h-145, c_name)
    c.setFont("Helvetica", 8); c.drawString(50, h-155, f"{c_email} | {c_phone}")
    
    # Alamat Client (Wrap)
    y_ptr = h-165
    for line in textwrap.wrap(c_addr, width=50):
        c.drawString(50, y_ptr, line); y_ptr -= 10

    # TABEL BARANG
    y_table = y_ptr - 30
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y_table, "DESKRIPSI"); c.drawString(300, y_table, "QTY"); c.drawString(370, y_table, "HARGA"); c.drawRightString(w-50, y_table, "TOTAL")
    c.line(50, y_table-5, w-50, y_table-5)
    
    y_ptr = y_table - 20
    c.setFont("Helvetica", 9)
    for item in items:
        # Wrap deskripsi per item
        lines = textwrap.wrap(item['desc'], width=40)
        start_y = y_ptr
        for line in lines:
            c.drawString(50, y_ptr, line); y_ptr -= 12
        
        c.drawString(300, start_y, str(item['qty']))
        c.drawString(370, start_y, f"{item['price']:,.0f}")
        c.drawRightString(w-50, start_y, f"{(item['price']*item['qty']):,.0f}")
        y_ptr -= 5 # spasi antar item
        
    # TOTALS
    y_ptr -= 20
    c.line(w-200, y_ptr, w-50, y_ptr)
    c.drawRightString(w-120, y_ptr-15, "Subtotal:")
    c.drawRightString(w-50, y_ptr-15, f"Rp {sub:,.0f}")
    if t_amt > 0:
        y_ptr -= 15
        c.drawRightString(w-120, y_ptr-15, f"Pajak {t_rate}%:")
        c.drawRightString(w-50, y_ptr-15, f"Rp {t_amt:,.0f}")
    
    y_ptr -= 35
    c.setFillColor(HexColor("#f4f4f4")); c.rect(w-210, y_ptr, 160, 25, fill=True, stroke=False)
    c.setFillColor(HexColor("#000000")); c.setFont("Helvetica-Bold", 11)
    c.drawRightString(w-60, y_ptr+8, f"TOTAL: Rp {total:,.0f}")

    c.save(); buffer.seek(0)
    return buffer

with col_preview:
    st.subheader("👀 Preview")
    # Preview sederhana UI
    st.info(f"Penerima: {client_name}\n\nTotal Item: {len(st.session_state.items)}")
    for item in st.session_state.items:
        if item['desc']: st.write(f"- {item['desc']} (x{item['qty']})")
    
    if st.button("🚀 Cetak PDF", type="primary", use_container_width=True):
        pdf = create_pdf(uploaded_logo, my_name, my_email, my_phone, my_address, client_name, client_email, client_phone, client_address, st.session_state.items, grand_subtotal, tax_rate, tax_amt, total_akhir, notes)
        st.download_button("⬇️ Download Invoice", data=pdf, file_name=f"Invoice_{client_name}.pdf")
