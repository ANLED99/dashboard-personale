from datetime import datetime
import pandas as pd
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Dashboard Finanziaria & Lavoro", page_icon="⚡", layout="wide"
)

# --- STILE GRAFICO MODERN (CSS) ---
st.markdown(
    """
    <style>
    .main { background-color: #f8fafc; }
    .stMetric {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        border-left: 5px solid #4f46e5;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- INIZIALIZZAZIONE MEMORIA E CARICAMENTO CSV AUTOMATICO ---
if "dati_finanziari" not in st.session_state:
  try:
    st.session_state.dati_finanziari = pd.read_csv(
        "movimenti_estratti_conto_2026.csv"
    )
  except Exception:
    st.session_state.dati_finanziari = pd.DataFrame(
        columns=["Data", "Descrizione", "Importo (€)", "Categoria"]
    )

if "archivio_file" not in st.session_state:
  st.session_state.archivio_file = []


# --- FUNZIONI DELLE SEZIONI ---
def home_page():
  st.title("⚡ Centro di Controllo Finanziario")
  st.markdown(
      "Panoramica intelligente dei tuoi estratti conto e indicatori di bilancio"
      " in tempo reale."
  )
  st.markdown("---")

  df = st.session_state.dati_finanziari

  if not df.empty:
    # Calcoli KPI avanzati
    entrate_totali = df[df["Importo (€)"] > 0]["Importo (€)"].sum()
    uscite_totali = df[df["Importo (€)"] < 0]["Importo (€)"].sum()
    bilancio_netto = entrate_totali + uscite_totali  # uscite sono negative

    col1, col2, col3, col4 = st.columns(4)
    with col1:
      st.metric(
          label="💰 Bilancio Netto Periodo", value=f"€ {bilancio_netto:,.2f}"
      )
    with col2:
      st.metric(label="📈 Entrate Totali", value=f"€ {entrate_totali:,.2f}")
    with col3:
      st.metric(
          label="📉 Uscite / Spese Totali", value=f"€ {uscite_totali:,.2f}"
      )
    with col4:
      st.metric(label="📌 Voci Registrate", value=f"{len(df)} transazioni")

    st.markdown("---")

    # TOOL 1: Grafico interattivo per Categoria
    st.subheader("📊 Analisi Spese per Categoria")
    col_g1, col_g2 = st.columns([2, 1])

    with col_g1:
      # Filtriamo solo le uscite per analizzare dove si spende di più
      df_uscite = df[df["Importo (€)"] < 0].copy()
      df_uscite["Importo Assoluto"] = df_uscite["Importo (€)"].abs()
      spese_per_cat = df_uscite.groupby("Categoria")[
          "Importo Assoluto"
      ].sum()
      st.bar_chart(spese_per_cat)

    with col_g2:
      st.markdown("### 💡 Insight Rapidi")
      if not spese_per_cat.empty:
        cat_max = spese_per_cat.idxmax()
        val_max = spese_per_cat.max()
        st.info(
            f"La categoria con più uscite è **{cat_max}** con un totale di"
            f" **€ {val_max:,.2f}**."
        )
      else:
        st.success("Nessuna spesa registrata.")

    st.markdown("---")

    # TOOL 2: Classifica delle Spese Più Maggiori (Top 5 Outliers)
    st.subheader("🚨 Top 5 Spese Più Rilevanti del Periodo")
    top_spese = df[df["Importo (€)"] < 0].nsmallest(5, "Importo (€)")
    st.dataframe(
        top_spese[["Data", "Descrizione", "Importo (€)", "Categoria"]],
        use_container_width=True,
    )

  else:
    st.warning(
        "Nessun dato finanziario trovato. Assicurati che il file"
        " 'movimenti_estratti_conto_2026.csv' sia caricato su GitHub."
    )


def analisi_avanzata_page():
  st.title("🔍 Tool di Filtro e Categorizzazione Avanzata")
  st.markdown(
      "Filtra i movimenti per intervallo di date, categoria o cerca parole"
      " chiave specifiche nei tuoi estratti conto."
  )

  df = st.session_state.dati_finanziari

  if not df.empty:
    col_f1, col_f2 = st.columns(2)
    with col_f1:
      cat_list = ["Tutte"] + df["Categoria"].dropna().unique().tolist()
      scelta_cat = st.selectbox("Filtra per Categoria:", cat_list)
    with col_f2:
      testo_ricerca = st.text_input("Cerca nella descrizione (es. Amazon, Conad, Vinted):")

    df_filtrato = df.copy()
    if scelta_cat != "Tutte":
      df_filtrato = df_filtrato[df_filtrato["Categoria"] == scelta_cat]
    if testo_ricerca:
      df_filtrato = df_filtrato[
          df_filtrato["Descrizione"]
          .astype(str)
          .str.contains(testo_ricerca, case=False, na=False)
      ]

    st.markdown(f"Trovate **{len(df_filtrato)}** transazioni corrispondenti:")

    # Tabella modificabile per ricategorizzare al volo
    st.session_state.dati_finanziari = st.data_editor(
        df_filtrato, num_rows="dynamic", use_container_width=True
    )

    # Tool di Download Report Filtrato
    csv_data = df_filtrato.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Scarica Report Filtrato in CSV",
        data=csv_data,
        file_name="report_finanziario_filtrato.csv",
        mime="text/csv",
    )
  else:
    st.info("Nessun dato disponibile da analizzare.")


def archivio_file_page():
  st.title("📁 Archivio Documenti e PDF")
  st.markdown("Consulta l'archivio dei documenti caricati nel sistema.")

  uploaded_files = st.file_uploader(
      "Carica altri documenti di supporto:",
      accept_multiple_files=True,
      type=["pdf", "docx", "xlsx", "csv"],
  )
  if uploaded_files:
    for f in uploaded_files:
      st.session_state.archivio_file.append(
          {"Nome File": f.name, "Dimensione": f"{f.size / 1024:.1f} KB"}
      )
    st.success("File aggiunti all'archivio con successo!")

  if st.session_state.archivio_file:
    st.dataframe(
        pd.DataFrame(st.session_state.archivio_file), use_container_width=True
    )
  else:
    st.info("Nessun file extra nell'archivio.")


def guide_lavoro_page():
  st.title("📚 Guide Operative Lavoro (Bpoint / Zucchetti)")
   software = st.selectbox("Seleziona Software", ["Bpoint", "Zucchetti Paghe", "AdE"])
  st.text_area(
      f"Note e procedure per {software}:",
      placeholder="Inserisci qui i tuoi promemoria...",
      height=300,
  )


# --- NAVIGAZIONE NATIVA STREAMLIT ---
pg = st.navigation({
    "Panoramica & KPI": [
        st.Page(home_page, title="🏠 Home & Bilancio", default=True)
    ],
    "Gestione Finanziaria": [
        st.Page(analisi_avanzata_page, title="💰 Analisi & Filtri Spese")
    ],
    "Archivio & Lavoro": [
        st.Page(archivio_file_page, title="📁 Archivio File"),
        st.Page(guide_lavoro_page, title="📚 Guide Lavoro"),
    ],
})

pg.run()
