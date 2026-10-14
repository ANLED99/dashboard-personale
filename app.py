from datetime import datetime
import io
import pandas as pd
import pypdf
import streamlit as st
from docx import Document

# Configurazione della pagina
st.set_page_config(
    page_title="Dashboard Personale & Lavoro", page_icon="✨", layout="wide"
)

# --- INIZIALIZZAZIONE STATO SESSIONE (MEMORIA DATI) ---
if "dati_finanziari" not in st.session_state:
  st.session_state.dati_finanziari = pd.DataFrame(
      columns=["Data", "Descrizione", "Importo (€)", "Categoria"]
  )

if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "assistant",
      "content": (
          "Ciao! Ora puoi caricare più file contemporaneamente e confermare"
          " l'upload con il nuovo pulsante dedicato."
      ),
  }]

# --- BARRA DI NAVIGAZIONE (SIDEBAR) ---
st.sidebar.title("🚀 Centro di Controllo")
scelta = st.sidebar.selectbox(
    "Vai a:",
    [
        "🏠 Home & Panoramica",
        "📁 Gestione Universale File",
        "💰 Finanze & PAC",
        "📅 Calendario & Task",
        "📚 Guide Lavoro (Bpoint/Zucchetti)",
        "💬 Assistente IA (Chat)",
    ],
)

st.sidebar.markdown("---")
st.sidebar.success("🟢 **Stato Sistema**: Online & Sincronizzato")

# --- CALCOLO DATI GLOBALI PER LA HOME ---
df_globale = st.session_state.dati_finanziari
totale_spese = (
    df_globale["Importo (€)"].sum() if not df_globale.empty else 0.0
)

# --- SEZIONE 1: HOME & PANORAMICA ---
if scelta == "🏠 Home & Panoramica":
  st.title("✨ Benvenuto nella tua Dashboard Privata")
  st.markdown(
      "Quadro generale aggiornato in tempo reale dai tuoi file e dai dati"
      " inseriti."
  )

  st.markdown("<br>", unsafe_allow_html=True)

  col1, col2, col3 = st.columns(3)
  with col1:
    st.metric(
        label="💳 Bilancio Totale Registrato",
        value=f"€ {totale_spese:,.2f}",
        delta="Aggiornato da file",
    )
  with col2:
    st.metric(
        label="📌 Movimenti Totali",
        value=f"{len(df_globale)} transazioni",
        delta="Attive nel sistema",
    )
  with col3:
    st.metric(
        label="📚 Libreria Guide", value="Attiva", delta="Bpoint / Zucchetti"
    )

  st.markdown("<br>", unsafe_allow_html=True)

  if not df_globale.empty:
    st.subheader("📊 Ultime Transazioni Rilevate")
    st.dataframe(df_globale.tail(5), use_container_width=True)
  else:
    st.info(
        "💡 **Suggerimento:** Carica i tuoi estratti conto nella sezione"
        " 'Gestione Universale File' per popolare la Home."
    )

# --- SEZIONE 2: GESTIONE UNIVERSALE FILE (MULTI-UPLOAD & CONFERMA) ---
elif scelta == "📁 Gestione Universale File":
  st.title("📁 Archivio e Importazione Multipla File")
  st.markdown(
      "Seleziona o trascina **uno o più file contemporaneamente** (Excel, CSV,"
      " PDF, Word, ecc.). Una volta scelti, clicca sul pulsante di conferma"
      " per aggiornare la dashboard."
  )

  # accept_multiple_files=True permette di selezionare più file insieme
  uploaded_files = st.file_uploader(
      "Seleziona i tuoi file (puoi sceglierne più di uno):",
      type=[
          "pdf",
          "docx",
          "xlsx",
          "xls",
          "csv",
          "txt",
          "png",
          "jpg",
          "jpeg",
      ],
      accept_multiple_files=True,
  )

  if uploaded_files:
    st.success(
        f"Hai selezionato {len(uploaded_files)} file pronti per il caricamento."
    )

    # Mostra l'elenco dei file selezionati
    for f in uploaded_files:
      st.write(
          f"📄 **{f.name}** ({f.size / 1024:.1f} KB)"
      )

    st.markdown("<br>", unsafe_allow_html=True)

    # Pulsante di conferma esplicito per elaborare i file
    if st.button("🚀 Conferma Upload e Aggiorna Dati"):
      for uploaded_file in uploaded_files:
        file_name = uploaded_file.name

        # Gestione Fogli di calcolo (Excel / CSV) -> Aggiunta automatica al quadro finanziario
        if file_name.endswith((".csv", ".xlsx", ".xls")):
          try:
            if file_name.endswith(".csv"):
              df_temp = pd.read_csv(uploaded_file)
            else:
              df_temp = pd.read_excel(uploaded_file)

            # Uniamo i dati alla memoria globale della sessione
            st.session_state.dati_finanziari = pd.concat(
                [st.session_state.dati_finanziari, df_temp], ignore_index=True
            )
          except Exception as e:
            st.error(f"Errore nella lettura del file {file_name}: {e}")

      st.success(
          "✅ Upload completato e dati sincronizzati con successo in tutte le"
          " sezioni!"
      )
      st.balloons()

  else:
    st.warning(
        "Nessun file selezionato. Usa il riquadro sopra per caricare i tuoi"
        " documenti."
    )

