import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Personale", page_icon="📊", layout="wide"
)

st.title("📊 La Mia Dashboard Personale")
st.write("Pannello di controllo per la gestione dati, finanze e note.")

# Sidebar per la navigazione
st.sidebar.header("⚙️ Menu & Opzioni")
sezione = st.sidebar.radio(
    "Seleziona Sezione:", ["📁 Gestione File & Dati", "📝 Note & Cheat Sheet"]
)

if sezione == "📁 Gestione File & Dati":
  st.subheader("📁 Carica e Modifica i tuoi Dati")

  # Componente per caricare i file dal sito
  uploaded_file = st.file_uploader(
      "Trascina qui il tuo file Excel o CSV:", type=["xlsx", "xls", "csv"]
  )

  if uploaded_file is not None:
    try:
      if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
      else:
        df = pd.read_excel(uploaded_file)

      st.success(f"File '{uploaded_file.name}' caricato con successo!")

      # Tabella interattiva e modificabile direttamente sulla pagina web
      st.markdown("### ✏️ Tabella Modificabile")
      st.info(
          "Puoi fare doppio clic sulle celle per modificare i valori"
          " direttamente da qui."
      )

      edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

      # Possibilità di riscaricare il file aggiornato
      st.markdown("### 💾 Scarica Dati Aggiornati")
      csv_data = edited_df.to_csv(index=False).encode("utf-8")
      st.download_button(
          label="Scarica File Aggiornato (CSV)",
          data=csv_data,
          file_name="dati_aggiornati.csv",
          mime="text/csv",
      )

    except Exception as e:
      st.error(f"Errore nella lettura del file: {e}")
  else:
    st.info(
        "Nessun file caricato al momento. Usa il riquadro sopra per iniziare."
    )

elif sezione == "📝 Note & Cheat Sheet":
  st.subheader("📝 Note e Promemoria Operativi")

  nota = st.text_area(
      "Inserisci note, guide o cheat sheet operativi:", height=200
  )
  if st.button("Salva Nota"):
    st.success("Nota salvata per questa sessione!")
    st.write("---")
    st.markdown("**Nota inserita:**")
    st.write(nota)
