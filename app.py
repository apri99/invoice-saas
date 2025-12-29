import streamlit as st
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="Invoice Pro v4.0", layout="wide")

# --- KUNCI UTAMA: Inisialisasi Session State ---
# Ini mencegah TypeError: 'NoneType' object is not iterable
if 'items' not in st.session_state:
    st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]

st.title("🧾 Invoice Generator Pro")

with st.sidebar:
    st.header("👤 Pengirim")
    my_name = st.text_input("Nama Bisnis", value="CV. MAJU JAYA")
    if st.button("🚨 Reset Aplikasi / Clear Error"):
        st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]
        st.rerun()

col1, col2 = st.columns([1.5, 1])

with col1:
    c_name = st.text_input("Nama Klien")
    st.subheader("💰 Daftar Barang / Jasa")
    
    total_tagihan = 0
    # Menggunakan index range agar looping selalu aman
    for i in range(len(st.session_state.items)):
        with st.container(border=True):
            ca, cb, cc, cd = st.columns([3, 1.5, 1, 0.5])
            
            d = ca.text_input(f"Barang #{i+1}", value=st.session_state.items[i]['desc'], key=f"d_v4_{i}")
            p = cb.number_input(f"Harga", value=int(st.session_state.items[i]['price']), step=1000, key=f"p_v4_{i}")
            q = cc.number_input(f"Qty", value=int(st.session_state.items[i]['qty']), min_value=1, key=f"q_v4_{i}")
            
            st.session_state.items[i] = {"desc": d, "price": p, "qty": q}
            total_tagihan += (p * q)
            
            if cd.button("🗑️", key=f"del_v4_{i}"):
                st.session_state.items.pop(i)
                st.rerun()

    if st.button("➕ Tambah Baris"):
        st.session_state.items.append({"desc": "", "price": 0, "qty": 1})
        st.rerun()

    st.success(f"### Grand Total: Rp {total_tagihan:,.0f}")

with col2:
    st.subheader("👀 Preview")
    st.write(f"Klien: {c_name if c_name else '-'}")
    if st.button("🚀 DOWNLOAD PDF", type="primary", use_container_width=True):
        buf = io.BytesIO()
        can = canvas.Canvas(buf, pagesize=A4)
        can.drawString(100, 800, f"INVOICE: {my_name}")
        can.drawString(100, 780, f"Total: Rp {total_tagihan:,.0f}")
        can.save()
        st.download_button("⬇️ Simpan PDF", data=buf.getvalue(), file_name="invoice.pdf")
