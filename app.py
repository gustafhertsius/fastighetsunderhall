import streamlit as st
import pandas as pd
from datetime import date, timedelta

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

# --- LADDA UPP DOKUMENT ELLER BILDER ---
st.subheader("📎 Ladda upp dokument eller bilder")
uploaded_files = st.file_uploader("Ladda upp filer", accept_multiple_files=True)
if uploaded_files:
    st.success(f"{len(uploaded_files)} fil(er) uppladdade.")

# --- PÅMINNELSER OM ÄLDRE INSTALLATIONER ---
st.subheader("🔔 Installationer äldre än 10 år")
ten_years_ago = date.today() - timedelta(days=365 * 10)
