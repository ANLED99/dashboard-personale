from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Finanze & PAC", page_icon="💰", layout="wide")

st.title("💰 Gestione Finanziaria e Spese")
st.markdown(
    "Qui trovi l'elenco dei movimenti sincronizzati dai tuoi file o inseriti"
    " manualmente."
)

if "dati_finanziari" not in st.session_state:
  st.session_state.dati_finanziari = pd.DataFrame(
      columns=["Data", "Descrizione", "Importo (€)", "Categoria"]
  )

st.subheader("Registro Movimenti")
st.session_state.dati_finanziari = st.data_editor(
    st.session_state.dati_finanziari,
    num_rows="dynamic",
    use_container_width=True,
)

with st.expander("➕ Aggiungi Nuova Transazione Manuale"):
  with st.form("form_spesa"):
    d_data = st.date_input("Data", datetime.today())
    d_desc = st.text_input("Descrizione / Causale")
    d_imp = st.number_input("Importo (€) (usa il segno meno per le spese)", value=0.00)
    d_cat = st.selectbox(
        "Categoria",
        [
            "Finanza & Lavoro",
            "Vita Quotidiana & Famiglia",
            "Casa & Utenze",
            "Svago",
        ],
    )
    submit = st.form_submit_button("Aggiungi Transazione")
    if submit:
      nuova_riga = pd.DataFrame([{
          "Data": str(d_data),
          "Descrizione": d_desc,
          "Importo (€)": d_imp,
          "Categoria": d_cat,
      }])
      st.session_state.dati_finanziari = pd.concat(
          [st.session_state.dati_finanziari, nuova_riga], ignore_index=True
      )
      st.success("Transazione aggiunta correttamente!")
      st.rerun()
