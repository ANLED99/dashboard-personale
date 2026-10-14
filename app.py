from datetime import datetime
import pandas as pd
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Dashboard Dinamica Personale", page_icon="⚡", layout="wide"
)

# --- INIZIALIZZAZIONE CONFIGURAZIONI DI PERSONALIZZAZIONE (SESSION STATE) ---
if "tema_colore" not in st.session_state:
  st.session_state.tema_colore = "Indigo Professionale (#4f46e5)"
if "bordo_riquadri" not in st.session_state:
  st.session_state.bordo_riquadri = 12  # px
if "ombra_box" not in st.session_state:
  st.session_state.ombra_box = True

# Controllo visibilità sezioni
if "mostra_home" not in st.session_state:
  st.session_state.mostra_home = True
if "mostra_analisi" not in st.session_state:
  st.session_state.mostra_analisi = True
if "mostra_archivio" not in st.session_state:
  st.session_state.mostra_archivio = True
if "mostra_guide" not in st.session_state:
  st.session_state.mostra_guide = True

# Mappa dei colori in base alla scelta
colori_mappa = {
    "Indigo Professionale (#4f46e5)": "#4f46e5",
    "Verde Finanza (#059669)": "#059669",
    "Blu Elettrico (#2563eb)": "#2563eb",
    "Arancio Caldo (#ea580c)": "#ea580c",
    "Scuro Elegante (#334155)": "#334155",
}
colore_scelto = colori_mappa.get(st.session_state.tema_colore, "#4f46e5")
ombra_css = (
    "box-shadow: 0 4px 15px rgba(0,0,0,0.08);"
    if st.session_state.ombra_box
    else "box-shadow: none;"
)

# --- APPLICAZIONE DINAMICA DEGLI STILI CSS ---
st.markdown(
    f"""
    <style>
    .main {{ background-color: #f8fafc; }}
    .stMetric {{
        background-color: #ffffff;
        padding: 16px;
        border-radius: {st.session_state.bordo_riquadri}px;
        {ombra_css}
        border-left: 6px solid {colore_scelto};
    }}
    </style>
""",
    unsafe_allow_html=True,
)

# --- INIZIALIZZAZIONE MEMORIA E CARICAMENTO CSV AUTOMATICO ---
if "dati_finanziari" not in st.session_state:
  try:
    df_load = pd.read_csv("movimenti_estratti_conto_2026.csv")
    if "Importo (€)" in df_load.columns:
      df_load["Importo (€)"] = (
          df_load["Importo (€)"]
          .astype(str)
          .str.replace("€", "", regex=False)
          .str.replace(" ", "", regex=False)
          .str.replace(",", ".", regex=False)
      )
      df_load["Importo (€)"] = pd.to_numeric(
          df_load["Importo (€)"], errors="coerce"
      )
    st.session_state.dati_finanziari = df_load
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
    df["Importo (€)"] = pd.to_numeric(df["Importo (€)"], errors="coerce")

    entrate_totali = df[df["Importo (€)"] > 0]["Importo (€)"].sum()
    uscite_totali = df[df["Importo (€)"] < 0]["Importo (€)"].sum()
    bilancio_netto = entrate_totali + uscite_totali

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

    st.subheader("📊 Analisi Spese per Categoria")
    col_g1, col_g2 = st.columns([2, 1])

    with col_g1:
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

    st.subheader("🚨 Top 5 Spese Più Rilevanti del Periodo")
    top_spese = df[df["Importo (€)"] < 0].nsmallest(5, "Importo (€)")
    st.dataframe(
        top_spese[["Data", "Descrizione", "Importo (€)", "Categoria"]],
        use_container_width=True,
    )
  else:
    st.warning("Nessun dato finanziario trovato nel file CSV.")


def analisi_avanzata_page():
  st.title("🔍 Tool di Filtro e Categorizzazione Avanzata")
  st.markdown(
      "Filtra i movimenti per categoria o cerca parole chiave specifiche nei"
      " tuoi estratti conto."
  )

  df = st.session_state.dati_finanziari
  if not df.empty:
    df["Importo (€)"] = pd.to_numeric(df["Importo (€)"], errors="coerce")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
      cat_list = ["Tutte"] + df["Categoria"].dropna().unique().tolist()
      scelta_cat = st.selectbox("Filtra per Categoria:", cat_list)
    with col_f2:
      testo_ricerca = st.text_input("Cerca nella descrizione:")

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
    st.session_state.dati_finanziari = st.data_editor(
        df_filtrato, num_rows="dynamic", use_container_width=True
    )
  else:
    st.info("Nessun dato disponibile.")


