import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import io
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

# --- MAIN LAYOUT (INPUT & PREVIEW) ---
col_input, col_preview = st.columns([1.2, 1])

with col_input:
    st.subheader("🏢 Data Penerima Tagihan")
    
    # Baris 1: Nama & Tipe
    row1_1, row1_2 = st.columns([2, 1])
    with row1_1:
        client_name = st.text_input("Nama Lengkap / Perusahaan", placeholder="Contoh: PT. Maju Terus")
    with row1_2:
        client_type = st.selectbox("Tipe", ["Perusahaan", "Perorangan"])
    
    # Baris 2: Kontak
    row2_1, row2_2 = st.columns(2)
    with row2_1:
        client_email = st.text_input("Email Klien")
    with row2_2:
        client_phone = st.text_input("No. Telp Klien")
    
    client_address = st.text_area("Alamat Lengkap Klien", height=80)
    
    st.divider()
    st.subheader("💰 Detail Tagihan")
    
    # Baris 3: No Invoice, Tgl, Nominal
    row3_1, row3_2, row3_3 = st.columns([1, 1, 1.2])
    with row3_1:
        inv_num = st.text_input("No. Invoice", value=datetime.now().strftime('%Y%m%d%H'))
    with row3_2:
        due_date = st.date_input("Jatuh Tempo")
    with row3_3:
        amount = st.number_input("Total Tagihan (Rp)", min_value=0, step=100000, format="%d")
        
    item_desc = st.text_area("Deskripsi Pekerjaan / Produk", placeholder="Contoh: Jasa Pembuatan Website Portfolio")
    notes = st.text_area("Catatan Pembayaran", value=f"Transfer Bank BCA\n123456789\nA/N {my_name}")

# --- FUNGSI PDF GENERATOR ---
def create_pdf(logo_file, inv_num, s_name, s_email, s_phone, s_addr, p_name, p_email, p_phone, p_addr, item, total, note):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Watermark
    c.saveState()
    c.setFont("Helvetica-Bold", 80)
    c.setFillColor(HexColor("#f0f0f0"), alpha=0.3)
    c.translate(width/2, height/2)
    c.rotate(45)
    c.drawCentredString(0, 0, "ORIGINAL")
    c.restoreState()
    
    # Header
    c.setFillColor(HexColor("#1f538d")) 
    c.rect(0, height - 120, width, 120, fill=True, stroke=False)
    if logo_file:
        img = ImageReader(logo_file)
        c.drawImage(img, width - 150, height - 90, width=100, height=60, preserveAspectRatio=True, mask='auto')
    
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 30)
    c.drawString(50, height - 70, "INVOICE")
    c.setFont("Helvetica", 9)
    c.drawRightString(width - 50, height - 75, f"Telp: {s_phone}")
    c.drawRightString(width - 50, height - 88, s_email)
    
    # Detail Client
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 150, "DITAGIHKAN KEPADA:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 168, f"{p_name.upper() if p_name else 'NAMA PENERIMA'}")
    c.setFont("Helvetica", 9)
    c.drawString(50, height - 182, f"Email: {p_email} | Telp: {p_phone}")
    
    # Alamat Client
    text_p = c.beginText(50, height - 195)
    text_p.setFont("Helvetica", 9)
    text_p.setLeading(11)
    for line in p_addr.split('\n'):
        text_p.textLine(line)
    c.drawText(text_p)

    # Info Invoice
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(width - 50, height - 150, f"No. Invoice: #{inv_num}")
    c.drawRightString(width - 50, height - 165, f"Tempo: {due_date}")

    # Tabel
    c.setStrokeColor(HexColor("#dddddd"))
    c.line(50, height - 260, width - 50, height - 260)
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 300, item if item else "-")
    c.drawRightString(width - 50, height - 300, f"Rp {total:,.2f}")

    # Total
    c.setFillColor(HexColor("#f4f4f4"))
    c.rect(width - 250, height - 360, 200, 40, fill=True, stroke=False)
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(width - 65, height - 345, f"Total: Rp {total:,.2f}")
    
    # Footer
    footer_y = height - 410
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, footer_y, "Catatan Pembayaran:")
    text_n = c.beginText(50, footer_y - 15)
    text_n.setFont("Helvetica", 9)
    text_n.setLeading(11)
    for line in note.split('\n'):
        text_n.textLine(line)
    c.drawText(text_n)
    
    num_lines = len(note.split('\n'))
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(HexColor("#666666"))
    c.drawString(50, footer_y - 30 - (num_lines * 11), f"Diterbitkan otomatis oleh {s_name}")
    
    c.save()
    buffer.seek(0)
    return buffer

# --- LIVE PREVIEW (KOLOM KANAN) ---
with col_preview:
    st.subheader("👀 Preview")
    with st.container(border=True):
        st.markdown(f"""
        <div style="background-color:#1f538d; padding:15px; border-radius:5px 5px 0 0; color:white;">
            <h2 style="margin:0;">INVOICE</h2>
            <p style="text-align:right; margin:0; font-size:12px;">{my_name}</p>
        </div>
        <div style="padding:15px; background-color:white; color:black; border:1px solid #ddd; font-family:sans-serif;">
            <p style="font-size:10px; color:gray; margin:0;">DITAGIHKAN KEPADA:</p>
            <h4 style="margin:0;">{client_name if client_name else 'NAMA PENERIMA'}</h4>
            <p style="font-size:12px; margin:0;">{client_email} | {client_phone}</p>
            <hr>
            <table style="width:100%; font-size:12px;">
                <tr><td><b>Deskripsi</b></td><td style="text-align:right;"><b>Total</b></td></tr>
                <tr><td>{item_desc if item_desc else '-'}</td><td style="text-align:right;">Rp {amount:,.0f}</td></tr>
            </table>
            <div style="background-color:#f4f4f4; padding:10px; margin-top:15px; text-align:right;">
                <h3 style="margin:0;">Rp {amount:,.0f}</h3>
            </div>
            <p style="font-size:10px; color:gray; margin-top:15px;"><b>Catatan:</b><br>{notes}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("🚀 Cetak Sekarang", type="primary", use_container_width=True):
            pdf_data = create_pdf(uploaded_logo, inv_num, my_name, my_email, my_phone, my_address, 
                                  client_name, client_email, client_phone, client_address, 
                                  item_desc, amount, notes)
            st.download_button(label="⬇️ Download PDF", data=pdf_data, file_name=f"INV_{client_name}.pdf", mime="application/pdf", use_container_width=True)