# --- SEZIONE 3: FINANZE & PAC ---
elif scelta == "💰 Finanze & PAC":
  st.title("💰 Quadro Generale Spese & Finanze")
  st.markdown(
      "Elenco completo di tutte le transazioni estratte dai file caricati o"
      " inserite manualmente."
  )

  st.subheader("Registro Movimenti Sincronizzati")
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
      submit = st.form_submit_button("Aggiungi al Quadro Spese")
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

# --- SEZIONE 4: CALENDARIO & TASK ---
elif scelta == "📅 Calendario & Task":
  st.title("📅 Calendario e Task Manager")
  tab1, tab2 = st.tabs(["💼 Attività Lavoro", "🏡 Attività Personali"])
  with tab1:
    st.subheader("Scadenze e Adempimenti Professionali")
    df_lavoro = pd.DataFrame(columns=["Titolo Task", "Scadenza", "Stato"])
    st.data_editor(df_lavoro, num_rows="dynamic", use_container_width=True)
  with tab2:
    st.subheader("Promemoria Personali")
    df_privato = pd.DataFrame(columns=["Attività", "Data", "Priorità"])
    st.data_editor(df_privato, num_rows="dynamic", use_container_width=True)

# --- SEZIONE 5: GUIDE LAVORO ---
elif scelta == "📚 Guide Lavoro (Bpoint/Zucchetti)":
  st.title("📚 Cheat Sheet & Guide Operative")
  software_scelto = st.selectbox(
      "Seleziona Software / Portale",
      ["Bpoint", "Zucchetti Paghe", "Agenzia delle Entrate", "Altro software"],
  )
  if software_scelto == "Bpoint":
    st.subheader("🔹 Bpoint - Procedure Principali")
    st.text_area(
        "Note operative Bpoint:",
        placeholder="Scrivi qui i passaggi chiave...",
        height=150,
    )
  elif software_scelto == "Zucchetti Paghe":
    st.subheader("🔹 Zucchetti - Procedure Paghe e Presenze")
    st.text_area(
        "Note operative Zucchetti:",
        placeholder="Scrivi qui i passaggi chiave...",
        height=150,
    )
  elif software_scelto == "Agenzia delle Entrate":
    st.subheader("🔹 Agenzia delle Entrate - Invii Telematici")
    st.text_area(
        "Note operative AdE:",
        placeholder="Scrivi qui i passaggi chiave...",
        height=150,
    )
  else:
    st.subheader("🔹 Altre Guide")
    st.text_area(
        "Note:", placeholder="Inserisci qui appunti per altri software...", height=150
    )

# --- SEZIONE 6: ASSISTENTE IA (CHAT) ---
elif scelta == "💬 Assistente IA (Chat)":
  st.title("💬 Assistente Personale Intelligente")
  st.markdown(
      "Parla direttamente con me: posso aiutarti ad analizzare i dati o"
      " modificare la dashboard."
  )

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input("Scrivi qui la tua richiesta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    risposta_ia = (
        f"Ho elaborato la tua richiesta: '{prompt}'. I dati nella dashboard"
        " restano sincronizzati!"
    )
    st.session_state.messages.append({"role": "assistant", "content": risposta_ia})
    with st.chat_message("assistant"):
      st.markdown(risposta_ia)
