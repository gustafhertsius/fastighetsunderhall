import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os
import shutil

# --- RENSNING AV EXPORTFILER ÄLDRE ÄN 30 DAGAR ---
EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)
today = date.today()
for filename in os.listdir(EXPORT_DIR):
    filepath = os.path.join(EXPORT_DIR, filename)
    if os.path.isfile(filepath):
        file_date_str = filename.split("_")[-1].replace(".xlsx", "")
        try:
            file_date = date.fromisoformat(file_date_str)
            if (today - file_date).days > 30:
                os.remove(filepath)
        except ValueError:
            continue  # Ignorera filer utan datum i namnet

# Resten av din befintliga kod nedan (oförändrad)

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os

# --- LADDA IN OBJEKTFÖRTECKNING TIDIGT ---
objektfil_path = "./Objektförteckning - Enterprise.xlsx"
fastigheter = []
if os.path.exists(objektfil_path):
    objekt_df = pd.read_excel(objektfil_path)
    st.session_state["objektdata"] = objekt_df
    fastigheter = sorted(objekt_df["Fastighet"].dropna().unique())

# --- SIDHUVD ---
st.set_page_config(page_title="Fastighetsunderhåll", layout="wide")
st.title("🏠 Fastighetsunderhåll – Översikt")

# --- LÄGG TILL INSTALLATION ---
st.subheader("➕ Lägg till installation")
with st.form("install_form"):
    if "objektdata" in st.session_state:
        fastigheter = sorted(st.session_state["objektdata"]["Fastighet"].dropna().unique())
    else:
        fastigheter = []  # ersatt med riktig lista om Exceldata finns
    prop = st.selectbox("Fastighet", fastigheter, key="prop")
    install_type = st.selectbox("Typ av installation", ["Kylskåp", "Frys", "Spis", "Diskmaskin", "Tvättmaskin", "Torktumlare"], key="install_type")
    install_date = st.date_input("Installationsdatum", value=date.today(), key="install_date")
    if "objektdata" in st.session_state and prop:
        objekt_df = st.session_state["objektdata"]
        objekt_df = objekt_df[objekt_df["Fastighet"] == prop]
        anv_val = st.selectbox("Filtrera på användning", ["Alla"] + sorted(objekt_df["Användning"].dropna().unique()), key="usefilter")
        if anv_val != "Alla":
            objekt_df = objekt_df[objekt_df["Användning"] == anv_val]
        valbara_objekt = objekt_df["Objekt"].dropna().unique()
        apt_number = st.selectbox("Välj objekt (lägenhet eller lokal)", sorted(valbara_objekt), key="apt")
    else:
        apt_number = st.text_input("Lägenhetsnummer", key="apt")
    model = st.text_input("Märke/modell", key="model")
    comment = st.text_input("Kommentar", key="comment")
    submitted = st.form_submit_button("Spara installation")
    if submitted:
        st.success(f"Installation sparad: {install_type} i {apt_number}, {prop}")

# --- LADDA UPP DOKUMENT ELLER BILDER ---
st.subheader("📎 Ladda upp dokument eller bilder")
uploaded_files = st.file_uploader("Ladda upp filer", type=["jpg", "png", "pdf", "xlsx"], accept_multiple_files=True)
if uploaded_files:
    for f in uploaded_files:
        st.success(f"Fil mottagen: {f.name}")

# --- GEMENSAMMA UTRYMMEN ---
st.subheader("🏢 Underhåll i gemensamma utrymmen")
with st.form("common_area_form"):
    ca_property = st.selectbox("Fastighet", fastigheter, key="ca_property")
    if "objektdata" in st.session_state:
        gemensamma = st.session_state["objektdata"]
        utrymmen = sorted(gemensamma["Objekttyp"].dropna().unique())
        ca_area_val = st.selectbox("Välj utrymme", utrymmen + ["Eget val"], key="ca_area")
        ca_area = st.text_input("Eget utrymme (om du valde 'Eget val')", key="ca_area_custom") if ca_area_val == "Eget val" else ca_area_val
    else:
        ca_area = st.selectbox("Utrymme", ["Tvättstuga", "Källarförråd", "Vindsförråd", "Pannrum", "Garage", "Trapphus", "Cykelrum", "Fasader", "Fönster", "Balkonger", "Tak", "Övrigt"], key="ca_area")
    ca_part = st.selectbox("Del i utrymmet", ["Golv", "Väggar", "Tak", "Belysning", "Ventilation", "Inredning", "Eget val"], key="ca_part")
    ca_custom = st.text_input("Egen punkt (om du valde 'Eget val')", key="ca_custom")
    ca_status = st.selectbox("Status", ["OK", "Behöver åtgärdas", "Under bevakning"], key="ca_status")
    ca_comment = st.text_input("Kommentar", key="ca_comment")
    ca_date = st.date_input("Datum", value=date.today(), key="ca_date")
    ca_freq = st.number_input("Frekvens (år, valfritt)", min_value=0, max_value=50, value=0, step=1, key="ca_freq")
    ca_priority = st.selectbox("Prioritet", ["Hög", "Mellan", "Låg"], key="ca_priority")
    ca_responsible = st.text_input("Ansvarig (valfritt)", key="ca_responsible")
    ca_image = st.file_uploader("Ladda upp bild (valfritt)", type=["jpg", "png"], key="ca_image")
    ca_submit = st.form_submit_button("Spara underhållspunkt")
    if ca_submit:
        st.success(f"Underhållspunkt sparad för {ca_area} ({ca_custom or ca_part}) i {ca_property}.")

