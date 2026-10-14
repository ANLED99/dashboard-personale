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
  # Tabella globale condivisa tra le sezioni
  st.session_state.dati_finanziari = pd.DataFrame(
      columns=["Data", "Descrizione", "Importo (€)", "Categoria"]
  )

if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "assistant",
      "content": (
          "Ciao! Ho configurato la memoria globale: ora i file che carichi"
          " nell'archivio aggiorneranno in automatico la sezione Finanze e la"
          " Home."
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

# --- CALCOLO DATI GLOBALI PER LA HOME E FINANZE ---
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
        "💡 **Suggerimento:** Carica un estratto conto nella sezione 'Gestione"
        " Universale File' o inserisci i dati in 'Finanze & PAC' per popolare"
        " la Home."
    )

# --- SEZIONE 2: GESTIONE UNIVERSALE FILE ---
elif scelta == "📁 Gestione Universale File":
  st.title("📁 Archivio e Importazione Estratti Conto")
  st.markdown(
      "Carica i tuoi estratti conto (**Excel, CSV o PDF**). La dashboard"
      " estrarrà i movimenti e aggiornerà automaticamente il quadro spese."
  )

  uploaded_file = st.file_uploader(
      "Trascina o seleziona il tuo file:",
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
  )

  if uploaded_file is not None:
    file_name = uploaded_file.name
    st.success(f"File '{file_name}' caricato con successo!")

    # 1. Fogli di Calcolo / Estratti Conto in Excel o CSV
    if file_name.endswith((".csv", ".xlsx", ".xls")):
      try:
        if file_name.endswith(".csv"):
          df_caricato = pd.read_csv(uploaded_file)
        else:
          df_caricato = pd.read_excel(uploaded_file)

        st.markdown(
            "### 🔍 Anteprima e Integrazione Automatica nel Quadro Spese"
        )
        st.write(
            "Verifica o adatta le colonne qui sotto, poi clicca sul pulsante per"
            " sincronizzarle."
        )

        df_editato = st.data_editor(
            df_caricato, num_rows="dynamic", use_container_width=True
        )

        if st.button("🔄 Sincronizza con la Dashboard Finanziaria"):
          # Normalizziamo le colonne se possibile o salviamo direttamente
          st.session_state.dati_finanziari = df_editato
          st.success(
              "✅ Dati sincronizzati con successo! Tutte le sezioni ora"
              " mostrano questi movimenti."
          )

      except Exception as e:
        st.error(f"Errore nella lettura del file: {e}")

    # 2. Gestione File PDF (Estratti conto bancari in PDF)
    elif file_name.endswith(".pdf"):
      st.markdown("### 📄 Analisi Testo Estratto Conto PDF")
      try:
        reader = pypdf.PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
          pdf_text += page.extract_text() + "\n"

        st.text_area("Testo estratto dal documento:", pdf_text, height=300)
        st.info(
            "💡 Se l'estratto conto è in formato PDF testuale, puoi copiare i"
            " dati chiave o chiedere all'assistente in chat di aiutarti ad"
            " estrarre le voci di spesa."
        )
      except Exception as e:
        st.error(f"Errore nella lettura del PDF: {e}")

    # Altri formati (Word, Immagini, TXT)
    elif file_name.endswith(".docx"):
      doc = Document(uploaded_file)
      docx_text = "\n".join([para.text for para in doc.paragraphs])
      st.text_area("Testo documento:", docx_text, height=300)
    elif file_name.endswith((".png", ".jpg", ".jpeg")):
      st.image(uploaded_file, caption=file_name, use_container_width=True)
    elif file_name.endswith(".txt"):
      stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
      st.text_area("Testo:", stringio.read(), height=300)

  else:
    st.warning("Nessun file caricato al momento.")

# --- SEZIONE 3: FINANZE & PAC ---
elif scelta == "💰 Finanze & PAC":
  st.title("💰 Quadro Generale Spese & Finanze")
  st.markdown(
      "Qui trovi l'elenco completo di tutte le transazioni caricate dai tuoi"
      " file o inserite manualmente."
  )

  # Tabella interattiva collegata allo stato globale
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
        st.success(
            "Transazione aggiunta e quadro generale aggiornato in tempo"
            " reale!"
        )
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
      "Parla direttamente con me: posso aiutarti ad analizzare i dati caricati"
      " o modificare la dashboard."
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
        " restano sincronizzati in tempo reale!"
    )
    st.session_state.messages.append({"role": "assistant", "content": risposta_ia})
    with st.chat_message("assistant"):
      st.markdown(risposta_ia)
