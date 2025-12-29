import streamlit as st
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="Invoice Pro v5.0", layout="wide")

# --- GUNAKAN NAMA UNIK AGAR TIDAK BENTROK ---
if 'data_tagihan' not in st.session_state:
    st.session_state['data_tagihan'] = [{"nama_item": "", "harga_satuan": 0, "jumlah": 1}]

st.title("🧾 Invoice Generator Pro")

with st.sidebar:
    st.header("👤 Pengirim")
    nama_bisnis = st.text_input("Nama Bisnis", value="CV. MAJU JAYA")
    st.divider()
    # Tombol Reset untuk membersihkan memori yang nyangkut
    if st.button("🚨 Bersihkan Error / Reset"):
        st.session_state.clear()
        st.rerun()

col1, col2 = st.columns([1.5, 1])

with col1:
    klien = st.text_input("Nama Klien")
    st.subheader("💰 Daftar Barang")
    
    total_bayar = 0
    # Ambil data dari memori
    list_belanja = st.session_state['data_tagihan']
    
    for i in range(len(list_belanja)):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 1.5, 1, 0.5])
            
            # Input data dengan nama variabel yang baru
            n = c1.text_input(f"Barang {i+1}", value=list_belanja[i]['nama_item'], key=f"n_v5_{i}")
            h = c2.number_input(f"Harga", value=int(list_belanja[i]['harga_satuan']), step=1000, key=f"h_v5_{i}")
            q = c3.number_input(f"Qty", value=int(list_belanja[i]['jumlah']), min_value=1, key=f"q_v5_{i}")
            
            # Simpan balik
            st.session_state['data_tagihan'][i] = {"nama_item": n, "harga_satuan": h, "jumlah": q}
            
            sub = h * q
            total_bayar += sub
            
            if c4.button("🗑️", key=f"hapus_v5_{i}"):
                st.session_state['data_tagihan'].pop(i)
                st.rerun()
            
            st.caption(f"Subtotal: Rp {sub:,.0f}")

    if st.button("➕ Tambah Barang"):
        st.session_state['data_tagihan'].append({"nama_item": "", "harga_satuan": 0, "jumlah": 1})
        st.rerun()

    st.success(f"### Total Akhir: Rp {total_bayar:,.0f}")

with col2:
    st.subheader("👀 Preview")
    st.write(f"Klien: {klien}")
    if st.button("🚀 CETAK PDF", type="primary", use_container_width=True):
        buf = io.BytesIO()
        pdf = canvas.Canvas(buf, pagesize=A4)
        pdf.drawString(100, 800, f"INVOICE: {nama_bisnis}")
        pdf.drawString(100, 780, f"Kepada: {klien}")
        pdf.drawString(100, 760, f"Total: Rp {total_bayar:,.0f}")
        pdf.save()
        st.download_button("⬇️ Download PDF", data=buf.getvalue(), file_name="invoice.pdf")
