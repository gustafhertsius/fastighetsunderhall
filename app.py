import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os

# --- SIDHUVD ---
st.set_page_config(page_title="Fastighetsunderhåll", layout="wide")
st.title("🏠 Fastighetsunderhåll – Översikt")

# --- INITIERA DATA ---
if "common_areas" not in st.session_state:
    st.session_state.common_areas = pd.DataFrame(columns=[
        "Fastighet", "Utrymme", "Del", "Status", "Kommentar", "Datum", "Frekvens (år)", "Prioritet", "Ansvarig", "Bildfil"
    ])
if "room_maintenance" not in st.session_state:
    st.session_state.room_maintenance = pd.DataFrame(columns=[
        "Fastighet", "Lägenhet", "Rum", "Del", "Status", "Kommentar", "Datum", "Bildfil"
    ])
if "installations" not in st.session_state:
    st.session_state.installations = pd.DataFrame(columns=[
        "Fastighet", "Lägenhet", "Typ", "Märke", "Installationsdatum", "Kommentar"
    ])
if "maintenance" not in st.session_state:
    st.session_state.maintenance = pd.DataFrame(columns=[
        "Fastighet", "Beskrivning", "Frekvens (år)", "Senast utfört", "Kommentar", "Prioritet", "Ansvarig"
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

# --- LÄS IN DATA FRÅN EXCEL I STÄLLET FÖR PDF ---
st.subheader("📥 Ladda upp objektrapport från Excel (ersätter PDF-tabeller)")
xls_file = st.file_uploader("Välj Excel-fil (XLSX)", type=["xlsx"], key="xls_upload")

if xls_file:
    df_xls = pd.read_excel(xls_file)
    st.write("**Kolumner hittade i filen:**", list(df_xls.columns))

    required_columns = ["Fastighet", "Objekt", "Objektadress", "Användning", "Standard", "Yta kvm", "Våning", "Kontraktinnehavare", "Kontrakttyp"]
    missing_cols = [col for col in required_columns if col not in df_xls.columns]
    if missing_cols:
        st.error(f"Följande obligatoriska kolumner saknas: {', '.join(missing_cols)}")
    st.success("Excel-data inläst!")
    st.dataframe(df_xls)

    if st.button("💾 Spara Excel-tabell som data"):
        st.session_state.extracted_tables = df_xls
        st.success("Excel-tabellen är nu sparad som objektrapport.")

if "extracted_tables" in st.session_state and not st.session_state.extracted_tables.empty:
    st.subheader("📋 Sparade tabeller från objektrapporter")

    if "Fastighet" in st.session_state.extracted_tables.columns:
        selected_property = st.selectbox("Filtrera på fastighet", ["Alla"] + sorted(st.session_state.extracted_tables["Fastighet"].dropna().unique()))
    else:
        st.warning("Kolumnen 'Fastighet' saknas i den uppladdade Excel-tabellen.")
        selected_property = "Alla"
    filtered_df = st.session_state.extracted_tables.copy()
    if selected_property != "Alla":
        filtered_df = filtered_df[filtered_df["Fastighet"] == selected_property]

    st.dataframe(filtered_df)

    if st.button("⬇️ Exportera tabeller till Excel"):
        export_path = "extraherade_tabeller.xlsx"
        filtered_df.to_excel(export_path, index=False)
        with open(export_path, "rb") as f:
            st.download_button("Ladda ner Excel-fil", f, file_name=export_path)

# --- UNDERHÅLL I GEMENSAMMA UTRYMMEN ---

# --- VISNING AV YTTRE UNDERHÅLL PER FASTIGHET ---
if not st.session_state.common_areas.empty:
    st.subheader("🏗️ Yttre underhåll per fastighet")
    outer_areas = ["Fasader", "Fönster", "Balkonger", "Tak"]
    filtered_outer = st.session_state.common_areas[st.session_state.common_areas["Utrymme"].isin(outer_areas)]
    outer_filter_prop = st.selectbox("Filtrera yttre underhåll per fastighet", ["Alla"] + sorted(filtered_outer["Fastighet"].dropna().unique()), key="outer_filter")
    if outer_filter_prop != "Alla":
        filtered_outer = filtered_outer[filtered_outer["Fastighet"] == outer_filter_prop]
    st.dataframe(filtered_outer)

    if st.button("⬇️ Exportera yttre underhåll till Excel"):
        export_outer = "yttre_underhall.xlsx"
        filtered_outer.to_excel(export_outer, index=False)
        with open(export_outer, "rb") as f:
            st.download_button("Ladda ner Excel-fil", f, file_name=export_outer)
st.subheader("🧰 Underhåll i gemensamma utrymmen")
with st.form("add_common_maintenance"):
    col1, col2, col3 = st.columns(3)
    with col1:
        ca_property = st.selectbox("Fastighet", ["Essingeslätten 5", "Fastighet 2", "Fastighet 3", "Fastighet 4", "Estland – Vandrarhem"], key="ca_property")
        ca_area = st.selectbox("Utrymme", ["Tvättstuga", "Källarförråd", "Vindsförråd", "Pannrum", "Garage", "Trapphus", "Cykelrum", "Fasader", "Fönster", "Balkonger", "Tak", "Övrigt"], key="ca_area")
    with col2:
        ca_part = st.text_input("Del (t.ex. Golv, Maskiner, Ventilation)", key="ca_part")
        ca_status = st.selectbox("Status", ["OK", "Behöver åtgärdas", "Planerat underhåll"], key="ca_status")
    with col3:
        ca_comment = st.text_input("Kommentar", key="ca_comment")
        ca_date = st.date_input("Datum", value=date.today(), key="ca_date")
        ca_freq = st.number_input("Frekvens (år, valfritt)", min_value=0, max_value=50, value=0, step=1, key="ca_freq")
        ca_priority = st.selectbox("Prioritet", ["Hög", "Mellan", "Låg"], key="ca_priority")
        ca_responsible = st.text_input("Ansvarig (valfritt)", key="ca_responsible")
        ca_image = st.file_uploader("Bild (valfritt)", type=["jpg", "jpeg", "png"], key="ca_image")

    ca_submit = st.form_submit_button("Spara gemensam punkt")
    if ca_submit:
        image_path = ""
        if ca_image:
            os.makedirs("common_area_images", exist_ok=True)
            image_path = os.path.join("common_area_images", ca_image.name)
            with open(image_path, "wb") as f:
                f.write(ca_image.getbuffer())

        new_ca = {
            "Fastighet": ca_property,
            "Utrymme": ca_area,
            "Del": ca_part,
            "Status": ca_status,
            "Kommentar": ca_comment,
            "Datum": ca_date,
            "Frekvens (år)": ca_freq, "Prioritet": ca_priority, "Ansvarig": ca_responsible, "Bildfil": image_path
        }
        st.session_state.common_areas = pd.concat([
            st.session_state.common_areas,
            pd.DataFrame([new_ca])
        ], ignore_index=True)
        st.success(f"Punkt sparad för {ca_area} ({ca_part}) i {ca_property}.")

if not st.session_state.common_areas.empty:
    st.subheader("📋 Gemensamma utrymmen – underhållspunkter")
    filter_ca_prop = st.selectbox("Filtrera på fastighet (gemensamma utrymmen)", ["Alla"] + sorted(st.session_state.common_areas["Fastighet"].dropna().unique()), key="filter_ca")
    filtered_ca = st.session_state.common_areas.copy()
    if filter_ca_prop != "Alla":
        filtered_ca = filtered_ca[filtered_ca["Fastighet"] == filter_ca_prop]

    for i, row in filtered_ca.iterrows():
        with st.expander(f"{row['Fastighet']} – {row['Utrymme']} – {row['Del']}"):
            st.write(f"📅 Datum: {row['Datum']}")
            st.write(f"📈 Frekvens: {row['Frekvens (år)']} år")
            st.write(f"🏷️ Prioritet: {row['Prioritet']}")
            st.write(f"👷 Ansvarig: {row['Ansvarig']}")
            st.write(f"🔧 Status: {row['Status']}")
            st.write(f"📝 Kommentar: {row['Kommentar']}")
            if row['Bildfil'] and os.path.exists(row['Bildfil']):
                st.image(row['Bildfil'], caption="Bild", use_column_width=True)
            if st.button("✅ Markera som färdig", key=f"ca_done_{i}"):
                st.session_state.common_areas.at[i, "Status"] = "OK"
                st.experimental_rerun()

    if st.button("⬇️ Exportera gemensamma punkter till Excel"):
        export_path_ca = "gemensamma_underhall.xlsx"
        filtered_ca.to_excel(export_path_ca, index=False)
        with open(export_path_ca, "rb") as f:
            st.download_button("Ladda ner Excel-fil", f, file_name=export_path_ca)

# --- LÄGG TILL UNDERHÅLLSPUNKTER I RUM ---
st.subheader("🧱 Lägg till underhållspunkter i rum")
with st.form("add_room_maintenance"):
    col1, col2, col3 = st.columns(3)
    with col1:
        rm_prop = st.selectbox("Fastighet", ["Essingeslätten 5", "Fastighet 2", "Fastighet 3", "Fastighet 4", "Estland – Vandrarhem"], key="rm_prop")
        rm_apt = st.text_input("Lägenhetsnummer", key="rm_apt")
    with col2:
        room = st.text_input("Rum (t.ex. Sovrum, Kök)", key="rm_room")
        predefined_parts = [
    "Golv", "Tak", "Väggar", "Lister", "Fönster", "Dörrar", "El",
    "Värme", "Ventilation", "Rökdetektor", "Brandvarnare", "Armatur",
    "Garderober", "Köksluckor", "Tvättställ", "Blandare", "Golvbrunn",
    "Spisfläkt", "Övrigt"
]
selected_part = st.selectbox("Del i rummet", predefined_parts + ["Annan..."])
if selected_part == "Annan...":
    part = st.text_input("Skriv in annan del", key="rm_part_custom")
else:
    part = selected_part
    with col3:
        status = st.selectbox("Status", ["OK", "Behöver åtgärdas", "Planerat underhåll"], key="rm_status")
        comment = st.text_input("Kommentar", key="rm_comment")

    col4, col5 = st.columns(2)
    with col4:
        rm_date = st.date_input("Datum", value=date.today(), key="rm_date")
    with col5:
        rm_image = st.file_uploader("Ladda upp bild (valfritt)", type=["png", "jpg", "jpeg"], key="rm_image")

    save_room = st.form_submit_button("Spara underhållspunkt")
    if save_room:
        image_filename = ""
        if rm_image:
            image_dir = "room_maintenance_images"
            os.makedirs(image_dir, exist_ok=True)
            image_filename = os.path.join(image_dir, rm_image.name)
            with open(image_filename, "wb") as f:
                f.write(rm_image.getbuffer())

        new_rm = {
            "Fastighet": rm_prop,
            "Lägenhet": rm_apt,
            "Rum": room,
            "Del": part,
            "Status": status,
            "Kommentar": comment,
            "Datum": rm_date,
            "Bildfil": image_filename
        }
        st.session_state.room_maintenance = pd.concat([
            st.session_state.room_maintenance,
            pd.DataFrame([new_rm])
        ], ignore_index=True)
        st.success(f"Underhållspunkt sparad för {room} ({part}) i {rm_apt}, {rm_prop}.") i {rm_apt}, {rm_prop}.")

if not st.session_state.room_maintenance.empty:
    st.subheader("📋 Alla underhållspunkter i rum")
    colf1, colf2 = st.columns(2)
    with colf1:
        filter_property = st.selectbox("Filtrera på fastighet", ["Alla"] + sorted(st.session_state.room_maintenance["Fastighet"].dropna().unique()), key="filt_prop")
    with colf2:
        filter_status = st.selectbox("Filtrera på status", ["Alla"] + sorted(st.session_state.room_maintenance["Status"].dropna().unique()), key="filt_status")

    filtered_rm = st.session_state.room_maintenance.copy()
    if filter_property != "Alla":
        filtered_rm = filtered_rm[filtered_rm["Fastighet"] == filter_property]
    if filter_status != "Alla":
        filtered_rm = filtered_rm[filtered_rm["Status"] == filter_status]

    for i, row in filtered_rm.iterrows():
        with st.expander(f"{row['Fastighet']} – {row['Lägenhet']} – {row['Rum']} – {row['Del']}"):
            st.write(f"📅 Datum: {row['Datum']}")
            st.write(f"🔧 Status: {row['Status']}")
            st.write(f"📝 Kommentar: {row['Kommentar']}")
            if row['Bildfil'] and os.path.exists(row['Bildfil']):
                st.image(row['Bildfil'], caption="Bild på underhållspunkt", use_column_width=True)
            if st.button("✅ Markera som färdig", key=f"done_{i}"):
                st.session_state.room_maintenance.at[i, "Status"] = "OK"
                st.experimental_rerun()

    if st.button("⬇️ Exportera underhållspunkter till Excel"):
        export_file = "underhallspunkter.xlsx"
        filtered_rm.to_excel(export_file, index=False)
        with open(export_file, "rb") as f:
            st.download_button("Ladda ner Excel-fil", f, file_name=export_file)

# --- SUMMERING AV UNDERHÅLLSPUNKTER ---
st.subheader("📊 Summering av underhåll")
if not st.session_state.room_maintenance.empty:
    summary_by_property = st.session_state.room_maintenance.groupby("Fastighet")["Status"].value_counts().unstack().fillna(0)
    st.write("### Per fastighet")
    st.dataframe(summary_by_property)

    summary_total = st.session_state.room_maintenance["Status"].value_counts()
    st.write("### Totalt")
    st.dataframe(summary_total)

# --- ÅTERKOMMANDE UNDERHÅLL \(INTERVALL\) ---

# --- PÅMINNELSE FÖR GEMENSAMMA UTRYMMEN BASERAT PÅ FREKVENS ---
st.subheader("📅 Påminnelser – gemensamma utrymmen")
if not st.session_state.common_areas.empty:
    ca_df = st.session_state.common_areas.copy()
    ca_df["Datum"] = pd.to_datetime(ca_df["Datum"], errors="coerce")
    ca_df["Frekvens (år)"] = pd.to_numeric(ca_df["Frekvens (år)"], errors="coerce")
    ca_df = ca_df.dropna(subset=["Datum", "Frekvens (år)"])
    ca_df = ca_df[ca_df["Frekvens (år)"] > 0]
    ca_df["Nästa planerade"] = ca_df["Datum"] + pd.to_timedelta(ca_df["Frekvens (år)"] * 365, unit="D")
    upcoming_ca = ca_df[ca_df["Nästa planerade"] <= pd.to_datetime(date.today() + timedelta(days=180))]
    if not upcoming_ca.empty:
        st.warning("⚠️ Följande underhåll i gemensamma utrymmen infaller inom 6 månader:")
        st.dataframe(upcoming_ca)
    else:
        st.success("✅ Inga planerade underhåll i gemensamma utrymmen inom 6 månader.")
st.subheader("🔁 Återkommande underhåll")
with st.form("recurring_maintenance"):
    col1, col2, col3 = st.columns(3)
    with col1:
        r_fastighet = st.selectbox("Fastighet", ["Essingeslätten 5", "Fastighet 2", "Fastighet 3", "Fastighet 4", "Estland – Vandrarhem"], key="r_fastighet")
    with col2:
        r_desc = st.text_input("Vad ska göras?", key="r_desc")
        r_freq = st.number_input("Frekvens (år)", min_value=1, max_value=50, step=1, value=5)
        r_priority = st.selectbox("Prioritet", ["Hög", "Mellan", "Låg"], key="r_priority")
    with col3:
        r_last = st.date_input("Senast utfört", value=date.today())
        r_comment = st.text_input("Kommentar", key="r_comment")
        r_responsible = st.text_input("Ansvarig (namn eller firma)", key="r_responsible")

    r_submit = st.form_submit_button("Spara återkommande underhåll")
    if r_submit:
        new_r = {
            "Fastighet": r_fastighet,
            "Beskrivning": r_desc,
            "Frekvens (år)": r_freq,
            "Senast utfört": r_last,
            "Kommentar": r_comment,
            "Prioritet": r_priority,
            "Ansvarig": r_responsible
        }
        st.session_state.maintenance = pd.concat([
            st.session_state.maintenance,
            pd.DataFrame([new_r])
        ], ignore_index=True)
        st.success(f"Underhållspunkt sparad: {r_desc} ({r_fastighet})")

if not st.session_state.maintenance.empty:
    if st.button("⬇️ Exportera återkommande underhåll till Excel"):
        export_path_recur = "aterkommande_underhall.xlsx"
        df_maint.to_excel(export_path_recur, index=False)
        with open(export_path_recur, "rb") as f:
            st.download_button("Ladda ner Excel-fil", f, file_name=export_path_recur)
    colrm1, colrm2 = st.columns(2)
    with colrm1:
        filter_maint_property = st.selectbox("Filtrera återkommande underhåll per fastighet", ["Alla"] + sorted(st.session_state.maintenance["Fastighet"].dropna().unique()), key="filter_rec")

    df_maint = st.session_state.maintenance.copy()
    if filter_maint_property != "Alla":
        df_maint = df_maint[df_maint["Fastighet"] == filter_maint_property]

    df_maint["Nästa planerade"] = df_maint.apply(
        lambda row: row["Senast utfört"] + timedelta(days=365 * row["Frekvens (år)"]), axis=1
    )
    st.dataframe(df_maint)

    upcoming = df_maint[df_maint["Nästa planerade"] <= date.today() + timedelta(days=180)]
    if not upcoming.empty:
        st.warning("⚠️ Följande återkommande underhåll infaller inom 6 månader:")
        st.dataframe(upcoming)
    else:
        st.info("✅ Inga återkommande underhåll förfaller inom 6 månader.")

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
