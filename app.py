import streamlit as st
import io
import textwrap
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle

st.set_page_config(page_title="Invoice Global Pro v9.5", layout="wide", page_icon="🌐")

if 'invoice_items_v6' not in st.session_state:
    st.session_state['invoice_items_v6'] = [{"desc": "", "qty": 1, "price": 0.0}]

# --- KAMUS BAHASA ---
LANG_DATA = {
    "ID": {
        "title": "Faktur Resmi", "sender": "Data Pengirim", "client": "Data Penerima", 
        "items": "Daftar Barang/Jasa", "desc": "Deskripsi", "price": "Harga", 
        "total": "Total", "tax": "Pajak", "grand": "GRAND TOTAL",
        "date": "Tanggal", "due": "Jatuh Tempo", "sign": "Tanda Tangan Resmi", 
        "bill_to": "DITAGIHKAN KEPADA", "inv_no": "Nomor Invoice"
    },
    "EN": {
        "title": "Official Invoice", "sender": "Sender Details", "client": "Recipient Details", 
        "items": "Itemized List", "desc": "Description", "price": "Price", 
        "total": "Total", "tax": "Tax", "grand": "GRAND TOTAL",
        "date": "Date", "due": "Due Date", "sign": "Authorized Signature", 
        "bill_to": "BILL TO", "inv_no": "Invoice Number"
    }
}

with st.sidebar:
    st.title("⚙️ Global Settings (v9.5)")
    lang_choice = st.radio("Language / Bahasa", ["ID", "EN"], horizontal=True)
    L = LANG_DATA[lang_choice]
    
    curr_opt = {"USD ($)": "$", "EUR (€)": "€", "GBP (£)": "£", "IDR (Rp)": "Rp"}
    selected_curr = st.selectbox("Currency / Mata Uang", list(curr_opt.keys()))
    sym = curr_opt[selected_curr]
    
    st.divider()
    # FITUR NOMOR INVOICE OTOMATIS
    default_no = datetime.now().strftime("INV-%Y%m%d-01")
    invoice_no = st.text_input(L["inv_no"], value=default_no)
    
    main_color = st.color_picker("Color / Warna Tema", "#0D47A1")
    inv_date = st.date_input(L["date"], datetime.now())
    due_date = st.date_input(L["due"], datetime.now() + timedelta(days=7))
    
    st.divider()
    biz_name = st.text_input("Sender Name", value="Global Tech Solutions")
    biz_addr = st.text_area("Sender Address", value="Jl. Sudirman, Jakarta")
    biz_sign = st.text_input("Signer Name", value="John Doe")

st.title(f"🌐 {L['title']} ({lang_choice})")
col_in, col_pre = st.columns([1.5, 1])

with col_in:
    st.subheader(f"📩 {L['client']}")
    c_name = st.text_input("Client Name / Nama Klien")
    c_addr = st.text_area("Client Address / Alamat Klien")
    
    st.subheader(f"💰 {L['items']}")
    subtotal = 0.0
    for i in range(len(st.session_state['invoice_items_v6'])):
        with st.container(border=True):
            r1, r2, r3, r4 = st.columns([3, 1, 2, 0.5])
            d = r1.text_input(f"{L['desc']} {i+1}", value=st.session_state['invoice_items_v6'][i]['desc'], key=f"d_v95_f_{i}")
            q = r2.number_input("Qty", min_value=1, value=st.session_state['invoice_items_v6'][i]['qty'], key=f"q_v95_f_{i}")
            p = r3.number_input(f"{L['price']} ({sym})", min_value=0.0, format="%.2f", key=f"p_v95_f_{i}")
            st.session_state['invoice_items_v6'][i] = {"desc": d, "qty": q, "price": p}
            subtotal += (q * p)
            if r4.button("🗑️", key=f"del_v95_f_{i}"):
                st.session_state['invoice_items_v6'].pop(i); st.rerun()

    if st.button("➕ Add Item"):
        st.session_state['invoice_items_v6'].append({"desc": "", "qty": 1, "price": 0.0}); st.rerun()

with col_pre:
    st.subheader("📊 Summary")
    tax_pct = st.number_input(f"{L['tax']} (%)", value=0)
    tax_val = (tax_pct / 100) * subtotal
    grand_total = subtotal + tax_val
    st.metric(L["grand"], f"{sym} {grand_total:,.2f}")

    if st.button(f"🚀 GENERATE PDF", type="primary", use_container_width=True):
        buf = io.BytesIO()
        can = canvas.Canvas(buf, pagesize=A4)
        w, h = A4
        can.setFillColor(colors.HexColor(main_color)); can.rect(0, h-100, w, 100, fill=1, stroke=0)
        can.setFillColor(colors.white); can.setFont("Helvetica-Bold", 24); can.drawString(1*cm, h-60, L["title"].upper())
        
        # Info Invoice (Kanan Atas)
        can.setFont("Helvetica-Bold", 10); can.drawRightString(w-1*cm, h-35, f"{invoice_no}")
        can.setFont("Helvetica", 10); can.drawRightString(w-1*cm, h-50, biz_name)
        can.drawRightString(w-1*cm, h-65, f"{L['date']}: {inv_date.strftime('%d/%m/%Y')}")
        can.drawRightString(w-1*cm, h-80, f"{L['due']}: {due_date.strftime('%d/%m/%Y')}")
        
        can.setFillColor(colors.black); can.setFont("Helvetica-Bold", 11); can.drawString(1*cm, h-130, L["bill_to"] + ":")
        can.setFont("Helvetica", 11); can.drawString(1*cm, h-145, c_name)
        
        data = [[L["desc"], "Qty", L["price"], L["total"]]]
        for it in st.session_state['invoice_items_v6']:
            data.append([it['desc'], it['qty'], f"{it['price']:,.2f}", f"{it['qty']*it['price']:,.2f}"])
        
        t = Table(data, colWidths=[9*cm, 2*cm, 4*cm, 4*cm])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(main_color)),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.5,colors.grey)]))
        t.wrapOn(can, w, h); y_p = h-280 - (len(data)*0.8*cm); t.drawOn(can, 1*cm, y_p)
        
        y_p -= 40; can.setFont("Helvetica-Bold", 14); can.drawRightString(w-1*cm, y_p, f"{L['grand']}: {sym} {grand_total:,.2f}")
        y_si = y_p - 80; can.setFont("Helvetica", 10); can.drawString(w-7*cm, y_si, f"{L['sign']}:")
        can.setFont("Helvetica-Bold", 11); can.drawString(w-7*cm, y_si-50, biz_sign)
        can.save()
        st.download_button(f"⬇️ Download PDF", data=buf.getvalue(), file_name=f"{invoice_no}.pdf", use_container_width=True)
