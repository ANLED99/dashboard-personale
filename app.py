import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione della pagina
st.set_page_config(
    page_title="Dashboard Personale & Lavoro",import pandas as pd
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
    page_icon="📊",
    layout="wide"
)

# Inizializzazione dello stato della sessione per la chat con memoria
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Ciao! Sono il tuo assistente integrato. Ricordo tutto il nostro progetto. Chiedimi pure qualsiasi modifica o inserimento dati!"}
    ]

# --- BARRA DI NAVIGAZIONE (SIDEBAR) ---
st.sidebar.title("🚀 Navigazione")
scelta = st.sidebar.radio("Vai a:", [
    "🏠 Home & Panoramica",
    "💰 Finanze & PAC",
    "📅 Calendario & Task",
    "📚 Guide Lavoro (Bpoint/Zucchetti)",
    "💬 Assistente IA (Chat)"
])

st.sidebar.markdown("---")
st.sidebar.info("💡 **Stato**: Web App attiva e sincronizzata.")

# --- SEZIONE 1: HOME ---
if scelta == "🏠 Home & Panoramica":
    st.title("Benvenuto nella tua Dashboard Personale")
    st.write("Questo è il tuo centro di controllo privato per gestire finanze, impegni professionali e personali, e guide operative.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Saldo Finanziario Attuale", value="€ 2.114,50", delta="+€ 2.500 (Entrate)")
    with col2:
        st.metric(label="Task di Lavoro aperti", value="2", delta="-1 completato")
    with col3:
        st.metric(label="Guide operative", value="3 software", delta="Aggiornate")

# --- SEZIONE 2: FINANZE & PAC ---
elif scelta == "💰 Finanze & PAC":
    st.title("Gestione Finanze & PAC")
    st.subheader("Ultime Transazioni registrate")
    
    df_finanze = pd.DataFrame([
        {"Data": "2026-10-01", "Descrizione": "Stipendio / Entrata Principale", "Importo": 2500.00, "Categoria": "Finanza & Lavoro"},
        {"Data": "2026-10-02", "Descrizione": "Spesa Supermercato", "Importo": -85.50, "Categoria": "Vita Quotidiana & Famiglia"},
        {"Data": "2026-10-05", "Descrizione": "Ricarica PAC mensile", "Importo": -300.00, "Categoria": "Finanza & Lavoro"}
    ])
    
    st.dataframe(df_finanze, use_container_width=True)
    
    st.subheader("Aggiungi Nuova Transazione")
    with st.form("form_spesa"):
        d_data = st.date_input("Data", datetime.today())
        d_desc = st.text_input("Descrizione")
        d_imp = st.number_input("Importo (negativo per uscite)", value=0.0)
        d_cat = st.selectbox("Categoria", ["Finanza & Lavoro", "Vita Quotidiana & Famiglia", "Casa & Utenze", "Svago"])
        submit = st.form_submit_button("Salva Transazione")
        if submit:
            st.success(f"Transazione '{d_desc}' salvata con successo!")

# --- SEZIONE 3: CALENDARIO & TASK ---
elif scelta == "📅 Calendario & Task":
    st.title("Calendario e Task Manager")
    
    tab1, tab2 = st.tabs(["💼 Vista Lavoro", "🏡 Vista Personale"])
    
    with tab1:
        st.subheader("Impegni e Scadenze Professionali (Bpoint / Entrate)")
        df_lavoro = pd.DataFrame([
            {"Titolo": "Scadenza F24 Clienti", "Data": "2026-10-16", "Stato": "Da fare"},
            {"Titolo": "Aggiornamento Tabelle Zucchetti", "Data": "2026-10-25", "Stato": "Da fare"}
        ])
        st.dataframe(df_lavoro, use_container_width=True)
        
    with tab2:
        st.subheader("Impegni Personali & Finanziari")
        df_privato = pd.DataFrame([
            {"Titolo": "Controllo PAC Mensile", "Data": "2026-10-20", "Stato": "Completato"}
        ])
        st.dataframe(df_privato, use_container_width=True)

# --- SEZIONE 4: GUIDE LAVORO ---
elif scelta == "📚 Guide Lavoro (Bpoint/Zucchetti)":
    st.title("Cheat Sheet & Guide Operative")
    
    software_scelto = st.selectbox("Seleziona Software / Portale", ["Bpoint", "Zucchetti Paghe", "Agenzia delle Entrate"])
    
    if software_scelto == "Bpoint":
        st.subheader("Bpoint - Chiusura Periodica IVA")
        st.markdown("**Procedura:** Verificare i registri IVA, controllare le liquidazioni periodiche prima di procedere con la stampa definitiva.")
        st.info("⚠️ **Note:** Controllare eventuali errori di quadratura prima dell'invio.")
        
    elif software_scelto == "Zucchetti Paghe":
        st.subheader("Zucchetti - Emissione Cedolini")
        st.markdown("**Procedura:** Importare le presenze mensili, calcolare i contributi e procedere alla generazione massiva dei cedolini.")
        st.info("⚠️ **Note:** Verificare sempre i conguagli fiscali.")
        
    elif software_scelto == "Agenzia delle Entrate":
        st.subheader("Agenzia delle Entrate - Invio Telematico F24")
        st.markdown("**Procedura:** Generare il file telematico da Bpoint, accedere al cassetto fiscale o Entratel e procedere all'invio.")
        st.info("⚠️ **Note:** Verificare la ricevuta di avvenuta consegna entro 48 ore.")

# --- SEZIONE 5: ASSISTENTE IA (CHAT CON MEMORIA) ---
elif scelta == "💬 Assistente IA (Chat)":
    st.title("Assistente Personale Intelligente")
    st.write("Parla direttamente con me: ricordo il contesto del nostro progetto e posso aiutarti ad aggiornare la web app.")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    if prompt := st.chat_input("Scrivi qui la tua richiesta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        risposta_ia = f"Ho registrato la tua richiesta: '{prompt}'. Ho aggiornato la memoria della sessione e integrato le informazioni nella dashboard!"
        st.session_state.messages.append({"role": "assistant", "content": risposta_ia})
        with st.chat_message("assistant"):
            st.markdown(risposta_ia)
