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

# --- SIDHUVD ---
st.set_page_config(page_title="Fastighetsunderhåll", layout="wide")
st.title("🏠 Fastighetsunderhåll – Översikt")

# ... (resten av befintlig kod fortsätter som tidigare)
