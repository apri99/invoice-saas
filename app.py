import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
import io
from datetime import datetime

st.set_page_config(page_title="Invoice Generator Pro", page_icon="🧾", layout="centered")

st.title("🚀 Invoice Generator Pro")
st.markdown("Buat invoice profesional dalam hitungan detik. Gratis untuk MicroSaaS demo.")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Nama Klien / Perusahaan", placeholder="Contoh: PT. Maju Mundur")
    email_client = st.text_input("Email Klien (Opsional)", placeholder="email@klien.com")
with col2:
    invoice_number = st.text_input("Nomor Invoice", value=f"INV-{datetime.now().strftime('%Y%m%d')}")
    due_date = st.date_input("Jatuh Tempo")

item_desc = st.text_area("Deskripsi Pekerjaan / Produk", placeholder="Jasa Pembuatan Website, Konsultasi, dll.")
amount = st.number_input("Total Nominal (Rp)", min_value=0, step=10000, format="%d")
notes = st.text_area("Catatan Tambahan", value="Harap transfer pembayaran dalam waktu 3 hari kerja.")

def create_pdf(client, item, total, note, inv_num):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Desain Header Biru
    c.setFillColor(HexColor("#1f538d")) 
    c.rect(0, height - 120, width, 120, fill=True, stroke=False)
    
    # Text Header
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 30)
    c.drawString(50, height - 70, "INVOICE")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 95, f"No: #{inv_num}")
    c.drawRightString(width - 50, height - 70, "YOUR SAAS BRAND")
    
    # Info Klien
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 160, "KEPADA:")
    c.setFont("Helvetica", 14)
    c.drawString(50, height - 180, client)
    c.setStrokeColor(HexColor("#dddddd"))
    c.line(50, height - 200, width - 50, height - 200)

    # Item & Total
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 230, "DESKRIPSI")
    c.drawRightString(width - 50, height - 230, "JUMLAH")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 260, item)
    c.drawRightString(width - 50, height - 260, f"Rp {total:,.2f}")
    
    c.setFillColor(HexColor("#f0f0f0"))
    c.rect(width - 250, height - 350, 200, 40, fill=True, stroke=False)
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(width - 230, height - 335, "TOTAL:")
    c.drawRightString(width - 70, height - 335, f"Rp {total:,.2f}")

    # Footer
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#555555"))
    c.drawString(50, 100, "Catatan:")
    c.drawString(50, 85, note)
    
    c.save()
    buffer.seek(0)
    return buffer

st.markdown("---")
if st.button("✨ Buat Invoice Sekarang", type="primary"):
    if not client_name or not item_desc or amount == 0:
        st.error("Mohon lengkapi data.")
    else:
        pdf_data = create_pdf(client_name, item_desc, amount, notes, invoice_number)
        st.success("Berhasil!")
        st.download_button(label="⬇️ Download PDF", data=pdf_data, file_name="invoice.pdf", mime="application/pdf")
