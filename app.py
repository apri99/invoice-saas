import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import io
import textwrap
from datetime import datetime

st.set_page_config(page_title="Invoice Generator Pro", page_icon="🧾", layout="wide")

st.title("🚀 Invoice Generator Pro")

# --- SIDEBAR (DATA PENGIRIM) ---
with st.sidebar:
    st.header("🖼️ Branding")
    uploaded_logo = st.file_uploader("Logo Perusahaan", type=["png", "jpg", "jpeg"])
    st.divider()
    st.header("👤 Identitas Anda")
    my_name = st.text_input("Nama Bisnis", value="CV. MAJU JAYA")
    my_email = st.text_input("Email Bisnis", value="kontak@majusaja.com")
    my_phone = st.text_input("No. WhatsApp", value="08123456789")
    my_address = st.text_area("Alamat Bisnis", value="Jl. Utama No. 1, Jakarta")

# --- MAIN LAYOUT ---
col_input, col_preview = st.columns([1.2, 1])

with col_input:
    st.subheader("🏢 Data Penerima")
    r1_1, r1_2 = st.columns([2, 1])
    with r1_1: client_name = st.text_input("Nama Klien", placeholder="Contoh: PT. Maju Terus")
    with r1_2: client_type = st.selectbox("Tipe", ["Perusahaan", "Perorangan"])
    
    r2_1, r2_2 = st.columns(2)
    with r2_1: client_email = st.text_input("Email Klien")
    with r2_2: client_phone = st.text_input("No. Telp Klien")
    
    client_address = st.text_area("Alamat Lengkap Klien")
    
    st.divider()
    st.subheader("💰 Detail Tagihan")
    r3_1, r3_2, r3_3 = st.columns([1, 1, 1.2])
    with r3_1: inv_num = st.text_input("No. Invoice", value=datetime.now().strftime('%Y%m%d%H'))
    with r3_2: due_date = st.date_input("Jatuh Tempo")
    with r3_3: amount = st.number_input("Total Tagihan (Rp)", min_value=0, step=100000)
        
    item_desc = st.text_area("Deskripsi Pekerjaan", placeholder="Ketik deskripsi panjang di sini...")
    notes = st.text_area("Catatan Pembayaran", value=f"Transfer Bank BCA\n123456789\nA/N {my_name}")

