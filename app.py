import streamlit as st
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="Invoice Pro v3.2", layout="wide")

# --- INISIALISASI SESSION STATE (WAJIB PALING ATAS) ---
# Ini untuk mencegah error "TypeError" di baris looping barang
if 'items' not in st.session_state:
    st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]

st.title("🧾 Invoice Generator Pro")

# --- SIDEBAR ---
with st.sidebar:
    st.header("👤 Identitas Pengirim")
    my_name = st.text_input("Nama Bisnis", value="CV. MAJU JAYA")
    st.divider()
    # Tombol Reset untuk membersihkan sinkronisasi data yang macet
    if st.button("🚨 Reset Aplikasi / Clear Error"):
        st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]
        st.rerun()

# --- INPUT AREA ---
col1, col2 = st.columns([1.5, 1])

with col1:
    c_name = st.text_input("Nama Klien", placeholder="Contoh: PT. Maju Terus")
    st.subheader("💰 Daftar Barang / Jasa")
    
    total_akhir = 0
    # Proteksi: Pastikan items adalah list
    if isinstance(st.session_state.items, list):
        for i in range(len(st.session_state.items)):
            with st.container(border=True):
                ca, cb, cc, cd = st.columns([3, 1.5, 1, 0.5])
                
                # Input menggunakan key unik agar tidak tabrakan memori
                d = ca.text_input(f"Deskripsi #{i+1}", value=st.session_state.items[i]['desc'], key=f"d_v32_{i}")
                p = cb.number_input(f"Harga", value=int(st.session_state.items[i]['price']), step=1000, key=f"p_v32_{i}")
                q = cc.number_input(f"Qty", value=int(st.session_state.items[i]['qty']), min_value=1, key=f"q_v32_{i}")
                
                st.session_state.items[i] = {"desc": d, "price": p, "qty": q}
                total_akhir += (p * q)
                
                if cd.button("🗑️", key=f"del_v32_{i}"):
                    st.session_state.items.pop(i)
                    st.rerun()

    if st.button("➕ Tambah Baris"):
        st.session_state.items.append({"desc": "", "price": 0, "qty": 1})
        st.rerun()

    st.success(f"### Grand Total: Rp {total_akhir:,.0f}")

with col2:
    st.subheader("👀 Preview")
    with st.container(border=True):
        st.write(f"**Penerima:** {c_name if c_name else '-'}")
        st.write(f"**Total Item:** {len(st.session_state.items)}")
        if st.button("🚀 DOWNLOAD PDF", type="primary", use_container_width=True):
            buf = io.BytesIO()
            can = canvas.Canvas(buf, pagesize=A4)
            can.drawString(100, 800, f"INVOICE: {my_name}")
            can.drawString(100, 780, f"Kepada: {c_name}")
            can.drawString(100, 760, f"Total: Rp {total_akhir:,.0f}")
            can.save()
            st.download_button("⬇️ Simpan PDF", data=buf.getvalue(), file_name=f"Invoice_{c_name}.pdf")
