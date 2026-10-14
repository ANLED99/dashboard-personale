import pandas as pd
import streamlit as st

# Configurazione della pagina principale
st.set_page_config(
    page_title="Dashboard Personale & Lavoro", page_icon="⚡", layout="wide"
)

# --- INIZIALIZZAZIONE DELLA MEMORIA CONDIVISA ---
if "dati_finanziari" not in st.session_state:
  st.session_state.dati_finanziari = pd.DataFrame(
      columns=["Data", "Descrizione", "Importo (€)", "Categoria"]
  )

if "archivio_file" not in st.session_state:
  st.session_state.archivio_file = []


# --- DEFINIZIONE DELLE FUNZIONI DELLE SEZIONI ---
def home_page():
  st.title("⚡ Centro di Controllo Personale")
  st.markdown(
      "Benvenuto nella tua dashboard centralizzata. Usa il menu a tendina o"
      " i link nella barra laterale per accedere alle sezioni."
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
        label="📚 File Storicizzati",
        value=f"{len(st.session_state.archivio_file)}",
    )

  st.info(
      "💡 **Suggerimento:** Seleziona una sezione dal menu laterale per iniziare"
      " a gestire i file o le finanze."
  )


def archivio_file_page():
  from datetime import datetime

  st.title("📁 Archivio e Multi-Upload File")
  st.markdown(
      "Carica i tuoi documenti (Excel, CSV, PDF, Word) e mantieni uno"
      " storico permanente."
  )

  uploaded_files = st.file_uploader(
      "Seleziona i file da caricare:",
      accept_multiple_files=True,
      type=["pdf", "docx", "xlsx", "xls", "csv", "txt"],
  )

  if uploaded_files:
    st.write(f"📁 Hai selezionato {len(uploaded_files)} file.")
    if st.button("🚀 Conferma Upload e Storicizza"):
      for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        file_size = f"{uploaded_file.size / 1024:.1f} KB"
        data_caricamento = datetime.now().strftime("%Y-%m-%d %H:%M")

        archivio_nomi = [
            item["Nome File"] for item in st.session_state.archivio_file
        ]
        if file_name not in archivio_nomi:
          st.session_state.archivio_file.append({
              "Nome File": file_name,
              "Dimensione": file_size,
              "Data Caricamento": data_caricamento,
          })

        if file_name.endswith((".csv", ".xlsx", ".xls")):
          try:
            if file_name.endswith(".csv"):
              df_temp = pd.read_csv(uploaded_file)
            else:
              df_temp = pd.read_excel(uploaded_file)
            st.session_state.dati_finanziari = pd.concat(
                [st.session_state.dati_finanziari, df_temp], ignore_index=True
            )
          except Exception as e:
            st.error(f"Errore lettura file {file_name}: {e}")

      st.success("✅ File caricati e storicizzati con successo!")
      st.balloons()

  st.markdown("---")
  st.subheader("📚 Storico Documenti Salvati")
  if len(st.session_state.archivio_file) > 0:
    st.dataframe(
        pd.DataFrame(st.session_state.archivio_file), use_container_width=True
    )
  else:
    st.info("Nessun file presente nell'archivio storico.")


def finanze_page():
  from datetime import datetime

  st.title("💰 Gestione Finanziaria e Spese")
  st.markdown("Elenco dei movimenti sincronizzati o inseriti manualmente.")

  st.session_state.dati_finanziari = st.data_editor(
      st.session_state.dati_finanziari,
      num_rows="dynamic",
      use_container_width=True,
  )

  with st.expander("➕ Aggiungi Nuova Transazione Manuale"):
    with st.form("form_spesa"):
      d_data = st.date_input("Data", datetime.today())
      d_desc = st.text_input("Descrizione / Causale")
      d_imp = st.number_input(
          "Importo (€) (usa il segno meno per le spese)", value=0.00
      )
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


def guide_lavoro_page():
  st.title("📚 Cheat Sheet & Guide Operative")
  st.markdown("Consulenza rapida per i software di lavoro.")

  software_scelto = st.selectbox(
      "Seleziona Software",
      ["Bpoint", "Zucchetti Paghe", "Agenzia delle Entrate", "Altro"],
  )
  st.text_area(
      f"Note e procedure per {software_scelto}:",
      placeholder="Scrivi o incolla qui i tuoi appunti...",
      height=300,
  )


# --- STRUTTURA DI NAVIGAZIONE NATIVA ST.NAVIGATION ---
pg = st.navigation({
    "Panoramica": [st.Page(home_page, title="🏠 Home & KPI", default=True)],
    "Gestione Dati": [
        st.Page(archivio_file_page, title="📁 Archivio File"),
        st.Page(finanze_page, title="💰 Finanze & Spese"),
    ],
    "Lavoro & Utility": [
        st.Page(guide_lavoro_page, title="📚 Guide Lavoro (Bpoint/Zucchetti)")
    ],
})

# Esegue la pagina selezionata
pg.run()
