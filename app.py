import streamlit as st
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle

st.set_page_config(page_title="Invoice Enterprise", layout="wide")

# Proteksi Session State
if 'invoice_items_v6' not in st.session_state:
    st.session_state['invoice_items_v6'] = [{"desc": "", "qty": 1, "price": 0}]

st.title("💼 Official Invoice Generator")

# --- SIDEBAR: IDENTITAS PENGIRIM ---
with st.sidebar:
    st.header("👤 Pengirim")
    s_type = st.radio("Tipe", ["Perusahaan", "Perorangan"], horizontal=True)
    biz_name = st.text_input(f"Nama {s_type}", value="CV. MAJU JAYA")
    biz_contact = st.text_input("WhatsApp", value="08123456789")
    biz_addr = st.text_area("Alamat Pengirim", value="Jl. Jendral Sudirman No. 1")

# --- INPUT PENERIMA ---
col_in, col_pre = st.columns([1.5, 1])
with col_in:
    st.subheader("📩 Penerima")
    c_type = st.radio("Tipe Penerima", ["Perusahaan", "Perorangan"], horizontal=True)
    c_name = st.text_input(f"Nama {c_type}")
    c_addr = st.text_area("Alamat Penerima")

    st.subheader("💰 Barang/Jasa")
    subtotal = 0
    for i in range(len(st.session_state['invoice_items_v6'])):
        with st.container(border=True):
            r1, r2, r3, r4 = st.columns([3, 1, 2, 0.5])
            d = r1.text_input(f"Item {i+1}", value=st.session_state['invoice_items_v6'][i]['desc'], key=f"d_{i}")
            q = r2.number_input(f"Qty", min_value=1, value=st.session_state['invoice_items_v6'][i]['qty'], key=f"q_{i}")
            p = r3.number_input(f"Harga", min_value=0, value=st.session_state['invoice_items_v6'][i]['price'], key=f"p_{i}")
            st.session_state['invoice_items_v6'][i] = {"desc": d, "qty": q, "price": p}
            subtotal += (q * p)
            if r4.button("🗑️", key=f"del_{i}"):
                st.session_state['invoice_items_v6'].pop(i); st.rerun()

    if st.button("➕ Tambah Baris"):
        st.session_state['invoice_items_v6'].append({"desc": "", "qty": 1, "price": 0}); st.rerun()

# --- KALKULASI TOTAL ---
tax = 0.11 * subtotal
grand_total = subtotal + tax

with col_pre:
    st.subheader("🚀 Download")
    if st.button("GENERATE PDF SEKARANG", type="primary", use_container_width=True):
        buf = io.BytesIO()
        can = canvas.Canvas(buf, pagesize=A4)
        width, height = A4
        
        # Header Biru
        can.setFillColorRGB(0.1, 0.3, 0.5)
        can.rect(0, height-100, width, 100, fill=1, stroke=0)
        can.setFillColor(colors.white)
        can.setFont("Helvetica-Bold", 24); can.drawString(1*cm, height-60, "OFFICIAL INVOICE")
        
        # Identitas Pengirim (Kanan Atas)
        can.setFont("Helvetica", 10)
        can.drawRightString(width-1*cm, height-40, biz_name)
        can.drawRightString(width-1*cm, height-55, biz_contact)
        can.drawRightString(width-1*cm, height-70, biz_addr[:40]) # Alamat dipotong jika terlalu panjang
        
        # Identitas Penerima
        can.setFillColor(colors.black)
        can.setFont("Helvetica-Bold", 11); can.drawString(1*cm, height-130, f"DITAGIHKAN KEPADA ({c_type}):")
        can.setFont("Helvetica", 11); can.drawString(1*cm, height-145, c_name); can.drawString(1*cm, height-160, c_addr)
        
        # Tabel
        data = [["Deskripsi", "Qty", "Harga", "Total"]]
        for it in st.session_state['invoice_items_v6']:
            data.append([it['desc'], it['qty'], f"{it['price']:,.0f}", f"{it['qty']*it['price']:,.0f}"])
        
        t = Table(data, colWidths=[9*cm, 2*cm, 4*cm, 4*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0D47A1")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        t.wrapOn(can, width, height)
        y_pos = height-250 - (len(data)*0.8*cm)
        t.drawOn(can, 1*cm, y_pos)
        
        # TOTALS (Di bawah tabel)
        y_pos -= 30
        can.setFont("Helvetica-Bold", 11)
        can.drawRightString(width-1*cm, y_pos, f"Subtotal: Rp {subtotal:,.0f}")
        can.drawRightString(width-1*cm, y_pos-15, f"PPN 11%: Rp {tax:,.0f}")
        can.setFont("Helvetica-Bold", 14)
        can.drawRightString(width-1*cm, y_pos-40, f"GRAND TOTAL: Rp {grand_total:,.0f}")
        
        can.save()
        st.download_button("⬇️ Simpan PDF", data=buf.getvalue(), file_name="Invoice_Lengkap.pdf", use_container_width=True)
