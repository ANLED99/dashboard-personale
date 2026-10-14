
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Personale", page_icon="⚡", layout="wide"
)

# Inizializzazione globale della memoria condivisa
if "dati_finanziari" not in st.session_state:
  st.session_state.dati_finanziari = pd.DataFrame(
      columns=["Data", "Descrizione", "Importo (€)", "Categoria"]
  )

if "archivio_file" not in st.session_state:
  st.session_state.archivio_file = []

# --- MENU LATERALE AGGIUNTIVO ---
st.sidebar.title("⚡ Centro di Controllo")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "📌 **Navigazione Pagine**\nUsa il menu nativo di Streamlit sopra o i"
    " pulsanti di scelta rapida sottostanti per spostarti."
)

st.sidebar.markdown("---")
st.sidebar.success("🟢 **Stato Sistema**: Online & Sincronizzato")

# --- HOME CONTENT ---
st.title("⚡ Centro di Controllo Personale")
st.markdown(
    "Benvenuto nella tua dashboard modulare. Da qui puoi monitorare i tuoi"
    " dati finanziari e la documentazione archiviata."
)
st.markdown("---")

df_globale = st.session_state.dati_finanziari
totale_spese = (
    df_globale["Importo (€)"].sum() if not df_globale.empty else 0.0
)

col1, col2, col3 = st.columns(3)
with col1:
  st.metric(
      label="💳 Bilancio Totale Registrato", value=f"€ {totale_spese:,.2f}"
  )
with col2:
  st.metric(label="📌 Transazioni Attive", value=f"{len(df_globale)}")
with col3:
  st.metric(
      label="📚 File Storicizzati", value=f"{len(st.session_state.archivio_file)}"
  )

st.info(
    "💡 **Suggerimento:** Seleziona la sezione desiderata dal menu laterale"
    " delle pagine per iniziare a lavorare."
)
