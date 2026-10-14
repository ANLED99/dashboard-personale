# --- BARRA LATERALE COMUNE ---
st.sidebar.title("⚡ Centro di Controllo")
st.sidebar.markdown("---")
st.sidebar.success("🟢 **Stato Sistema**: Online & Sincronizzato")import streamlit as st

st.set_page_config(
    page_title="Guide Lavoro", page_icon="📚", layout="wide"
)

st.title("📚 Cheat Sheet & Guide Operative")
st.markdown("Consulenza rapida per i software di lavoro.")

software_scelto = st.selectbox(
    "Seleziona Software",
    ["Bpoint", "Zucchetti Paghe", "Agenzia delle Entrate", "Altro"],
)

st.text_area(
    f"Note e procedure per {software_scelto}:",
    placeholder="Scrivi o incolla qui i tuoi appunti...",
    height=350,
)
