from datetime import datetime
import os
import pandas as pd
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Google Command Center", page_icon="🌐", layout="wide"
)

# --- CREAZIONE CARTELLA DATI PER LA PERSISTENZA ---
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
  os.makedirs(DATA_DIR)

# --- STILE GRAFICO GOOGLE MATERIAL DESIGN ---
st.markdown(
    """
    <style>
    .main { background-color: #f8f9fa; font-family: 'Roboto', sans-serif; }
    h1, h2, h3 { color: #202124; font-weight: 500; }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(60,64,67,0.3);
        border: 1px solid #dadce0;
        border-left: 6px solid #1a73e8;
    }
    .stButton>button {
        border-radius: 8px;
        background-color: #1a73e8;
        color: white;
        font-weight: 500;
        border: none;
        padding: 8px 16px;
    }
    .stButton>button:hover {
        background-color: #1557b0;
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- FUNZIONE DI CARICAMENTO E SALVATAGGIO DATI ISOLATI ---
def carica_dati_modulo(nome_file, colonne_default):
  file_path = os.path.join(DATA_DIR, nome_file)
  if os.path.exists(file_path):
    try:
      return pd.read_csv(file_path)
    except Exception:
      pass

  # Fallback iniziale per le finanze
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

# Session state per To-Do List e Note
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
  st.info(
      "💡 Usa la sezione **Centro Upload** nel menu per caricare file o le altre"
      " sezioni per visualizzare, modificare ed eliminare i dati."
  )


def centro_upload_page():
  st.title("📁 Centro Upload & Importazione Universale")
  st.markdown(
      "Carica un file e seleziona a quale categoria di destinazione associarlo."
  )
  st.markdown("---")

  # Mappa delle destinazioni con i rispettivi file di salvataggio
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

        # Legge il file esistente, unisce o sostituisce, e salva
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
      # Tabella interattiva per modificare o eliminare righe al volo
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
          placeholder="Ticca il microfono per dettare...",
      )

      if st.form_submit_button("Registra Partita"):
        p_new = pd.DataFrame([{
            "Data": str(dp),
            "Avversario": avv,
            "Competizione": comp,
            "Risultato": ris,
            "Gol Fatti": gol,
            "Voto": voto,
            "Nota": nota,
        }])
        df_partite = pd.concat([df_partite, p_new], ignore_index=True)
        salva_dati_modulo("partite.csv", df_partite)
        st.success("Partita salvata!")
        st.rerun()

    if not df_partite.empty:
      st.subheader("Elenco Partite (Modificabili o Eliminabili)")
      df_part_mod = st.data_editor(
          df_partite, num_rows="dynamic", use_container_width=True, key="edit_part"
      )
      if st.button("💾 Salva Modifiche Partite"):
        salva_dati_modulo("partite.csv", df_part_mod)
        st.success("Partite aggiornate!")
        st.rerun()

  with tab2:
    st.subheader("Registro Allenamenti")
    with st.form("f_all"):
      da = st.date_input("Data Allenamento", datetime.today())
      ta = st.selectbox(
          "Tipo", ["Seduta Atletica", "Tattica", "Rifinitura", "Palestra"]
      )
      dur = st.number_input("Durata (min)", 90)
      nota_all = st.text_area("Note allenamento:")
      if st.form_submit_button("Aggiungi Allenamento"):
        a_new = pd.DataFrame([{
            "Data": str(da),
            "Tipo": ta,
            "Durata (min)": dur,
            "Nota": nota_all,
        }])
        df_allenamenti = pd.concat([df_allenamenti, a_new], ignore_index=True)
        salva_dati_modulo("allenamenti.csv", df_allenamenti)
        st.success("Allenamento salvato!")
        st.rerun()

    if not df_allenamenti.empty:
      df_all_mod = st.data_editor(
          df_allenamenti, num_rows="dynamic", use_container_width=True, key="edit_all"
      )
      if st.button("💾 Salva Modifiche Allenamenti"):
        salva_dati_modulo("allenamenti.csv", df_all_mod)
        st.success("Allenamenti aggiornati!")
        st.rerun()


def spotify_page():
  st.title("🎧 Spotify & Monitoraggio Ascolti")
  global df_spotify

  with st.form("f_spot"):
    c1, c2 = st.columns(2)
    with c1:
      ds = st.date_input("Data", datetime.today())
      gen = st.text_input("Genere Principale")
    with c2:
      brani = st.number_input("Brani Ascoltati", 50)
      art = st.text_input("Artista Top")

    nota_spot = st.text_area("Note ascolti (o dettatura vocale):")

    if st.form_submit_button("Registra Ascolti"):
      s_new = pd.DataFrame([{
          "Data": str(ds),
          "Genere Principale": gen,
          "Brani Ascoltati": brani,
          "Artista Top": art,
          "Nota": nota_spot,
      }])
      df_spotify = pd.concat([df_spotify, s_new], ignore_index=True)
      salva_dati_modulo("spotify.csv", df_spotify)
      st.success("Dati Spotify salvati!")
      st.rer
