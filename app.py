import streamlit as st
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="Invoice Pro v4.1", layout="wide")

# --- INISIALISASI DENGAN NAMA BARU (daftar_barang) ---
# Menggunakan nama unik agar tidak bentrok dengan method sistem .items()
if 'daftar_barang' not in st.session_state:
    st.session_state['daftar_barang'] = [{"nama": "", "harga": 0, "qty": 1}]

st.title("🧾 Invoice Generator Pro")

with st.sidebar:
    st.header("👤 Pengirim")
    my_name = st.text_input("Nama Bisnis", value="CV. MAJU JAYA")
    if st.button("🚨 Reset Aplikasi / Clear Error"):
        st.session_state.clear()
        st.session_state['daftar_barang'] = [{"nama": "", "harga": 0, "qty": 1}]
        st.rerun()

col1, col2 = st.columns([1.5, 1])

with col1:
    c_name = st.text_input("Nama Klien")
    st.subheader("💰 Detail Tagihan")
    
    total_tagihan = 0
    # Mengambil data dari daftar_barang
    items_list = st.session_state['daftar_barang']
    
    for i in range(len(items_list)):
        with st.container(border=True):
            ca, cb, cc, cd = st.columns([3, 1.5, 1, 0.5])
            
            # Input data
            n = ca.text_input(f"Item {i+1}", value=items_list[i]['nama'], key=f"nm_{i}")
            h = cb.number_input(f"Harga", value=int(items_list[i]['harga']), step=1000, key=f"hr_{i}")
            q = cc.number_input(f"Qty", value=int(items_list[i]['qty']), min_value=1, key=f"qt_{i}")
            
            # Simpan balik ke state
            st.session_state['daftar_barang'][i] = {"nama": n, "harga": h, "qty": q}
            
            line_total = h * q
            total_tagihan += line_total
            
            if cd.button("🗑️", key=f"hps_{i}"):
                st.session_state['daftar_barang'].pop(i)
                st.rerun()
            
            st.caption(f"Subtotal: Rp {line_total:,.0f}")

    if st.button("➕ Tambah Baris"):
        st.session_state['daftar_barang'].append({"nama": "", "harga": 0, "qty": 1})
        st.rerun()

    st.success(f"### Grand Total: Rp {total_tagihan:,.0f}")

with col2:
    st.subheader("👀 Preview")
    st.write(f"Klien: {c_name if c_name else '-'}")
    if st.button("🚀 DOWNLOAD PDF", type="primary", use_container_width=True):
        buf = io.BytesIO()
        pdf = canvas.Canvas(buf, pagesize=A4)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 800, f"INVOICE: {my_name}")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, 780, f"Kepada: {c_name}")
        pdf.drawString(50, 760, f"Total Bayar: Rp {total_tagihan:,.0f}")
        pdf.save()
        st.download_button("⬇️ Simpan PDF", data=buf.getvalue(), file_name="invoice.pdf", use_container_width=True)
