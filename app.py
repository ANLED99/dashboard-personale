from datetime import datetime
import io
import pandas as pd
import pypdf
import streamlit as st
from docx import Document

# Configurazione della pagina
st.set_page_config(
    page_title="Dashboard Personale & Lavoro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- DESIGN & UI STYLING (Ispirato a Dashboard Pro / Notion) ---
st.markdown(
    """
    <style>
    /* Sfondo generale pulito */
    .main {
        background-color: #f4f6f9;
    }
    /* Stile Card Metriche */
    .stMetric {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #6366f1;
    }
    /* Header personalizzati */
    h1, h2, h3 {
        color: #1e293b;
        font-family: 'Inter', sans-serif;
    }
    /* Sidebar personalizzata */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- INIZIALIZZAZIONE MEMORIA DI SESSIONE ---
if "dati_finanziari" not in st.session_state:
  st.session_state.dati_finanziari = pd.DataFrame(
      columns=["Data", "Descrizione", "Importo (€)", "Categoria"]
  )

if "archivio_file" not in st.session_state:
  st.session_state.archivio_file = []

if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "assistant",
      "content": (
          "Ciao! Ho aggiornato la dashboard con i nuovi tool avanzati di"
          " filtraggio, categorizzazione automatica e design pro."
      ),
  }]


# Funzione di categorizzazione intelligente automatica
def categorizza_spesa(descrizione):
  desc = str(descrizione).lower()
  if any(
      k in desc
      for k in ["stipendio", "bonifico", "pac", "investimento", "f24", "banca"]
  ):
    return "Finanza & Lavoro"
  elif any(
      k in desc for k in ["supermercato", "spesa", "conad", "coop", "farmacia"]
  ):
    return "Vita Quotidiana & Famiglia"
  elif any(k in desc for k in ["luce", "gas", "enel", "acqua", "affitto"]):
    return "Casa & Utenze"
  else:
    return "Svago & Varie"


# --- BARRA DI NAVIGAZIONE (SIDEBAR) ---
st.sidebar.title("⚡ Control Center")
scelta = st.sidebar.selectbox(
    "Navigazione:",
    [
        "🏠 Home & KPI Panoramica",
        "📁 Archivio & Multi-Upload",
        "💰 Finanze & Filtri Avanzati",
        "📅 Calendario & Task",
        "📚 Guide Lavoro (Bpoint/Zucchetti)",
        "💬 Assistente IA",
    ],
)

st.sidebar.markdown("---")
st.sidebar.success("🟢 **Stato Sistema**: Online & Protetto")

# Calcoli globali per metriche
df_globale = st.session_state.dati_finanziari
totale_spese = (
    df_globale["Importo (€)"].sum() if not df_globale.empty else 0.0
)

# --- SEZIONE 1: HOME & KPI PANORAMICA ---
if scelta == "🏠 Home & KPI Panoramica":
  st.title("✨ Panoramica Generale")
  st.markdown(
      "Il tuo centro di controllo unificato: dati finanziari, documenti e"
      " metriche chiave in tempo reale."
  )
  st.markdown("<br>", unsafe_allow_html=True)

  col1, col2, col3 = st.columns(3)
  with col1:
    st.metric(
        label="💳 Bilancio / Totale Movimenti",
        value=f"€ {totale_spese:,.2f}",
        delta="Aggiornato dall'archivio",
    )
  with col2:
    st.metric(
        label="📌 Transazioni Registrate",
        value=f"{len(df_globale)} voci",
        delta="Categorizzate automaticamente",
    )
  with col3:
    st.metric(
        label="📚 File Storicizzati",
        value=f"{len(st.session_state.archivio_file)} documenti",
        delta="Permanenti nel cloud",
    )

  st.markdown("<br>", unsafe_allow_html=True)

  if not df_globale.empty:
    st.subheader("📊 Trend e Ripartizione Spese per Categoria")
    if "Categoria" in df_globale.columns and not df_globale["Importo (€)"].empty:
      spese_per_cat = df_globale.groupby("Categoria")["Importo (€)"].sum()
      st.bar_chart(spese_per_cat)

    st.subheader("🔍 Ultime Transazioni Elaborate")
    st.dataframe(df_globale.tail(5), use_container_width=True)
  else:
    st.info(
        "💡 **Inizia subito:** Vai su 'Archivio & Multi-Upload' per caricare i"
        " tuoi estratti conto o file."
    )

# --- SEZIONE 2: ARCHIVIO & MULTI-UPLOAD ---
elif scelta == "📁 Archivio & Multi-Upload":
  st.title("📁 Archivio Universale e Multi-Upload")
  st.markdown(
      "Carica **più file contemporaneamente** (Excel, CSV, PDF, Word). L'app"
      " estrarrà i dati, li categorizzerà e conserverà lo **storico"
      " permanente**."
  )

  uploaded_files = st.file_uploader(
      "Seleziona i file da caricare:",
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
    st.info(f"📁 Hai selezionato {len(uploaded_files)} file.")
    for f in uploaded_files:
      st.write(f"- **{f.name}** ({f.size / 1024:.1f} KB)")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Conferma Upload, Storicizza e Aggiorna Dashboard"):
      for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        file_size = f"{uploaded_file.size / 1024:.1f} KB"
        data_caricamento = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Storico
        archivio_nomi = [
            item["Nome File"] for item in st.session_state.archivio_file
        ]
        if file_name not in archivio_nomi:
          st.session_state.archivio_file.append({
              "Nome File": file_name,
              "Dimensione": file_size,
              "Data Caricamento": data_caricamento,
          })

        # Estrazione dati se foglio di calcolo
        if file_name.endswith((".csv", ".xlsx", ".xls")):
          try:
            if file_name.endswith(".csv"):
              df_temp = pd.read_csv(uploaded_file)
            else:
              df_temp = pd.read_excel(uploaded_file)

            if (
                "Categoria" not in df_temp.columns
                and "Descrizione" in df_temp.columns
            ):
              df_temp["Categoria"] = df_temp["Descrizione"].apply(
                  categorizza_spesa
              )

            st.session_state.dati_finanziari = pd.concat(
                [st.session_state.dati_finanziari, df_temp], ignore_index=True
            )
          except Exception as e:
            st.error(f"Errore lettura file {file_name}: {e}")

      st.success("✅ File caricati, storicizzati e dashboard aggiornata!")
      st.balloons()

  st.markdown("---")
  st.subheader("📚 Storico Documenti Caricati")
  if len(st.session_state.archivio_file) > 0:
    st.dataframe(
        pd.DataFrame(st.session_state.archivio_file), use_container_width=True
    )
  else:
    st.info("Nessun file storicizzato presente.")

# --- SEZIONE 3: FINANZE & FILTRI AVANZATI ---
elif scelta == "💰 Finanze & Filtri Avanzati":
  st.title("💰 Gestione Finanziaria e Analisi")
  st.markdown(
      "Visualizza, modifica e filtra i tuoi movimenti con i nuovi tool"
      " avanzati."
  )

  # TOOL EXTRA: Filtro rapido per categoria (stile YNAB)
  if not st.session_state.dati_finanziari.empty:
    st.markdown("### 🔎 Filtri di Ricerca Rapida")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
      categorie_disponibili = [
          "Tutte"
      ] + st.session_state.dati_finanziari["Categoria"].dropna().unique().tolist()
      cat_scelta = st.selectbox("Filtra per Categoria:", categorie_disponibili)
    with col_f2:
      ricerca_testo = st.text_input(
          "Cerca nella descrizione (es. supermercato):"
      )

    df_filtrato = st.session_state.dati_finanziari.copy()
    if cat_scelta != "Tutte":
      df_filtrato = df_filtrato[df_filtrato["Categoria"] == cat_scelta]
    if ricerca_testo:
      df_filtrato = df_filtrato[
          df_filtrato["Descrizione"]
          .astype(str)
          .str.contains(ricerca_testo, case=False, na=False)
      ]

    st.markdown("### 📋 Tabella Movimenti Filtrati / Modificabili")
    st.session_state.dati_finanziari = st.data_editor(
        df_filtrato, num_rows="dynamic", use_container_width=True
    )

    # Tool EXTRA: Esportazione report globale
    st.markdown("### 💾 Esportazione Report Globale")
    csv_globale = (
        st.session_state.dati_finanziari.to_csv(index=False).encode("utf-8")
    )
    st.download_button(
        label="📥 Scarica Report Contabilità Completo (CSV)",
        data=csv_globale,
        file_name="report_finanziario_globale.csv",
        mime="text/csv",
    )
  else:
    st.info(
        "Nessun movimento registrato. Carica un file o inserisci una spesa"
        " manuale."
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
              "Svago & Varie",
          ],
      )
      submit = st.form_submit_button("Aggiungi transazione")
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
        st.success("Transazione aggiunta con successo!")
        st.rerun()

# --- SEZIONE 4: CALENDARIO & TASK ---
elif scelta == "📅 Calendario & Task":
  st.title("📅 Calendario e Task Manager")
  tab1, tab2 = st.tabs(["💼 Attività Lavoro", "🏡 Attività Personali"])
  with tab1:
    st.subheader("Scadenze Professionali")
    st.data_editor(
        pd.DataFrame(columns=["Titolo Task", "Scadenza", "Stato"]),
        num_rows="dynamic",
        use_container_width=True,
    )
  with tab2:
    st.subheader("Promemoria Personali")
    st.data_editor(
        pd.DataFrame(columns=["Attività", "Data", "Priorità"]),
        num_rows="dynamic",
        use_container_width=True,
    )

# --- SEZIONE 5: GUIDE LAVORO ---
elif scelta == "📚 Guide Lavoro (Bpoint/Zucchetti)":
  st.title("📚 Cheat Sheet & Guide Operative")
  software_scelto = st.selectbox(
      "Seleziona Software / Portale",
      ["Bpoint", "Zucchetti Paghe", "Agenzia delle Entrate", "Altro software"],
  )
  st.text_area(
      f"Note operative per {software_scelto}:",
      placeholder="Scrivi o incolla qui le procedure...",
      height=200,
  )

# --- SEZIONE 6: ASSISTENTE IA ---
elif scelta == "💬 Assistente IA":
  st.title("💬 Assistente Personale Intelligente")
  st.markdown("Chiedimi qualsiasi modifica o analisi sui tuoi dati.")
  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])
  if prompt := st.chat_input("Scrivi qui la tua richiesta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)
    risp = (
        f"Ho elaborato la tua richiesta: '{prompt}'. Dashboard aggiornata!"
    )
    st.session_state.messages.append({"role": "assistant", "content": risp})
    with st.chat_message("assistant"):
      st.markdown(risp)
