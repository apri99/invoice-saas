import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
import io, textwrap

st.set_page_config(page_title="Invoice Pro v3.0", layout="wide")

# --- SISTEM PENYEMBUHAN OTOMATIS (MENCEGAH ERROR MERAH) ---
if 'items' not in st.session_state or not isinstance(st.session_state.items, list):
    st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]

# Pastikan isi list tidak None
if len(st.session_state.items) == 0 or st.session_state.items[0] is None:
    st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]

st.title("🧾 Invoice Generator Pro")

with st.sidebar:
    st.header("👤 Identitas Pengirim")
    my_name = st.text_input("Nama Bisnis", value="CV. MAJU JAYA")
    st.divider()
    # Tombol Reset Paksa jika masih ada kendala
    if st.button("🚨 Reset Total (Hapus Semua Error)"):
        st.session_state.clear()
        st.rerun()

col1, col2 = st.columns([1.5, 1])

with col1:
    client_name = st.text_input("Nama Klien", placeholder="Contoh: PT. Maju Terus")
    st.subheader("💰 Daftar Barang / Jasa")
    
    grand_subtotal = 0
    # Proteksi Looping agar tidak TypeError
    try:
        for i in range(len(st.session_state.items)):
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3, 1.5, 1, 0.5])
                
                # Input dengan key baru (v30) untuk memutus memori lama
                d = c1.text_input(f"Deskripsi #{i+1}", value=st.session_state.items[i].get('desc', ""), key=f"d_v30_{i}")
                p = c2.number_input(f"Harga", value=int(st.session_state.items[i].get('price', 0)), step=1000, key=f"p_v30_{i}")
                q = c3.number_input(f"Qty", value=int(st.session_state.items[i].get('qty', 1)), min_value=1, key=f"q_v30_{i}")
                
                st.session_state.items[i] = {"desc": d, "price": p, "qty": q}
                line_total = p * q
                grand_subtotal += line_total
                
                if c4.button("🗑️", key=f"del_v30_{i}"):
                    if len(st.session_state.items) > 1:
                        st.session_state.items.pop(i)
                        st.rerun()
                st.caption(f"Subtotal: Rp {line_total:,.0f}")
    except:
        st.session_state.items = [{"desc": "", "price": 0, "qty": 1}]
        st.rerun()

    if st.button("➕ Tambah Baris Baru"):
        st.session_state.items.append({"desc": "", "price": 0, "qty": 1})
        st.rerun()

    use_tax = st.checkbox("Gunakan PPN 11%")
    tax_amt = (0.11 * grand_subtotal) if use_tax else 0
    total_final = grand_subtotal + tax_amt
    st.success(f"### Grand Total Akhir: Rp {total_final:,.0f}")

with col2:
    st.subheader("👀 Preview")
    with st.container(border=True):
        st.write(f"**Klien:** {client_name if client_name else '-'}")
        st.write(f"**Total Item:** {len(st.session_state.items)}")
        st.divider()
        st.write(f"### Rp {total_final:,.0f}")
        
        if st.button("🚀 DOWNLOAD PDF", type="primary", use_container_width=True):
            buf = io.BytesIO()
            pdf = canvas.Canvas(buf, pagesize=A4)
            pdf.setFont("Helvetica-Bold", 25); pdf.drawString(50, 800, "INVOICE")
            pdf.setFont("Helvetica", 12); pdf.drawString(50, 770, f"Kepada: {client_name}")
            pdf.drawString(50, 750, f"Total Bayar: Rp {total_final:,.0f}")
            pdf.save(); buf.seek(0)
            st.download_button("⬇️ Simpan File", data=buf, file_name=f"Invoice_{client_name}.pdf", use_container_width=True)