def archivio_file_page():
  st.title("📁 Archivio Documenti e PDF")
  st.markdown("Consulta l'archivio dei documenti caricati nel sistema.")
  uploaded_files = st.file_uploader(
      "Carica altri documenti:",
      accept_multiple_files=True,
      type=["pdf", "docx", "xlsx", "csv"],
  )
  if uploaded_files:
    for f in uploaded_files:
      st.session_state.archivio_file.append(
          {"Nome File": f.name, "Dimensione": f"{f.size / 1024:.1f} KB"}
      )
    st.success("File aggiunti con successo!")
  if st.session_state.archivio_file:
    st.dataframe(
        pd.DataFrame(st.session_state.archivio_file), use_container_width=True
    )
  else:
    st.info("Nessun file extra nell'archivio.")


def guide_lavoro_page():
  st.title("📚 Guide Operative Lavoro (Bpoint / Zucchetti)")
  software = st.selectbox(
      "Seleziona Software", ["Bpoint", "Zucchetti Paghe", "AdE"]
  )
  st.text_area(
      f"Note e procedure per {software}:",
      placeholder="Inserisci qui i tuoi promemoria...",
      height=300,
  )


def personalizzazione_page():
  st.title("🎨 Centro Personalizzazione & Layout")
  st.markdown(
      "Modifica l'estetica, la forma dei riquadri e gestisci la visibilità delle"
      " sezioni direttamente dal sito."
  )
  st.markdown("---")

  col_p1, col_p2 = st.columns(2)

  with col_p1:
    st.subheader("🎨 Estetica & Stile")
    st.session_state.tema_colore = st.selectbox(
        "Colore Principale Accento",
        [
            "Indigo Professionale (#4f46e5)",
            "Verde Finanza (#059669)",
            "Blu Elettrico (#2563eb)",
            "Arancio Caldo (#ea580c)",
            "Scuro Elegante (#334155)",
        ],
        index=[
            "Indigo Professionale (#4f46e5)",
            "Verde Finanza (#059669)",
            "Blu Elettrico (#2563eb)",
            "Arancio Caldo (#ea580c)",
            "Scuro Elegante (#334155)",
        ].index(st.session_state.tema_colore),
    )

    st.session_state.bordo_riquadri = st.slider(
        "Arrotondamento Riquadri / Card (Pixel)",
        min_value=0,
        max_value=30,
        value=st.session_state.bordo_riquadri,
    )

    st.session_state.ombra_box = st.checkbox(
        "Attiva Effetto Ombra sui Riquadri", value=st.session_state.ombra_box
    )

  with col_p2:
    st.subheader("📑 Gestione Sezioni (Mostra / Nascondi)")
    st.session_state.mostra_home = st.checkbox(
        "🏠 Mostra Home & Bilancio", value=st.session_state.mostra_home
    )
    st.session_state.mostra_analisi = st.checkbox(
        "💰 Mostra Analisi & Filtri Spese",
        value=st.session_state.mostra_analisi,
    )
    st.session_state.mostra_archivio = st.checkbox(
        "📁 Mostra Archivio File", value=st.session_state.mostra_archivio
    )
    st.session_state.mostra_guide = st.checkbox(
        "📚 Mostra Guide Lavoro", value=st.session_state.mostra_guide
    )

  st.markdown("---")
  if st.button("💾 Applica e Salva Modifiche"):
    st.success("✅ Modifiche estetiche applicate con successo!")
    st.rerun()


# --- COSTRUZIONE DINAMICA DEL MENU DI NAVIGAZIONE ---
pagine_attive = {}

if st.session_state.mostra_home:
  pagine_attive["Panoramica & KPI"] = [
      st.Page(home_page, title="🏠 Home & Bilancio", default=True)
  ]

finanza_sub = []
if st.session_state.mostra_analisi:
  finanza_sub.append(
      st.Page(analisi_avanzata_page, title="💰 Analisi & Filtri Spese")
  )
if finanza_sub:
  pagine_attive["Gestione Finanziaria"] = finanza_sub

lavoro_sub = []
if st.session_state.mostra_archivio:
  lavoro_sub.append(st.Page(archivio_file_page, title="📁 Archivio File"))
if st.session_state.mostra_guide:
  lavoro_sub.append(st.Page(guide_lavoro_page, title="📚 Guide Lavoro"))
if lavoro_sub:
  pagine_attive["Archivio & Lavoro"] = lavoro_sub

# La pagina di personalizzazione è sempre accessibile per modificare il layout
pagine_attive["Impostazioni"] = [
    st.Page(personalizzazione_page, title="🎨 Personalizza Layout")
]

# Esecuzione della navigazione dinamica
if pagine_attive:
  pg = st.navigation(pagine_attive)
  pg.run()
else:
  st.warning(
      "⚠️ Hai disattivato tutte le sezioni dal pannello di personalizzazione."
      " Vai su 'Impostazioni' per riattivarne almeno una."
  )
  st.Page(personalizzazione_page, title="🎨 Personalizza Layout").run()