def create_pdf(logo_file, inv_num, s_name, s_email, s_phone, s_addr, p_name, p_email, p_phone, p_addr, item, total, note):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Watermark
    c.saveState()
    c.setFont("Helvetica-Bold", 80)
    c.setFillColor(HexColor("#f0f0f0"), alpha=0.3)
    c.translate(width/2, height/2); c.rotate(45)
    c.drawCentredString(0, 0, "ORIGINAL")
    c.restoreState()
    
    # Header
    c.setFillColor(HexColor("#1f538d")) 
    c.rect(0, height - 120, width, 120, fill=True, stroke=False)
    if logo_file:
        img = ImageReader(logo_file)
        c.drawImage(img, width - 150, height - 90, width=100, height=60, preserveAspectRatio=True, mask='auto')
    
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 28); c.drawString(50, height - 70, "INVOICE")
    c.setFont("Helvetica", 9)
    c.drawRightString(width - 50, height - 75, f"Telp: {s_phone}")
    c.drawRightString(width - 50, height - 88, s_email)
    
    # Client Info
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 10); c.drawString(50, height - 150, "DITAGIHKAN KEPADA:")
    c.setFont("Helvetica-Bold", 12); c.drawString(50, height - 168, p_name.upper() if p_name else "NAMA PENERIMA")
    
    # Wrapping Alamat Klien
    c.setFont("Helvetica", 9)
    y_ptr = height - 182
    c.drawString(50, y_ptr, f"Email: {p_email} | Telp: {p_phone}"); y_ptr -= 15
    
    wrapped_addr = textwrap.wrap(p_addr, width=50)
    for line in wrapped_addr:
        c.drawString(50, y_ptr, line); y_ptr -= 12

    # Info Invoice
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(width - 50, height - 150, f"No. Invoice: #{inv_num}")
    c.drawRightString(width - 50, height - 165, f"Tempo: {due_date}")

    # Tabel Deskripsi dengan Wrapping
    c.setStrokeColor(HexColor("#dddddd")); c.line(50, height - 280, width - 50, height - 280)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 295, "DESKRIPSI PEKERJAAN")
    c.drawRightString(width - 50, height - 295, "SUBTOTAL")
    
    c.setFont("Helvetica", 10)
    y_item = height - 315
    wrapped_item = textwrap.wrap(item if item else "-", width=70)
    for line in wrapped_item:
        c.drawString(50, y_item, line)
        y_item -= 15
    
    # Subtotal tetap sejajar baris pertama item
    c.drawRightString(width - 50, height - 315, f"Rp {total:,.2f}")

    # Total Box
    c.setFillColor(HexColor("#f4f4f4"))
    c.rect(width - 250, y_item - 40, 200, 40, fill=True, stroke=False)
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(width - 65, y_item - 25, f"Total: Rp {total:,.2f}")
    
    # Footer Rapat
    y_footer = y_item - 80
    c.setFont("Helvetica-Bold", 9); c.drawString(50, y_footer, "Catatan Pembayaran:")
    c.setFont("Helvetica", 9)
    y_footer -= 15
    for line in note.split('\n'):
        c.drawString(50, y_footer, line); y_footer -= 12
    
    c.setFont("Helvetica-Oblique", 8); c.setFillColor(HexColor("#666666"))
    c.drawString(50, y_footer - 10, f"Diterbitkan otomatis oleh {s_name}")
    
    c.save()
    buffer.seek(0)
    return buffer

with col_preview:
    st.subheader("👀 Preview")
    with st.container(border=True):
        st.markdown(f"""
        <div style="background-color:#1f538d; padding:15px; border-radius:5px 5px 0 0; color:white;">
            <h2 style="margin:0;">INVOICE</h2>
            <p style="text-align:right; margin:0; font-size:12px;">{my_name}</p>
        </div>
        <div style="padding:15px; background-color:white; color:black; border:1px solid #ddd; word-wrap: break-word;">
            <p style="font-size:10px; color:gray; margin:0;">DITAGIHKAN KEPADA:</p>
            <h4 style="margin:0;">{client_name if client_name else 'NAMA PENERIMA'}</h4>
            <p style="font-size:11px; margin:0;">{client_email} | {client_phone}</p>
            <p style="font-size:11px;">{client_address}</p>
            <hr>
            <div style="display: flex; justify-content: space-between; font-size:12px;">
                <div style="max-width: 70%; font-weight: bold;">Deskripsi</div>
                <div style="font-weight: bold;">Total</div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size:12px; margin-top:5px;">
                <div style="max-width: 70%; white-space: pre-wrap;">{item_desc if item_desc else '-'}</div>
                <div>Rp {amount:,.0f}</div>
            </div>
            <div style="background-color:#f4f4f4; padding:10px; margin-top:15px; text-align:right;">
                <h3 style="margin:0;">Rp {amount:,.0f}</h3>
            </div>
            <p style="font-size:10px; color:gray; margin-top:10px; white-space: pre-wrap;"><b>Catatan:</b><br>{notes}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Cetak Sekarang", type="primary", use_container_width=True):
            pdf_data = create_pdf(uploaded_logo, inv_num, my_name, my_email, my_phone, my_address, 
                                  client_name, client_email, client_phone, client_address, 
                                  item_desc, amount, notes)
            st.download_button(label="⬇️ Download PDF", data=pdf_data, file_name=f"INV_{client_name}.pdf", mime="application/pdf", use_container_width=True)
