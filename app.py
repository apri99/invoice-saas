import streamlit as st
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle

st.set_page_config(page_title="Invoice Pro v6.2", layout="wide", page_icon="🏢")

# INISIALISASI SESSION STATE (Anti-TypeError)
if 'invoice_items_v6' not in st.session_state:
    st.session_state['invoice_items_v6'] = [{"desc": "", "qty": 1, "price": 0}]

st.title("💼 Invoice SaaS - Enterprise Edition")

with st.sidebar:
    st.header("👤 Identitas Pengirim")
    s_type = st.radio("Tipe Pengirim", ["Perusahaan", "Perorangan"], horizontal=True)
    biz_name = st.text_input(f"Nama {s_type}", value="CV. MAJU JAYA")
    biz_contact = st.text_input("Kontak / WA", value="08123456789")
    
    if st.button("🚨 Reset Form / Hapus Error"):
        st.session_state['invoice_items_v6'] = [{"desc": "", "qty": 1, "price": 0}]
        st.rerun()

col_in, col_pre = st.columns([1.5, 1])

with col_in:
    st.subheader("📩 Detail Penerima")
    with st.container(border=True):
        c_type = st.radio("Tipe Penerima", ["Perusahaan", "Perorangan"], horizontal=True)
        c_name = st.text_input(f"Nama {c_type}")
        c_addr = st.text_area("Alamat Penerima")

    st.subheader("💰 Daftar Barang / Jasa")
    total_subtotal = 0
    
    # Looping yang aman
    for i in range(len(st.session_state['invoice_items_v6'])):
        with st.container(border=True):
            r1, r2, r3, r4 = st.columns([3, 1, 2, 0.5])
            d = r1.text_input(f"Item #{i+1}", value=st.session_state['invoice_items_v6'][i]['desc'], key=f"d_v6_{i}")
            q = r2.number_input(f"Qty", min_value=1, value=st.session_state['invoice_items_v6'][i]['qty'], key=f"q_v6_{i}")
            p = r3.number_input(f"Harga", min_value=0, value=st.session_state['invoice_items_v6'][i]['price'], step=1000, key=f"p_v6_{i}")
            
            st.session_state['invoice_items_v6'][i] = {"desc": d, "qty": q, "price": p}
            total_subtotal += (q * p)
            
            if r4.button("🗑️", key=f"del_v6_{i}"):
                st.session_state['invoice_items_v6'].pop(i)
                st.rerun()

    if st.button("➕ Tambah Baris"):
        st.session_state['invoice_items_v6'].append({"desc": "", "qty": 1, "price": 0})
        st.rerun()

with col_pre:
    st.subheader("👀 Preview & Cetak")
    st.info(f"Grand Total: Rp {total_subtotal:,.0f}")
    
    if st.button("🚀 GENERATE PDF PRO", type="primary", use_container_width=True):
        buf = io.BytesIO()
        can = canvas.Canvas(buf, pagesize=A4)
        width, height = A4
        
        # Header Biru Mewah
        can.setFillColorRGB(0.1, 0.3, 0.5)
        can.rect(0, height-100, width, 100, fill=1, stroke=0)
        can.setFillColor(colors.white)
        can.setFont("Helvetica-Bold", 24)
        can.drawString(1*cm, height-60, "OFFICIAL INVOICE")
        
        # Isi PDF
        can.setFillColor(colors.black)
        can.setFont("Helvetica-Bold", 11)
        can.drawString(1*cm, height-130, f"DITAGIHKAN KEPADA ({c_type}):")
        can.setFont("Helvetica", 11)
        can.drawString(1*cm, height-145, c_name if c_name else "-")
        can.drawString(1*cm, height-160, c_addr if c_addr else "-")
        
        # Tabel
        table_data = [["Deskripsi", "Qty", "Harga", "Total"]]
        for item in st.session_state['invoice_items_v6']:
            table_data.append([item['desc'], item['qty'], f"{item['price']:,.0f}", f"{item['qty']*item['price']:,.0f}"])
        
        t = Table(table_data, colWidths=[9*cm, 2*cm, 4*cm, 4*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0D47A1")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        t.wrapOn(can, width, height)
        t.drawOn(can, 1*cm, height-250 - (len(table_data)*0.8*cm))
        
        can.save()
        st.download_button("⬇️ Simpan PDF", data=buf.getvalue(), file_name=f"Invoice_{c_name}.pdf", use_container_width=True)
