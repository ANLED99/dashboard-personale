
from datetime import datetime
import os
import pandas as pd
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Google Command Center", page_icon="🌐", layout="wide"
)

# --- CONFIGURAZIONE CREDENZIALI SPOTIFY API ---
SPOTIFY_CLIENT_ID = "446a7c20e4b04072a4330fdf2f6d225a"
SPOTIFY_CLIENT_SECRET = "cba7af42c2874795ab343920a5e7d8d1"
SPOTIFY_REDIRECT_URI = "http://localhost:8501"

# --- STILE GRAFICO GOOGLE MATERIAL DESIGN & FORZATURA TEMA CHIARO ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f8f9fa !important;
        color: #202124 !important;
    }
    .main { 
        background-color: #f8f9fa !important; 
        font-family: 'Roboto', sans-serif; 
    }
    h1, h2, h3, h4, h5, h6, p, span, label { 
        color: #202124 !important; 
    }
    .stMetric {
        background-color: #ffffff !important;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(60,64,67,0.3);
        border: 1px solid #dadce0;
        border-left: 6px solid #1a73e8;
    }
    .stMetric label {
        color: #5f6368 !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #202124 !important;
    }
    .stButton>button {
        border-radius: 8px;
        background-color: #1a73e8;
        color: white !important;
        font-weight: 500;
        border: none;
        padding: 8px 16px;
    }
    .stButton>button:hover {
        background-color: #1557b0;
        color: white !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- CREAZIONE CARTELLA DATI PER LA PERSISTENZA ---
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
  os.makedirs(DATA_DIR)


# --- FUNZIONE DI CARICAMENTO E SALVATAGGIO DATI ISOLATI ---
def carica_dati_modulo(nome_file, colonne_default):
  file_path = os.path.join(DATA_DIR, nome_file)
  if os.path.exists(file_path):
    try:
      return pd.read_csv(file_path)
    except Exception:
      pass

  if nome_file == "finanze.csv":
    try:
      df_init = pd.read_csv("movimenti_estratti_conto_2026.csv")
      df_init.to_csv(file_path, index=False)
      return df_init
    except Exception:
      pass

  return pd.DataFrame(columns=colonne_default)


def salva_dati_modulo(nome_file, df):
  file_path = os.path.join(DATA_DIR, nome_file)
  df.to_csv(file_path, index=False)


# --- CARICAMENTO DATASET ---
df_finanze = carica_dati_modulo(
    "finanze.csv", ["Data", "Descrizione", "Importo (€)", "Categoria"]
)
df_abbonamenti = carica_dati_modulo(
    "abbonamenti.csv", ["Servizio", "Costo (€)", "Frequenza", "Scadenza"]
)
df_partite = carica_dati_modulo(
    "partite.csv",
    ["Data", "Avversario", "Competizione", "Risultato", "Gol Fatti", "Voto", "Nota"],
)
df_allenamenti = carica_dati_modulo(
    "allenamenti.csv", ["Data", "Tipo", "Durata (min)", "Nota"]
)
df_spotify = carica_dati_modulo(
    "spotify.csv",
    ["Data", "Genere Principale", "Brani Ascoltati", "Artista Top", "Nota"],
)
df_libri = carica_dati_modulo(
    "libri.csv", ["Titolo", "Tipologia", "Stato", "Voto"]
)
df_link = carica_dati_modulo("link.csv", ["Nome Portale", "URL", "Note"])

if "todo_list" not in st.session_state:
  st.session_state.todo_list = [
      {"Attività": "Aggiornare estratti conto", "Completata": False},
      {"Attività": "Preparare report Bpoint", "Completata": True},
  ]

if "note_lavoro" not in st.session_state:
  st.session_state.note_lavoro = "Appunti e note operative di lavoro..."


# --- DEFINIZIONE DELLE PAGINE DEL COMMAND CENTER ---
def home_page():
  st.title("🌐 Google Command Center")
  st.markdown("Panoramica generale e stato di salute di tutti i tuoi moduli.")
  st.markdown("---")

  tot_spese = (
      df_finanze[df_finanze["Importo (€)"] < 0]["Importo (€)"].sum()
      if not df_finanze.empty and "Importo (€)" in df_finanze.columns
      else 0.0
  )
  num_part = len(df_partite) if not df_partite.empty else 0
  num_tasks = sum(1 for t in st.session_state.todo_list if not t["Completata"])
  num_libri = len(df_libri) if not df_libri.empty else 0

  c1, c2, c3, c4 = st.columns(4)
  with c1:
    st.metric(label="💰 Spese Totali", value=f"€ {tot_spese:,.2f}")
  with c2:
    st.metric(label="⚽ Partite Registrate", value=f"{num_part}")
  with c3:
    st.metric(label="📌 Task Pendenti", value=f"{num_tasks}")
  with c4:
    st.metric(label="📚 Elementi Libreria", value=f"{num_libri}")

  st.markdown("---")
  st.info("💡 Sistema attivo e operativo.")


def calendario_page():
  st.title("📅 Calendario & Attività Unificate")
  st.markdown(
      "Visualizza lo storico e la programmazione unita di partite, abbonamenti,"
      " transazioni e impegni."
  )
  st.markdown("---")

  with st.expander("🔗 Sincronizzazione Google Calendar"):
    gcal_url = st.text_input(
        "URL Iframe Google Calendar:",
        placeholder=(
            "https://calendar.google.com/calendar/embed?src=tuo_id_calendario..."
        ),
    )
    if gcal_url:
      st.components.v1.iframe(gcal_url, height=500, scrolling=True)

  st.subheader("📋 Feed Unificato Attività (Tutte le Cartelle)")

  eventi_totali = []

  if not df_partite.empty and "Data" in df_partite.columns:
    for _, row in df_partite.iterrows():
      eventi_totali.append({
          "Data": str(row.get("Data", "")),
          "Categoria": "⚽ Partita",
          "Dettaglio": (
              f"vs {row.get('Avversario', 'N/D')} ({row.get('Competizione', '')})"
          ),
          "Note / Risultato": (
              f"Risultato: {row.get('Risultato', '')} - Voto:"
              f" {row.get('Voto', '')}"
          ),
      })

  if not df_allenamenti.empty and "Data" in df_allenamenti.columns:
    for _, row in df_allenamenti.iterrows():
      eventi_totali.append({
          "Data": str(row.get("Data", "")),
          "Categoria": "🏃 Allenamento",
          "Dettaglio": f"Tipo: {row.get('Tipo', '')}",
          "Note / Risultato": row.get("Nota", ""),
      })

  if not df_finanze.empty and "Data" in df_finanze.columns:
    for _, row in df_finanze.iterrows():
      eventi_totali.append({
          "Data": str(row.get("Data", "")),
          "Categoria": "💰 Finanza",
          "Dettaglio": str(row.get("Descrizione", "")),
          "Note / Risultato": f"Importo: € {row.get('Importo (€)', 0)}",
      })

  if eventi_totali:
    df_eventi = pd.DataFrame(eventi_totali)
    df_eventi = df_eventi.sort_values(by="Data", ascending=False)
    cat_scelta = st.selectbox(
        "Filtra per categoria eventi:",
        ["Tutti"] + df_eventi["Categoria"].unique().tolist(),
    )
    if cat_scelta != "Tutti":
      df_eventi = df_eventi[df_eventi["Categoria"] == cat_scelta]
    st.dataframe(df_eventi, use_container_width=True)
  else:
    st.info("Nessun evento registrato nelle cartelle.")


def centro_upload_page():
  st.title("📁 Centro Upload & Importazione Universale")
  st.markdown(
      "Carica un file e seleziona a quale categoria di destinazione associarlo."
  )
  st.markdown("---")

  mappa_destinazioni = {
      "Finanze / Estratto Conto (finanze.csv)": ("finanze.csv", ["Data", "Descrizione", "Importo (€)", "Categoria"]),
      "Abbonamenti & Costi Fissi (abbonamenti.csv)": ("abbonamenti.csv", ["Servizio", "Costo (€)", "Frequenza", "Scadenza"]),
      "Partite di Calcio (partite.csv)": ("partite.csv", ["Data", "Avversario", "Competizione", "Risultato", "Gol Fatti", "Voto", "Nota"]),
      "Allenamenti (allenamenti.csv)": ("allenamenti.csv", ["Data", "Tipo", "Durata (min)", "Nota"]),
      "Spotify & Ascolti (spotify.csv)": ("spotify.csv", ["Data", "Genere Principale", "Brani Ascoltati", "Artista Top", "Nota"]),
      "Cultura & Libri (libri.csv)": ("libri.csv", ["Titolo", "Tipologia", "Stato", "Voto"]),
      "Link & Portali (link.csv)": ("link.csv", ["Nome Portale", "URL", "Note"]),
  }

  scelta_categoria = st.selectbox(
      "Seleziona la categoria di destinazione del file:",
      list(mappa_destinazioni.keys()),
  )

  file_caricato = st.file_uploader(
      "Seleziona il file da importare (CSV o Excel):", type=["csv", "xlsx", "xls"]
  )

  if file_caricato is not None:
    if st.button("Conferma e Importa nei Dati"):
      nome_file_target, colonne_def = mappa_destinazioni[scelta_categoria]
      try:
        if file_caricato.name.endswith(".csv"):
          df_nuovo = pd.read_csv(file_caricato)
        else:
          df_nuovo = pd.read_excel(file_caricato)

        df_esistente = carica_dati_modulo(nome_file_target, colonne_def)
        df_finale = pd.concat([df_esistente, df_nuovo], ignore_index=True)
        salva_dati_modulo(nome_file_target, df_finale)

        st.success(
            f"File importato con successo nella sezione '{scelta_categoria}'!"
        )
        st.rerun()
      except Exception as e:
        st.error(f"Errore durante l'elaborazione del file: {e}")


def finanze_page():
  st.title("💰 Finanze & Abbonamenti")
  tab1, tab2 = st.tabs(["📊 Conto Corrente", "🔄 Costi Fissi & Abbonamenti"])

  global df_finanze, df_abbonamenti

  with tab1:
    st.subheader("Movimenti Conto Corrente (Modificabili / Eliminabili)")
    if not df_finanze.empty:
      df_finanze_modificato = st.data_editor(
          df_finanze, num_rows="dynamic", use_container_width=True, key="edit_fin"
      )
      if st.button("💾 Salva Modifiche Conto"):
        salva_dati_modulo("finanze.csv", df_finanze_modificato)
        st.success("Modifiche salvate con successo!")
        st.rerun()

      if "Importo (€)" in df_finanze.columns and "Categoria" in df_finanze.columns:
        df_uscite = df_finanze[df_finanze["Importo (€)"] < 0].copy()
        df_uscite["Assoluto"] = df_uscite["Importo (€)"].abs()
        st.bar_chart(df_uscite.groupby("Categoria")["Assoluto"].sum())
    else:
      st.warning("Nessun movimento registrato. Usa il Centro Upload.")

  with tab2:
    st.subheader("Gestione Abbonamenti")
    with st.form("form_abbonamenti"):
      c1, c2, c3 = st.columns(3)
      with c1:
        servizio = st.text_input("Nome Servizio (es. Netflix)")
      with c2:
        costo = st.number_input("Costo (€)", value=9.99)
      with c3:
        freq = st.selectbox("Frequenza", ["Mensile", "Annuale"])
        scad = st.text_input("Scadenza")

      if st.form_submit_button("Aggiungi Abbonamento"):
        nuovo_abb = pd.DataFrame([{
            "Servizio": servizio,
            "Costo (€)": costo,
            "Frequenza": freq,
            "Scadenza": scad,
        }])
        df_abbonamenti = pd.concat([df_abbonamenti, nuovo_abb], ignore_index=True)
        salva_dati_modulo("abbonamenti.csv", df_abbonamenti)
        st.success("Abbonamento aggiunto!")
        st.rerun()

    if not df_abbonamenti.empty:
      df_abb_mod = st.data_editor(
          df_abbonamenti, num_rows="dynamic", use_container_width=True, key="edit_abb"
      )
      if st.button("💾 Salva Modifiche Abbonamenti"):
        salva_dati_modulo("abbonamenti.csv", df_abb_mod)
        st.success("Abbonamenti aggiornati!")
        st.rerun()


def sport_page():
  st.title("⚽ Sport & Calcio (Tuttocampo Style)")
  tab1, tab2 = st.tabs(["📋 Partite", "🏃‍♂️ Allenamenti"])

  global df_partite, df_allenamenti

  with tab1:
    st.subheader("Registro Partite")
    with st.form("f_partita"):
      c1, c2, c3 = st.columns(3)
      with c1:
        dp = st.date_input("Data", datetime.today())
        avv = st.text_input("Avversario")
      with c2:
        comp = st.text_input("Competizione")
        ris = st.text_input("Risultato")
      with c3:
        gol = st.number_input("Gol Fatti", 0)
        voto = st.slider("Voto", 1.0, 10.0, 6.5)

      nota = st.text_area(
          "Nota / Commento (supporta dettatura vocale da tastiera):",
