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
old_items = st.session_state.installations[
    pd.to_datetime(st.session_state.installations["Installationsdatum"]) < ten_years_ago
]
if not old_items.empty:
    st.warning("Följande installationer är äldre än 10 år:")
    st.dataframe(old_items)
else:
    st.info("Inga installationer är äldre än 10 år.")

# --- UNDERHÅLLSPLAN ---
st.subheader("🛠 Underhållsplan")
with st.form("add_maintenance"):
    col1, col2, col3 = st.columns(3)
    with col1:
        m_prop = st.selectbox("Fastighet", ["Essingeslätten 5", "Fastighet 2", "Fastighet 3", "Fastighet 4", "Estland – Vandrarhem"], key="m_prop")
        desc = st.text_input("Beskrivning av åtgärd")
    with col2:
        freq = st.number_input("Frekvens (år)", min_value=1, max_value=50, step=1)
        last_done = st.date_input("Senast utfört")
    with col3:
        m_comment = st.text_input("Kommentar")

    m_submit = st.form_submit_button("Spara underhållspunkt")
    if m_submit:
        new_maint = {
            "Fastighet": m_prop,
            "Beskrivning": desc,
            "Frekvens (år)": freq,
            "Senast utfört": last_done,
            "Kommentar": m_comment
        }
        st.session_state.maintenance = pd.concat(
            [st.session_state.maintenance, pd.DataFrame([new_maint])], ignore_index=True
        )
        st.success("Underhållspunkt tillagd.")

st.dataframe(st.session_state.maintenance)

# --- HYRESGÄSTREGISTER ---
st.subheader("🧑‍💼 Hyresgästregister")
with st.form("add_tenant"):
    col1, col2, col3 = st.columns(3)
    with col1:
        t_prop = st.selectbox("Fastighet", ["Essingeslätten 5", "Fastighet 2", "Fastighet 3", "Fastighet 4", "Estland – Vandrarhem"], key="t_prop")
        unit = st.text_input("Lägenhet/Lokal")
    with col2:
        name = st.text_input("Namn")
        typ = st.selectbox("Typ", ["Lägenhet", "Lokal"])
    with col3:
        contact = st.text_input("Kontaktinfo")

    t_submit = st.form_submit_button("Spara hyresgäst")
    if t_submit:
        new_tenant = {
            "Fastighet": t_prop,
            "Lägenhet/Lokal": unit,
            "Namn": name,
            "Typ": typ,
            "Kontakt": contact
        }
        st.session_state.tenants = pd.concat(
            [st.session_state.tenants, pd.DataFrame([new_tenant])], ignore_index=True
        )
        st.success("Hyresgäst tillagd.")

st.dataframe(st.session_state.tenants)

# --- EXPORTERA DATA ---
st.subheader("⬇️ Exportera till Excel")
export_btn = st.button("Ladda ner alla data som Excel-fil")
if export_btn:
    with pd.ExcelWriter("underhall_data.xlsx") as writer:
        st.session_state.installations.to_excel(writer, sheet_name="Installationer", index=False)
        st.session_state.maintenance.to_excel(writer, sheet_name="Underhållsplan", index=False)
        st.session_state.tenants.to_excel(writer, sheet_name="Hyresgäster", index=False)
    with open("underhall_data.xlsx", "rb") as f:
        st.download_button("Klicka här för att ladda ner", f, file_name="underhall_data.xlsx")

# --- VISA INSTALLATIONER ---
st.subheader("📋 Installationer per lägenhet")
with st.expander("Filtrera listan"):
    col1, col2 = st.columns(2)
    with col1:
        filter_property = st.selectbox("Filtrera på fastighet", ["Alla"] + list(st.session_state.installations["Fastighet"].unique()))
    with col2:
        filter_type = st.selectbox("Filtrera på typ", ["Alla"] + list(st.session_state.installations["Typ"].unique()))

df_filtered = st.session_state.installations.copy()
if filter_property != "Alla":
    df_filtered = df_filtered[df_filtered["Fastighet"] == filter_property]
if filter_type != "Alla":
    df_filtered = df_filtered[df_filtered["Typ"] == filter_type]

st.dataframe(df_filtered.sort_values(by=["Fastighet", "Lägenhet", "Typ"]))
