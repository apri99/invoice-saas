import streamlit as st
import io
import textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle

st.set_page_config(page_title="Invoice Pro v8.0", layout="wide", page_icon="💎")

if 'invoice_items_v6' not in st.session_state:
    st.session_state['invoice_items_v6'] = [{"desc": "", "qty": 1, "price": 0}]

st.title("💎 Invoice Ultimate SaaS")

# --- SIDEBAR: KUSTOMISASI ---
with st.sidebar:
    st.header("🎨 Branding & Warna")
    # FITUR BARU: Custom Color
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
    biz_sign = st.text_input("Nama Penandatangan", value="Apriadi Samsu")
    biz_title = st.text_input("Jabatan", value="Direktur Utama")

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
            d = r1.text_input(f"Item {i+1}", value=st.session_state['invoice_items_v6'][i]['desc'], key=f"d_v8_{i}")
            q = r2.number_input(f"Qty", min_value=1, value=st.session_state['invoice_items_v6'][i]['qty'], key=f"q_v8_{i}")
            p = r3.number_input(f"Harga", min_value=0, value=st.session_state['invoice_items_v6'][i]['price'], key=f"p_v8_{i}")
            st.session_state['invoice_items_v6'][i] = {"desc": d, "qty": q, "price": p}
            subtotal += (q * p)
            if r4.button("🗑️", key=f"del_v8_{i}"):
                st.session_state['invoice_items_v6'].pop(i); st.rerun()

    if st.button("➕ Tambah Baris"):
        st.session_state['invoice_items_v6'].append({"desc": "", "qty": 1, "price": 0}); st.rerun()

with col_pre:
    st.subheader("📑 Kalkulasi")
    tax_percent = st.number_input("Pajak (%)", value=11)
    tax_val = (tax_percent / 100) * subtotal
    grand_total = subtotal + tax_val
    st.metric("Total Pembayaran", f"Rp {grand_total:,.0f}", f"Pajak {tax_percent}%")

    if st.button("🚀 GENERATE ULTIMATE PDF", type="primary", use_container_width=True):
        buf = io.BytesIO()
        can = canvas.Canvas(buf, pagesize=A4)
        width, height = A4
        
        # --- WATERMARK ---
        if show_watermark:
            can.saveState()
            can.setFont("Helvetica-Bold", 100)
            can.setStrokeColor(colors.lightgrey)
            can.setFillColor(colors.lightgrey, alpha=0.15)
            can.translate(width/2, height/2)
            can.rotate(45)
            can.drawCentredString(0, 0, "PAID")
            can.restoreState()
        
        # Header (Warna Custom)
        can.setFillColor(colors.HexColor(main_color))
        can.rect(0, height-100, width, 100, fill=1, stroke=0)
        can.setFillColor(colors.white)
        can.setFont("Helvetica-Bold", 26); can.drawString(1*cm, height-60, "OFFICIAL INVOICE")
        
        # Pengirim
        can.setFont("Helvetica", 10)
        can.drawRightString(width-1*cm, height-40, biz_name)
        can.drawRightString(width-1*cm, height-55, biz_contact)
        wrap_s = textwrap.TextWrapper(width=35)
        lines_s = wrap_s.wrap(biz_addr)
        y_s = height-70
        for l in lines_s:
            can.drawRightString(width-1*cm, y_s, l); y_s -= 12
        
        # Penerima
        can.setFillColor(colors.black)
        can.setFont("Helvetica-Bold", 11); can.drawString(1*cm, height-130, f"DITAGIHKAN KEPADA:")
        can.setFont("Helvetica", 11); can.drawString(1*cm, height-145, f"{c_name} ({c_type})")
        wrap_c = textwrap.TextWrapper(width=55)
        lines_c = wrap_c.wrap(c_addr)
        y_c = height-160
        for l in lines_c:
            can.drawString(1*cm, y_c, l); y_c -= 12
        
        # Tabel
        table_data = [["Deskripsi Barang", "Qty", "Harga", "Total"]]
        for it in st.session_state['invoice_items_v6']:
            table_data.append([it['desc'], it['qty'], f"{it['price']:,.0f}", f"{it['qty']*it['price']:,.0f}"])
        
        t = Table(table_data, colWidths=[9*cm, 2*cm, 4*cm, 4*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor(main_color)),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        t.wrapOn(can, width, height)
        y_pos = height-260 - (len(table_data)*0.8*cm)
        t.drawOn(can, 1*cm, y_pos)
        
        # Total
        y_pos -= 40
        can.setFont("Helvetica-Bold", 11)
        can.drawRightString(width-1*cm, y_pos, f"Subtotal: Rp {subtotal:,.0f}")
        can.drawRightString(width-1*cm, y_pos-15, f"PPN {tax_percent}%: Rp {tax_val:,.0f}")
        can.setFont("Helvetica-Bold", 14)
        can.drawRightString(width-1*cm, y_pos-40, f"GRAND TOTAL: Rp {grand_total:,.0f}")
        
        # Tanda Tangan
        y_sign = y_pos - 100
        can.setFont("Helvetica", 10); can.drawString(width-7*cm, y_sign, "Hormat Kami,")
        can.setFont("Helvetica-Bold", 11); can.drawString(width-7*cm, y_sign-60, biz_sign)
        can.setFont("Helvetica-Oblique", 9); can.drawString(width-7*cm, y_sign-75, biz_title)
        
        can.save()
        st.download_button("⬇️ Download Final Invoice", data=buf.getvalue(), file_name=f"Invoice_{c_name}.pdf", use_container_width=True)
