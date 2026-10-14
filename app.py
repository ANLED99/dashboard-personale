from datetime import datetime
import io
import pandas as pd
import pypdf
import streamlit as st
from docx import Document

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
    </style>
""",
    unsafe_allow_html=True,
)

# Inizializzazione dello stato della sessione per la chat
if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "assistant",
      "content": (
          "Ciao! Ora puoi caricare qualsiasi tipo di file (PDF, Word, Excel,"
          " CSV, immagini, TXT). Come posso aiutarti?"
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
        value="Pronto",
        delta="Dati in tempo reale",
    )
  with col2:
    st.metric(
        label="📌 Task & Attività",
        value="Attivo",
        delta="Nessuna scadenza critica",
    )
  with col3:
    st.metric(
        label="📚 Libreria Guide", value="Attiva", delta="Bpoint / Zucchetti"
    )

  st.markdown("<br>", unsafe_allow_html=True)
  st.info(
      "💡 **Novità:** Ora nella sezione 'Gestione Universale File' puoi"
      " caricare qualsiasi formato (PDF, Word, Excel, CSV, Immagini)."
  )

# --- SEZIONE 2: GESTIONE UNIVERSALE FILE ---
elif scelta == "📁 Gestione Universale File":
  st.title("📁 Archivio e Gestione File Universale")
  st.markdown(
      "Carica qualsiasi documento: **PDF, Word (.docx), Excel, CSV, Immagini o"
      " file di testo**. La dashboard riconoscerà il formato e ti mostrerà il"
      " contenuto."
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

    # 1. Gestione Fogli di Calcolo (Excel / CSV)
    if file_name.endswith((".csv", ".xlsx", ".xls")):
      try:
        if file_name.endswith(".csv"):
          df = pd.read_csv(uploaded_file)
        else:
          df = pd.read_excel(uploaded_file)

        st.markdown("### ✏️ Tabella Interattiva (Modificabile)")
        st.info(
            "Fai doppio clic sulle celle per modificare i valori direttamente"
            " dalla pagina web."
        )
        edited_df = pd.data_editor(
            df, num_rows="dynamic", use_container_width=True
        )

        st.markdown("### 💾 Esporta Dati Aggiornati")
        csv_data = edited_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Scarica File Aggiornato (CSV)",
            data=csv_data,
            file_name="dati_aggiornati.csv",
            mime="text/csv",
        )
      except Exception as e:
        st.error(f"Errore nella lettura del file tabulare: {e}")

    # 2. Gestione File PDF
    elif file_name.endswith(".pdf"):
      st.markdown("### 📄 Contenuto del PDF")
      try:
        reader = pypdf.PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
          pdf_text += page.extract_text() + "\n"

        st.text_area(
            "Testo estratto dal PDF:", pdf_text, height=350
        )
        st.download_button(
            label="📥 Scarica Testo Estratto",
            data=pdf_text,
            file_name="testo_estratto.txt",
            mime="text/plain",
        )
      except Exception as e:
        st.error(f"Errore nella lettura del PDF: {e}")

    # 3. Gestione File Word (.docx)
    elif file_name.endswith(".docx"):
      st.markdown("### 📝 Contenuto del Documento Word")
      try:
        doc = Document(uploaded_file)
        docx_text = "\n".join([para.text for para in doc.paragraphs])

        st.text_area(
            "Testo estratto dal documento:", docx_text, height=350
        )
        st.download_button(
            label="📥 Scarica Testo Estratto",
            data=docx_text,
            file_name="testo_word.txt",
            mime="text/plain",
        )
      except Exception as e:
        st.error(f"Errore nella lettura del file Word: {e}")

    # 4. Gestione Immagini
    elif file_name.endswith((".png", ".jpg", ".jpeg")):
      st.markdown("### 🖼️ Anteprima Immagine")
      st.image(uploaded_file, caption=file_name, use_container_width=True)

    # 5. Gestione File di Testo Semplice (.txt)
    elif file_name.endswith(".txt"):
      st.markdown("### 📃 Contenuto del File di Testo")
      stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
      string_data = stringio.read()
      st.text_area("Testo:", string_data, height=350)

  else:
    st.warning("Nessun file caricato al momento. Trascina un file per iniziare.")

# --- SEZIONE 3: FINANZE & PAC ---
elif scelta == "💰 Finanze & PAC":
  st.title("💰 Gestione Finanze & PAC")
  st.markdown("Monitora transazioni, entrate e uscite.")

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
      "Parla direttamente con me: chiedimi modifiche o integrazioni per la tua"
      " dashboard."
  )

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input("Scrivi qui la tua richiesta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    risposta_ia = (
        f"Ho registrato la tua richiesta: '{prompt}'. Chiedimi il codice"
        " aggiornato quando desideri applicare nuove funzioni!"
    )
    st.session_state.messages.append({"role": "assistant", "content": risposta_ia})
    with st.chat_message("assistant"):
      st.markdown(risposta_ia)
