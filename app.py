import streamlit as st
import io
import textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle

st.set_page_config(page_title="Invoice Ultimate v8.1", layout="wide", page_icon="💎")

# Inisialisasi Data
if 'invoice_items_v6' not in st.session_state:
    st.session_state['invoice_items_v6'] = [{"desc": "", "qty": 1, "price": 0}]

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135706.png", width=100)
    st.title("Admin Panel")
    menu = st.selectbox("Menu", ["Buat Invoice", "Pengaturan Branding", "Bantuan"])
    
    st.divider()
    if menu == "Buat Invoice":
        st.header("🎨 Kustomisasi")
        main_color = st.color_picker("Warna Tema Invoice", "#0D47A1")
        show_paid = st.checkbox("Gunakan Watermark PAID", value=True)
        
        st.header("👤 Pengirim")
        s_type = st.radio("Entitas", ["Perusahaan", "Perorangan"], horizontal=True)
        biz_name = st.text_input(f"Nama {s_type}", value="CV. MAJU JAYA")
        biz_contact = st.text_input("WhatsApp", value="08123456789")
        biz_addr = st.text_area("Alamat Lengkap", value="Jl. Jendral Sudirman No. 1")
        
        st.header("✍️ Tanda Tangan")
        biz_sign = st.text_input("Nama Penandatangan", value="Apriadi Samsu")
        biz_title = st.text_input("Jabatan", value="Direktur Utama")

# --- MAIN CONTENT ---
if menu == "Buat Invoice":
    st.title("🧾 Generator Invoice Premium")
    
    col_in, col_pre = st.columns([1.5, 1])
    
    with col_in:
        st.subheader("📩 Detail Penerima")
        with st.container(border=True):
            c_type = st.radio("Tipe Penerima", ["Perusahaan", "Perorangan"], horizontal=True)
            c_name = st.text_input(f"Nama {c_type}")
            c_addr = st.text_area("Alamat Penerima")

        st.subheader("💰 Detail Pesanan")
        subtotal = 0
        for i in range(len(st.session_state['invoice_items_v6'])):
            with st.container(border=True):
                r1, r2, r3, r4 = st.columns([3, 1, 2, 0.5])
                d = r1.text_input(f"Item {i+1}", value=st.session_state['invoice_items_v6'][i]['desc'], key=f"d_v81_{i}")
                q = r2.number_input(f"Qty", min_value=1, value=st.session_state['invoice_items_v6'][i]['qty'], key=f"q_v81_{i}")
                p = r3.number_input(f"Harga", min_value=0, value=st.session_state['invoice_items_v6'][i]['price'], key=f"p_v81_{i}")
                st.session_state['invoice_items_v6'][i] = {"desc": d, "qty": q, "price": p}
                subtotal += (q * p)
                if r4.button("🗑️", key=f"del_v81_{i}"):
                    st.session_state['invoice_items_v6'].pop(i); st.rerun()

        if st.button("➕ Tambah Baris Barang"):
            st.session_state['invoice_items_v6'].append({"desc": "", "qty": 1, "price": 0}); st.rerun()

    with col_pre:
        st.subheader("📊 Ringkasan & Cetak")
        tax_pct = st.number_input("PPN (%)", value=11)
        tax_val = (tax_pct / 100) * subtotal
        grand_total = subtotal + tax_val
        
        st.metric("Grand Total", f"Rp {grand_total:,.0f}")
        
        if st.button("🔥 GENERATE PDF", type="primary", use_container_width=True):
            buf = io.BytesIO()
            can = canvas.Canvas(buf, pagesize=A4)
            w, h = A4
            
            if show_paid:
                can.saveState()
                can.setFont("Helvetica-Bold", 100); can.setFillColor(colors.lightgrey, alpha=0.15)
                can.translate(w/2, h/2); can.rotate(45)
                can.drawCentredString(0, 0, "PAID"); can.restoreState()
            
            can.setFillColor(colors.HexColor(main_color)); can.rect(0, h-100, w, 100, fill=1, stroke=0)
            can.setFillColor(colors.white); can.setFont("Helvetica-Bold", 26); can.drawString(1*cm, h-60, "INVOICE")
            
            can.setFont("Helvetica", 10); can.drawRightString(w-1*cm, h-40, biz_name)
            can.drawRightString(w-1*cm, h-55, biz_contact)
            
            # Wrap Alamat
            y_s = h-70
            for line in textwrap.wrap(biz_addr, width=35):
                can.drawRightString(w-1*cm, y_s, line); y_s -= 12
            
            can.setFillColor(colors.black); can.setFont("Helvetica-Bold", 11); can.drawString(1*cm, h-130, "PENERIMA:")
            can.setFont("Helvetica", 11); can.drawString(1*cm, h-145, f"{c_name} ({c_type})")
            y_c = h-160
            for line in textwrap.wrap(c_addr, width=55):
                can.drawString(1*cm, y_c, line); y_c -= 12
            
            data = [["Item", "Qty", "Harga", "Total"]]
            for it in st.session_state['invoice_items_v6']:
                data.append([it['desc'], it['qty'], f"{it['price']:,.0f}", f"{it['qty']*it['price']:,.0f}"])
            
            t = Table(data, colWidths=[9*cm, 2*cm, 4*cm, 4*cm])
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(main_color)),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.5,colors.grey)]))
            t.wrapOn(can, w, h)
            y_p = h-260 - (len(data)*0.8*cm); t.drawOn(can, 1*cm, y_p)
            
            y_p -= 40; can.setFont("Helvetica-Bold", 12); can.drawRightString(w-1*cm, y_p, f"TOTAL: Rp {grand_total:,.0f}")
            
            # Sign
            y_si = y_p - 100; can.setFont("Helvetica", 10); can.drawString(w-7*cm, y_si, "Hormat Kami,")
            can.setFont("Helvetica-Bold", 11); can.drawString(w-7*cm, y_si-60, biz_sign)
            can.setFont("Helvetica-Oblique", 9); can.drawString(w-7*cm, y_si-75, biz_title)
            
            can.save()
            st.download_button("⬇️ Download PDF", data=buf.getvalue(), file_name=f"Inv_{c_name}.pdf", use_container_width=True)

    st.divider()
    st.caption(f"© 2025 {biz_name} | Powered by Apri SaaS Technology")

elif menu == "Pengaturan Branding":
    st.info("Fitur Upload Logo akan segera hadir di versi selanjutnya.")

elif menu == "Bantuan":
    st.write("Hubungi support di: support@aprisaas.com")
