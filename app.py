import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import io
from datetime import datetime

st.set_page_config(page_title="Invoice Generator Pro", page_icon="🧾", layout="wide")

st.title("🚀 Invoice Generator Pro")
st.markdown("Isi data di bawah untuk melihat **Live Preview** sebelum cetak.")

# --- SIDEBAR / INPUT DATA ---
with st.sidebar:
    st.header("🖼️ Branding & Logo")
    uploaded_logo = st.file_uploader("Upload Logo", type=["png", "jpg", "jpeg"])
    
    st.header("👤 Pengirim")
    my_name = st.text_input("Nama Bisnis", value="CV. MAJU JAYA")
    my_email = st.text_input("Email", value="kontak@majusaja.com")
    my_phone = st.text_input("No. Telp", value="08123456789")
    my_address = st.text_area("Alamat", value="Jl. Utama No. 1, Jakarta")

# --- MAIN CONTENT ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("🏢 Data Penerima")
    client_name = st.text_input("Nama Klien", placeholder="Contoh: PT. INDO")
    client_address = st.text_area("Alamat Klien")
    client_email = st.text_input("Email Klien")
    client_phone = st.text_input("Telp Klien")
    
    st.subheader("💰 Detail Tagihan")
    item_desc = st.text_area("Deskripsi Pekerjaan")
    amount = st.number_input("Total Nominal (Rp)", min_value=0, step=50000)
    notes = st.text_area("Catatan Pembayaran", value="Transfer BCA 123456789 a/n CV MAJU JAYA")

# --- FUNGSI GENERATE PDF ---
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
    
    # Body
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 150, "DITAGIHKAN KEPADA:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 168, p_name.upper() if p_name else "NAMA PENERIMA")
    
    text_p = c.beginText(50, height - 182)
    text_p.setFont("Helvetica", 9)
    text_p.setLeading(11)
    text_p.textLine(f"Email: {p_email} | Telp: {p_phone}")
    for line in p_addr.split('\n'):
        text_p.textLine(line)
    c.drawText(text_p)

    # Tabel & Total
    c.setStrokeColor(HexColor("#dddddd"))
    c.line(50, height - 270, width - 50, height - 270)
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 310, item if item else "-")
    c.drawRightString(width - 50, height - 310, f"Rp {total:,.2f}")

    # Box Total
    c.setFillColor(HexColor("#f4f4f4"))
    c.rect(width - 250, height - 370, 200, 40, fill=True, stroke=False)
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 65, height - 355, f"Total: Rp {total:,.2f}")
    
    c.save()
    buffer.seek(0)
    return buffer

# --- LIVE PREVIEW (KOLOM KANAN) ---
with col_right:
    st.subheader("👀 Preview Invoice")
    with st.container(border=True):
        # Simulasi Header Invoice di UI
        st.markdown(f"""
        <div style="background-color:#1f538d; padding:20px; border-radius:5px 5px 0 0; color:white;">
            <h1 style="margin:0;">INVOICE</h1>
            <p style="text-align:right; margin:0;"><b>{my_name}</b></p>
            <p style="text-align:right; margin:0; font-size:12px;">{my_phone} | {my_email}</p>
        </div>
        <div style="padding:20px; background-color: white; color: black; border: 1px solid #ddd;">
            <p style="font-size:12px; color:gray; margin-bottom:5px;">DITAGIHKAN KEPADA:</p>
            <h3 style="margin:0;">{client_name if client_name else "NAMA PENERIMA"}</h3>
            <p style="font-size:13px; margin:0;">{client_email} | {client_phone}</p>
            <p style="font-size:13px;">{client_address}</p>
            <hr>
            <table style="width:100%; font-size:14px;">
                <tr><td><b>Deskripsi</b></td><td style="text-align:right;"><b>Total</b></td></tr>
                <tr><td>{item_desc if item_desc else "-"}</td><td style="text-align:right;">Rp {amount:,.0f}</td></tr>
            </table>
            <div style="background-color:#f4f4f4; padding:10px; margin-top:20px; text-align:right;">
                <h2 style="margin:0;">Total: Rp {amount:,.0f}</h2>
            </div>
            <div style="margin-top:20px; font-size:11px; color:gray;">
                <b>Catatan Pembayaran:</b><br>{notes}<br><br>
                <i>Invoice ini diterbitkan secara otomatis oleh {my_name}</i>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("🚀 Konfirmasi & Cetak PDF", type="primary", use_container_width=True):
            inv_num = f"INV-{datetime.now().strftime('%H%M%S')}"
            pdf_data = create_pdf(uploaded_logo, inv_num, my_name, my_email, my_phone, my_address, 
                                  client_name, client_email, client_phone, client_address, 
                                  item_desc, amount, notes)
            st.success("Invoice siap di-download!")
            st.download_button(label="⬇️ Klik Disini Untuk Simpan PDF", data=pdf_data, file_name=f"Invoice_{client_name}.pdf", mime="application/pdf", use_container_width=True)
