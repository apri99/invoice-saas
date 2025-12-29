import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
import io
from datetime import datetime

st.set_page_config(page_title="Invoice Generator Pro", page_icon="🧾", layout="centered")

st.title("🚀 Invoice Generator Pro")
st.markdown("Versi Teroptimasi: Jarak footer lebih proporsional.")

# --- INPUT DATA ---
with st.expander("👤 Data Pengirim (Bisnis Anda)", expanded=True):
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        my_name = st.text_input("Nama Bisnis/Anda", placeholder="Contoh: Apri Design Studio")
        my_email = st.text_input("Email Pengirim", placeholder="kontak@bisnisanda.com")
    with col_s2:
        my_phone = st.text_input("No. Telp Pengirim", placeholder="0812xxxxxxx")
        my_address = st.text_area("Alamat Lengkap Pengirim", placeholder="Jl. Raya Utama No.1, Kota...")

st.markdown("---")

with st.expander("🏢 Data Penerima (Klien)", expanded=True):
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        client_name = st.text_input("Nama Klien/Perusahaan", placeholder="Contoh: PT. Maju Jaya")
        client_email = st.text_input("Email Penerima", placeholder="admin@klien.com")
    with col_p2:
        client_phone = st.text_input("No. Telp Penerima", placeholder="0857xxxxxxx")
        client_address = st.text_area("Alamat Lengkap Penerima", placeholder="Jl. Sudirman No. 123, Jakarta")

st.markdown("---")

st.subheader("Detail Tagihan")
col_i1, col_i2 = st.columns(2)
with col_i1:
    invoice_number = st.text_input("Nomor Invoice", value=f"INV-{datetime.now().strftime('%Y%m%d%H%M')}")
with col_i2:
    due_date = st.date_input("Tanggal Jatuh Tempo")

item_desc = st.text_area("Deskripsi Pekerjaan / Produk")
amount = st.number_input("Total Nominal (Rp)", min_value=0, step=10000, format="%d")
notes = st.text_area("Catatan Pembayaran", value="Transfer ke Rekening BCA 123456789 a/n Nama Anda")

def create_pdf(inv_num, s_name, s_email, s_phone, s_addr, p_name, p_email, p_phone, p_addr, item, total, note):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # --- 1. WATERMARK ---
    c.saveState()
    c.setFont("Helvetica-Bold", 80)
    c.setFillColor(HexColor("#f0f0f0"), alpha=0.3)
    c.translate(width/2, height/2)
    c.rotate(45)
    c.drawCentredString(0, 0, "ORIGINAL")
    c.restoreState()
    
    # --- 2. HEADER ---
    c.setFillColor(HexColor("#1f538d")) 
    c.rect(0, height - 120, width, 120, fill=True, stroke=False)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 30)
    c.drawString(50, height - 70, "INVOICE")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 50, height - 50, s_name.upper() if s_name else "BRAND ANDA")
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 50, height - 65, f"Telp: {s_phone}")
    c.drawRightString(width - 50, height - 80, s_email)
    
    # --- 3. DETAIL PENERIMA ---
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 150, "DITAGIHKAN KEPADA:")
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, height - 170, p_name.upper() if p_name else "NAMA PENERIMA")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 185, f"Email: {p_email} | Telp: {p_phone}")
    
    text_p = c.beginText(50, height - 200)
    text_p.setFont("Helvetica", 9)
    text_p.setLeading(11)
    for line in p_addr.split('\n'):
        text_p.textLine(line)
    c.drawText(text_p)

    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(width - 50, height - 150, f"No. Invoice: #{inv_num}")
    c.drawRightString(width - 50, height - 165, f"Tgl Jatuh Tempo: {due_date}")

    # --- 4. TABEL ITEM (POSISI DINAMIS) ---
    c.setStrokeColor(HexColor("#dddddd"))
    c.line(50, height - 280, width - 50, height - 280)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 300, "DESKRIPSI PEKERJAAN")
    c.drawRightString(width - 50, height - 300, "SUBTOTAL")
    
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 325, item if item else "-")
    c.drawRightString(width - 50, height - 325, f"Rp {total:,.2f}")

    # --- 5. BOX TOTAL (DIPERTAHANKAN DI SINI) ---
    c.setFillColor(HexColor("#f4f4f4"))
    c.rect(width - 250, height - 380, 200, 45, fill=True, stroke=False)
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 15)
    c.drawString(width - 235, height - 365, "TOTAL:")
    c.drawRightString(width - 65, height - 365, f"Rp {total:,.2f}")

    # --- 6. FOOTER (SEKARANG LEBIH DEKAT KE ATAS) ---
    # Kita geser posisi Y footer dari 130 ke sekitar 420 agar tepat di bawah total
    footer_y = height - 420 
    
    c.setStrokeColor(HexColor("#eeeeee"))
    c.setDash(1, 2)
    c.line(50, footer_y, width - 50, footer_y)
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, footer_y - 20, "Catatan Pembayaran:")
    
    c.setFont("Helvetica", 9)
    # Membuat catatan bisa multi-baris
    text_n = c.beginText(50, footer_y - 35)
    text_n.setLeading(12)
    for line in note.split('\n'):
        text_n.textLine(line)
    c.drawText(text_n)
    
    # Hak Cipta paling bawah tetap ada
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(HexColor("#888888"))
    c.drawCentredString(width/2, 30, f"Invoice ini diterbitkan secara otomatis oleh {s_name}")
    
    c.save()
    buffer.seek(0)
    return buffer

st.markdown("---")
if st.button("✨ GENERATE INVOICE TEROPTIMASI", type="primary"):
    if not my_name or not client_name or not item_desc:
        st.error("Data belum lengkap!")
    else:
        pdf_data = create_pdf(invoice_number, my_name, my_email, my_phone, my_address, 
                              client_name, client_email, client_phone, client_address, 
                              item_desc, amount, notes)
        st.success("Invoice Berhasil!")
        st.download_button(label="⬇️ Download PDF Sekarang", data=pdf_data, 
                           file_name=f"Invoice_Optimized_{invoice_number}.pdf", mime="application/pdf")