# --- ÅTERKOMMANDE UNDERHÅLL (MED REDIGERING) ---
st.subheader("🔁 Återkommande underhåll")
if "recurring_tasks" not in st.session_state:
    st.session_state["recurring_tasks"] = pd.DataFrame([
        {"Fastighet": "Essingeslätten 5", "Beskrivning": "OVK", "Senast utfört": "2022-05-10", "Frekvens": 3, "Prioritet": "Hög", "Ansvarig": "Förvaltare"},
        {"Fastighet": "Estland – Vandrarhem", "Beskrivning": "Rensning av ventilationskanaler", "Senast utfört": "2024-01-01", "Frekvens": 2, "Prioritet": "Mellan", "Ansvarig": "Driftchef"},
    ])

with st.form("add_recurring"):
    col1, col2 = st.columns(2)
    with col1:
        r_prop = st.selectbox("Fastighet", fastigheter, key="r_prop")
        r_task = st.text_input("Beskrivning", key="r_task")
    with col2:
        r_date = st.date_input("Senast utfört", key="r_date")
        r_freq = st.number_input("Frekvens (år)", min_value=1, max_value=20, value=1, step=1, key="r_freq")
    r_priority = st.selectbox("Prioritet", ["Hög", "Mellan", "Låg"], key="r_priority")
    r_responsible = st.text_input("Ansvarig", key="r_responsible")
    r_submit = st.form_submit_button("➕ Lägg till uppgift")
    if r_submit:
        new_row = pd.DataFrame.from_records([{"Fastighet": r_prop, "Beskrivning": r_task, "Senast utfört": r_date, "Frekvens": r_freq, "Prioritet": r_priority, "Ansvarig": r_responsible}])
        st.session_state["recurring_tasks"] = pd.concat([st.session_state["recurring_tasks"], new_row], ignore_index=True)
        st.success("Uppgiften har lagts till.")

rec_tasks = st.session_state["recurring_tasks"].copy()
rec_tasks["Senast utfört"] = pd.to_datetime(rec_tasks["Senast utfört"])
rec_tasks["Nästa planerade"] = rec_tasks["Senast utfört"] + pd.to_timedelta(rec_tasks["Frekvens"] * 365, unit="D")
upcoming = rec_tasks[rec_tasks["Nästa planerade"] <= pd.Timestamp.today() + pd.to_timedelta(180, unit="D")]
if not upcoming.empty:
    st.warning("⚠️ Kommande underhåll inom 6 månader:")
    st.dataframe(upcoming)
st.markdown("---")

# --- EXPORTKNAPP ---
if st.button("⬇️ Exportera återkommande underhåll"):
    file_path = os.path.join("exports", f"aterkommande_underhall_{date.today()}.xlsx")
    rec_tasks.to_excel(file_path, index=False)
    with open(file_path, "rb") as f:
        st.download_button("Ladda ner Excel", f, file_name=os.path.basename(file_path))

# --- VISNING AV INSTALLATIONER ---
st.subheader("📋 Installerade enheter")
if submitted:
    df_install = pd.DataFrame([{
        "Fastighet": prop,
        "Lägenhet": apt_number,
        "Installation": install_type,
        "Datum": install_date,
        "Modell": model,
        "Kommentar": comment
    }])
    st.dataframe(df_install)
    if st.button("⬇️ Exportera installationer"):
        path = os.path.join("exports", f"installationer_{prop.replace(' ', '_')}_{date.today()}.xlsx")
        df_install.to_excel(path, index=False)
        with open(path, "rb") as f:
            st.download_button("Ladda ner Excel", f, file_name=os.path.basename(path))

# --- VISNING AV GEMENSAMMA UNDERHÅLLSPUNKTER ---
st.subheader("📋 Gemensamma utrymmen – alla punkter")
if ca_submit:
    df_ca = pd.DataFrame([{
        "Fastighet": ca_property,
        "Utrymme": ca_area,
        "Del": ca_custom or ca_part,
        "Datum": ca_date,
        "Status": ca_status,
        "Kommentar": ca_comment,
        "Frekvens": ca_freq,
        "Prioritet": ca_priority,
        "Ansvarig": ca_responsible
    }])
    st.dataframe(df_ca)
    if st.button("⬇️ Exportera gemensamma punkter"):
        ca_path = os.path.join("exports", f"gemensamma_underhall_{ca_property.replace(' ', '_')}_{date.today()}.xlsx")
        df_ca.to_excel(ca_path, index=False)
        with open(ca_path, "rb") as f:
            st.download_button("Ladda ner Excel", f, file_name=os.path.basename(ca_path))


st.markdown("- Visning av installationer")
st.markdown("- Påminnelser om kommande underhåll")
st.markdown("- Export av underhållsdata")
