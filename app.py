from datetime import datetime
import pandas as pd
import streamlit as st

# Configurazione della pagina (stile esteso e pulito)
st.set_page_config(
    page_title="Dashboard Personale & Lavoro", page_icon="✨", layout="wide"
)

# --- PERSONALIZZAZIONE GRAFICA CSS ---
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #4f46e5;
    }
    .custom-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Inizializzazione dello stato della sessione per la chat
if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "assistant",
      "content": (
          "Ciao! Sono il tuo assistente integrato. La dashboard è pronta per"
          " accogliere i tuoi file e dati reali. Chiedimi qualsiasi modifica!"
      ),
  }]

# --- BARRA DI NAVIGAZIONE (SIDEBAR) ---
st.sidebar.title("🚀 Centro di Controllo")
scelta = st.sidebar.selectbox(
    "Vai a:",
    [
        "🏠 Home & Panoramica",
        "📁 Gestione File & Dati Reali",
        "💰 Finanze & PAC",
        "📅 Calendario & Task",
        "📚 Guide Lavoro (Bpoint/Zucchetti)",
        "💬 Assistente IA (Chat)",
    ],
)

st.sidebar.markdown("---")
st.sidebar.success("🟢 **Stato Sistema**: Online & Sincronizzato")

# --- SEZIONE 1: HOME ---
if scelta == "🏠 Home & Panoramica":
  st.title("✨ Benvenuto nella tua Dashboard Privata")
  st.markdown(
      "Un unico centro di controllo per gestire i tuoi file, le finanze,"
      " impegni professionali e guide operative."
  )

  st.markdown("<br>", unsafe_allow_html=True)

  col1, col2, col3 = st.columns(3)
  with col1:
    st.metric(
        label="💳 Situazione Finanziaria",
        value="Carica file",
        delta="Dati in tempo reale",
    )
  with col2:
    st.metric(
        label="📌 Task & Attività",
        value="Pronto",
        delta="Nessuna scadenza critica",
    )
  with col3:
    st.metric(
        label="📚 Libreria Guide", value="Attiva", delta="Bpoint / Zucchetti"
    )

  st.markdown("<br>", unsafe_allow_html=True)
  st.info(
      "💡 **Come procedere:** Usa il menu a tendina laterale per navigare"
      " nelle sezioni, caricare i tuoi file Excel/CSV o consultare le guide."
  )

# --- SEZIONE 2: GESTIONE FILE & DATI REALI ---
elif scelta == "📁 Gestione File & Dati Reali":
  st.title("📁 Gestione e Caricamento File")
  st.markdown(
      "Trascina o carica qui i tuoi file Excel (`.xlsx`, `.xls`) o CSV per"
      " visualizzarli e modificarli al volo."
  )

  uploaded_file = st.file_uploader(
      "Seleziona il tuo file di dati personali:",
      type=["xlsx", "xls", "csv"],
  )

  if uploaded_file is not None:
    try:
      if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
      else:
        df = pd.read_excel(uploaded_file)

      st.success(f"File '{uploaded_file.name}' caricato con successo!")

      st.markdown("### ✏️ Tabella Interattiva (Modificabile)")
      st.info(
          "Fai doppio clic sulle celle per modificare i valori direttamente"
          " dalla pagina web."
      )

      edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

      st.markdown("### 💾 Esporta Dati Aggiornati")
      csv_data = edited_df.to_csv(index=False).encode("utf-8")
      st.download_button(
          label="📥 Scarica File Aggiornato (CSV)",
          data=csv_data,
          file_name="miei_dati_aggiornati.csv",
          mime="text/csv",
      )

    except Exception as e:
      st.error(f"Errore nella lettura del file: {e}")
  else:
    st.warning(
        "Nessun file caricato al momento. Carica un file per iniziare a"
        " gestirlo."
    )

# --- SEZIONE 3: FINANZE & PAC ---
elif scelta == "💰 Finanze & PAC":
  st.title("💰 Gestione Finanze & PAC")
  st.markdown(
      "Qui puoi monitorare transazioni, entrate e uscite con tabelle pulite e"
      " pronte per i tuoi dati."
  )

  # Tabella vuota pronta per i dati reali dell'utente
  df_finanze = pd.DataFrame(
      columns=["Data", "Descrizione", "Importo (€)", "Categoria"]
  )

  st.subheader("Registro Transazioni")
  edited_finanze = st.data_editor(
      df_finanze, num_rows="dynamic", use_container_width=True
  )

  with st.expander("➕ Aggiungi Nuova Transazione Rapida"):
    with st.form("form_spesa"):
      d_data = st.date_input("Data", datetime.today())
      d_desc = st.text_input("Descrizione / Causale")
      d_imp = st.number_input(
          "Importo (usa segno meno per le uscite)", value=0.00
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
      submit = st.form_submit_button("Salva Transazione")
      if submit:
        st.success(f"Transazione '{d_desc}' registrata correttamente!")

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
  st.markdown(
      "Consulta rapidamente le procedure per i software gestionali e"
      " professionali."
  )

  software_scelto = st.selectbox(
      "Seleziona Software / Portale",
      ["Bpoint", "Zucchetti Paghe", "Agenzia delle Entrate", "Altro software"],
  )

  if software_scelto == "Bpoint":
    st.subheader("🔹 Bpoint - Procedure Principali")
    st.markdown(
        "Inserisci qui le tue note o procedure operative per Bpoint (es."
        " liquidazioni IVA, stampe periodiche, gestione clienti)."
    )
    st.text_area(
        "Note operative Bpoint:",
        placeholder="Scrivi qui i passaggi chiave...",
        height=150,
    )

  elif software_scelto == "Zucchetti Paghe":
    st.subheader("🔹 Zucchetti - Procedure Paghe e Presenze")
    st.markdown(
        "Inserisci qui le tue note per l'importazione presenze e calcolo"
        " cedolini."
    )
    st.text_area(
        "Note operative Zucchetti:",
        placeholder="Scrivi qui i passaggi chiave...",
        height=150,
    )

  elif software_scelto == "Agenzia delle Entrate":
    st.subheader("🔹 Agenzia delle Entrate - Invii Telematici")
    st.markdown("Guide e promemoria per F24, cassetti fiscali e trasmissioni.")
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
      "Parla direttamente con me: chiedimi di modificare la grafica, aggiungere"
      " nuove sezioni o aggiornare il codice."
  )

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input(
      "Scrivi qui la tua richiesta o modifica desiderata..."
  ):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    risposta_ia = (
        f"Ho ricevuto la richiesta: '{prompt}'. Quando desideri applicarla,"
        " chiedimi il codice aggiornato e lo adatteremo subito alla tua"
        " dashboard!"
    )
    st.session_state.messages.append({"role": "assistant", "content": risposta_ia})
    with st.chat_message("assistant"):
      st.markdown(risposta_ia)
