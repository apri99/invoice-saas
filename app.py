import streamlit as st
import io
import textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle

st.set_page_config(page_title="Invoice Ultimate v8.6", layout="wide", page_icon="💎")

if 'invoice_items_v6' not in st.session_state:
    st.session_state['invoice_items_v6'] = [{"desc": "", "qty": 1, "price": 0}]

st.title("💎 Invoice Ultimate SaaS")

with st.sidebar:
    st.header("🎨 Branding & Warna")
    main_color = st.color_picker("Pilih Warna Header", "#0D47A1")
    show_watermark = st.checkbox("Tampilkan Watermark 'PAID'", value=True)
    
    st.divider()
    st.header("👤 Identitas Pengirim")
    s_type = st.radio("Entitas", ["Perusahaan", "Perorangan"], horizontal=True)
    biz_name = st.text_input(f"Nama {s_type}", value="CV. MAJU JAYA")
    biz_contact = st.text_input("WhatsApp", value="08123456789")
    biz_addr = st.text_area("Alamat Lengkap", value="Jl. Jendral Sudirman No. 1")
    
    st.divider()
    st.header("✍️ Pengesahan")
    # PERUBAHAN DISINI: Mengganti nama default menjadi John Doe
    biz_sign = st.text_input("Nama Penandatangan", value="John Doe")
    biz_title = st.text_input("Jabatan", value="Manager Operasional")

col_in, col_pre = st.columns([1.5, 1])

with col_in:
    st.subheader("📩 Detail Penerima")
    with st.container(border=True):
        c_type = st.radio("Tipe Penerima", ["Perusahaan", "Perorangan"], horizontal=True)
        c_name = st.text_input(f"Nama {c_type}")
        c_addr = st.text_area("Alamat Penerima")

    st.subheader("💰 Daftar Barang")
    subtotal = 0
    for i in range(len(st.session_state['invoice_items_v6'])):
        with st.container(border=True):
            r1, r2, r3, r4 = st.columns([3, 1, 2, 0.5])
            d = r1.text_input(f"Item {i+1}", value=st.session_state['invoice_items_v6'][i]['desc'], key=f"d_v86_{i}")
            q = r2.number_input(f"Qty", min_value=1, value=st.session_state['invoice_items_v6'][i]['qty'], key=f"q_v86_{i}")
            p = r3.number_input(f"Harga", min_value=0, value=st.session_state['invoice_items_v6'][i]['price'], key=f"p_v86_{i}")
            st.session_state['invoice_items_v6'][i] = {"desc": d, "qty": q, "price": p}
            subtotal += (q * p)
            if r4.button("🗑️", key=f"del_v86_{i}"):
                st.session_state['invoice_items_v6'].pop(i); st.rerun()

    if st.button("➕ Tambah Baris"):
        st.session_state['invoice_items_v6'].append({"desc": "", "qty": 1, "price": 0}); st.rerun()

with col_pre:
    st.subheader("📑 Kalkulasi")
    tax_percent = st.number_input("Pajak (%)", value=11)
    tax_val = (tax_percent / 100) * subtotal
    grand_total = subtotal + tax_val
    st.metric("Total Pembayaran", f"Rp {grand_total:,.0f}")

    if st.button("🚀 GENERATE PDF", type="primary", use_container_width=True):
        buf = io.BytesIO()
        can = canvas.Canvas(buf, pagesize=A4)
        width, height = A4
        
        if show_watermark:
            can.saveState()
            can.setFont("Helvetica-Bold", 100); can.setFillColor(colors.lightgrey, alpha=0.15)
            can.translate(width/2, height/2); can.rotate(45)
            can.drawCentredString(0, 0, "PAID"); can.restoreState()
        
        can.setFillColor(colors.HexColor(main_color)); can.rect(0, height-100, width, 100, fill=1, stroke=0)
        can.setFillColor(colors.white); can.setFont("Helvetica-Bold", 26); can.drawString(1*cm, height-60, "OFFICIAL INVOICE")
        
        can.setFont("Helvetica", 10); can.drawRightString(width-1*cm, height-40, biz_name)
        can.drawRightString(width-1*cm, height-55, biz_contact)
        wrap_s = textwrap.TextWrapper(width=35)
        for line in wrap_s.wrap(biz_addr):
            can.drawRightString(width-1*cm, height-70, line); height -= 12
        
        height = A4[1] # Reset height for receiver section
        can.setFillColor(colors.black); can.setFont("Helvetica-Bold", 11); can.drawString(1*cm, height-130, "TAGIHAN KEPADA:")
        can.setFont("Helvetica", 11); can.drawString(1*cm, height-145, f"{c_name} ({c_type})")
        
        data = [["Deskripsi", "Qty", "Harga", "Total"]]
        for it in st.session_state['invoice_items_v6']:
            data.append([it['desc'], it['qty'], f"{it['price']:,.0f}", f"{it['qty']*it['price']:,.0f}"])
        
        t = Table(data, colWidths=[9*cm, 2*cm, 4*cm, 4*cm])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(main_color)),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.5,colors.grey)]))
        t.wrapOn(can, width, height)
        y_pos = height-260 - (len(data)*0.8*cm); t.drawOn(can, 1*cm, y_pos)
        
        y_pos -= 40; can.setFont("Helvetica-Bold", 14); can.drawRightString(width-1*cm, y_pos, f"TOTAL: Rp {grand_total:,.0f}")
        
        y_sign = y_pos - 80; can.setFont("Helvetica", 10); can.drawString(width-7*cm, y_sign, "Hormat Kami,")
        can.setFont("Helvetica-Bold", 11); can.drawString(width-7*cm, y_sign-50, biz_sign)
        can.setFont("Helvetica-Oblique", 9); can.drawString(width-7*cm, y_sign-65, biz_title)
        
        can.save()
        st.download_button("⬇️ Download PDF", data=buf.getvalue(), file_name=f"Invoice_{c_name}.pdf", use_container_width=True)
