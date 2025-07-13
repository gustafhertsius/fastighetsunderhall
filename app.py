import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os

# --- SIDHUVD ---
st.set_page_config(page_title="Fastighetsunderhåll", layout="wide")
st.title("🏠 Fastighetsunderhåll – Översikt")

# --- INITIERA DATA ---
if "installations" not in st.session_state:
    st.session_state.installations = pd.DataFrame(columns=[
        "Fastighet", "Lägenhet", "Typ", "Märke", "Installationsdatum", "Kommentar"
    ])
if "maintenance" not in st.session_state:
    st.session_state.maintenance = pd.DataFrame(columns=[
        "Fastighet", "Beskrivning", "Frekvens (år)", "Senast utfört", "Kommentar"
    ])
if "tenants" not in st.session_state:
    st.session_state.tenants = pd.DataFrame(columns=[
        "Fastighet", "Lägenhet/Lokal", "Namn", "Typ", "Kontakt"
    ])
if "pdf_reports" not in st.session_state:
    st.session_state.pdf_reports = pd.DataFrame(columns=[
        "Fastighet", "Filnamn", "Kommentar"
    ])

# --- LÄGG TILL INSTALLATION ---
st.subheader("➕ Lägg till installation")
with st.form("add_installation"):
    col1, col2, col3 = st.columns(3)
    with col1:
        property = st.selectbox("Fastighet", ["Essingeslätten 5", "Fastighet 2", "Fastighet 3", "Fastighet 4", "Estland – Vandrarhem"])
        apartment = st.text_input("Lägenhetsnummer")
    with col2:
        item_type = st.selectbox("Typ av installation", ["Kylskåp", "Frys", "Spis", "Diskmaskin", "Tvättmaskin", "Torktumlare", "Fläkt", "Övrigt"])
        brand = st.text_input("Märke/modell")
    with col3:
        install_date = st.date_input("Installationsdatum", value=date.today())
        comment = st.text_input("Kommentar")

    submitted = st.form_submit_button("Spara installation")
    if submitted:
        new_row = {
            "Fastighet": property,
            "Lägenhet": apartment,
            "Typ": item_type,
            "Märke": brand,
            "Installationsdatum": install_date,
            "Kommentar": comment
        }
        st.session_state.installations = pd.concat(
            [st.session_state.installations, pd.DataFrame([new_row])], ignore_index=True
        )
        st.success(f"Installation tillagd för lägenhet {apartment} i {property}.")

# --- LADDA UPP OBJEKTRAPPORT (PDF) ---
st.subheader("📄 Ladda upp objektrapport (PDF)")
with st.form("upload_pdf"):
    col1, col2 = st.columns(2)
    with col1:
        pdf_property = st.selectbox("Fastighet", ["Essingeslätten 5", "Fastighet 2", "Fastighet 3", "Fastighet 4", "Estland – Vandrarhem"], key="pdf_prop")
        pdf_file = st.file_uploader("Välj PDF", type="pdf", key="pdf_upload")
    with col2:
        pdf_comment = st.text_input("Kommentar")

    pdf_submit = st.form_submit_button("Ladda upp")
    if pdf_submit and pdf_file:
        save_path = os.path.join("pdf_uploads", pdf_file.name)
        os.makedirs("pdf_uploads", exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(pdf_file.getbuffer())
        st.session_state.pdf_reports = pd.concat([
            st.session_state.pdf_reports,
            pd.DataFrame([{ "Fastighet": pdf_property, "Filnamn": pdf_file.name, "Kommentar": pdf_comment }])
        ], ignore_index=True)
        st.success(f"PDF uppladdad: {pdf_file.name}")

# --- EXTRAHERA OCH VISA TABELL UR OBJEKTRAPPORT (PDF) ---
import pdfplumber

st.subheader("📊 Extrahera data från objektrapport (PDF-tabell)")
with st.form("extract_pdf_table"):
    col1, col2 = st.columns(2)
    with col1:
        extract_file = st.file_uploader("Välj PDF med tabell", type="pdf", key="pdf_extract")
    with col2:
        extract_property = st.selectbox("Fastighet (kopplas till tabellen)", ["Essingeslätten 5", "Fastighet 2", "Fastighet 3", "Fastighet 4", "Estland – Vandrarhem"], key="extract_prop")

    extract_submit = st.form_submit_button("Extrahera tabell")

if extract_submit and extract_file is not None:
    with pdfplumber.open(extract_file) as pdf:
        tables = []
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                tables.extend(table[1:])  # hoppa över rubrikraden om den kommer flera gånger

    if tables:
        df_pdf = pd.DataFrame(tables, columns=[
            "Fastighet", "Objekt", "Objektadress", "Användning", "Standard",
            "Yta kvm", "Våning", "Kontraktinnehavare", "Kontrakttyp"
        ])
        df_pdf["Fastighet"] = extract_property
        st.success("Tabell extraherad!")
        st.dataframe(df_pdf)

        if st.button("💾 Spara tabell som data"):
            if "extracted_tables" not in st.session_state:
                st.session_state.extracted_tables = pd.DataFrame()
            st.session_state.extracted_tables = pd.concat([
                st.session_state.extracted_tables,
                df_pdf
            ], ignore_index=True)
            st.success("Tabellen är sparad i minnet.")
    else:
        st.warning("Ingen tabell hittades i PDF:en.")

# --- VISA UPPLADDADE PDF:ER ---
if not st.session_state.pdf_reports.empty:
    st.subheader("📁 Uppladdade PDF-rapporter")
    for i, row in st.session_state.pdf_reports.iterrows():
        with st.expander(f"{row['Fastighet']} – {row['Filnamn']}"):
            st.write(f"Kommentar: {row['Kommentar']}")
            file_path = os.path.join("pdf_uploads", row['Filnamn'])
            with open(file_path, "rb") as f:
                st.download_button("⬇️ Ladda ner PDF", f, file_name=row['Filnamn'])

# --- VISA SPARADE EXTRAHERADE TABELLER ---
if "extracted_tables" in st.session_state and not st.session_state.extracted_tables.empty:
    st.subheader("📋 Sparade tabeller från objektrapporter")

    selected_property = st.selectbox("Filtrera på fastighet", ["Alla"] + sorted(st.session_state.extracted_tables["Fastighet"].unique()))
    filtered_df = st.session_state.extracted_tables.copy()
    if selected_property != "Alla":
        filtered_df = filtered_df[filtered_df["Fastighet"] == selected_property]

    st.dataframe(filtered_df)

    if st.button("⬇️ Exportera tabeller till Excel"):
        export_path = "extraherade_tabeller.xlsx"
        filtered_df.to_excel(export_path, index=False)
        with open(export_path, "rb") as f:
            st.download_button("Ladda ner Excel-fil", f, file_name=export_path)

# --- PÅMINNELSER OM ÄLDRE INSTALLATIONER ---
st.subheader("🔔 Installationer äldre än 10 år")
ten_years_ago = date.today() - timedelta(days=365 * 10)
install_dates = pd.to_datetime(st.session_state.installations["Installationsdatum"], errors="coerce")
df_with_dates = st.session_state.installations.copy()
df_with_dates["Installationsdatum"] = install_dates
old_items = df_with_dates[df_with_dates["Installationsdatum"] < pd.to_datetime(ten_years_ago)]
if not old_items.empty:
    st.warning("Följande installationer är äldre än 10 år:")
    st.dataframe(old_items)
else:
    st.info("Inga installationer är äldre än 10 år.")
