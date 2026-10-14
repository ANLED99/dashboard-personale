from datetime import datetime
import os
import pandas as pd
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Google Command Center", page_icon="🌐", layout="wide"
)

# --- CREAZIONE CARTELLA DATI PER STORICIZZAZIONE ---
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
  os.makedirs(DATA_DIR)

# --- STILE GRAFICO GOOGLE STYLE ---
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


# --- FUNZIONE DI UPLOAD E SALVATAGGIO FISICO PERMANENTE ---
def gestisci_upload_persistente(nome_file_salvataggio):
  """Salva fisicamente il file caricato nella cartella data/ per mantenerlo storicizzato."""
  file_path = os.path.join(DATA_DIR, nome_file_salvataggio)

  uploaded_file = st.file_uploader(
      f"📁 Carica o aggiorna file ({nome_file_salvataggio}):",
      type=["csv", "xlsx", "json"],
      key=f"up_{nome_file_salvataggio}",
  )

  if uploaded_file is not None:
    try:
      with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
      st.success(
          f"File '{nome_file_salvataggio}' caricato e salvato in modo permanente!"
      )
    except Exception as e:
      st.error(f"Errore nel salvataggio: {e}")

  # Legge il file se esiste fisicamente
  if os.path.exists(file_path):
    if file_path.endswith(".csv"):
      return pd.read_csv(file_path)
    elif file_path.endswith((".xls", ".xlsx")):
      return pd.read_excel(file_path)
    elif file_path.endswith(".json"):
      return pd.read_json(file_path)

  return None


# --- CARICAMENTO DATI PERSISTENTI ---
df_finanze = gestisci_upload_persistente("movimenti_finanziari.csv")
if df_finanze is None:
  try:
    df_finanze = pd.read_csv("movimenti_estratti_conto_2026.csv")
  except Exception:
    df_finanze = pd.DataFrame(
        columns=["Data", "Descrizione", "Importo (€)", "Categoria"]
    )

df_partite = gestisci_upload_persistente("partite_calcio.csv")
if df_partite is None:
  df_partite = pd.DataFrame(
      columns=["Data", "Avversario", "Competizione", "Risultato", "Gol Fatti", "Voto", "Nota"]
  )

df_spotify = gestisci_upload_persistente("spotify_ascolti.csv")
if df_spotify is None:
  df_spotify = pd.DataFrame(
      columns=["Data", "Genere Principale", "Brani Ascoltati", "Artista Top", "Nota"]
  )


# --- FUNZIONI DELLE SEZIONI ---
def home_page():
  st.title("🌐 Google Command Center")
  st.markdown("Panoramica centrale con dati storicizzati in tempo reale.")
  st.markdown("---")

  tot_spese = (
      df_finanze[df_finanze["Importo (€)"] < 0]["Importo (€)"].sum()
      if not df_finanze.empty
      else 0.0
  )
  num_part = len(df_partite) if not df_partite.empty else 0

  c1, c2, c3 = st.columns(3)
  with c1:
    st.metric(label="💰 Spese Totali", value=f"€ {tot_spese:,.2f}")
  with c2:
    st.metric(label="⚽ Partite Registrate", value=f"{num_part}")
  with c3:
    st.metric(label="📁 Stato Archiviazione", value="Permanente (Attiva)")


def finanze_page():
  st.title("💰 Finanze & Estratti Conto")
  st.markdown(
      "I dati caricati qui vengono salvati permanentemente nella cartella di"
      " sistema."
  )

  # Mostra tool upload persistente per le finanze
  f_up = st.file_uploader(
      "Carica nuovo estratto conto (CSV)", type=["csv"], key="fin_up_new"
  )
  if f_up is not None:
    df_new = pd.read_csv(f_up)
    df_finanze_agg = pd.concat([df_finanze, df_new], ignore_index=True)
    df_finanze_agg.to_csv(
        os.path.join(DATA_DIR, "movimenti_finanziari.csv"), index=False
    )
    st.success("Movimenti aggiornati e salvati con successo!")
    st.rerun()

  if not df_finanze.empty:
    st.dataframe(df_finanze, use_container_width=True)
  else:
    st.warning("Nessun movimento finanziario presente.")


def sport_page():
  st.title("⚽ Sport & Calcio (con Note Vocali/Testuali)")

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

    # Campo Nota testuale (può essere dettata a voce usando il microfono integrato della tastiera del telefono/PC)
    nota = st.text_area(
        "Note sulla partita (puoi usare il dettato vocale della tastiera):",
        placeholder="Tocca il microfono della tastiera per dettare la nota...",
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
      global df_partite
      df_partite = pd.concat([df_partite, p_new], ignore_index=True)
      df_partite.to_csv(
          os.path.join(DATA_DIR, "partite_calcio.csv"), index=False
      )
      st.success("Partita salvata in modo permanente!")
      st.rerun()

  if not df_partite.empty:
    st.dataframe(df_partite, use_container_width=True)


def spotify_page():
  st.title("🎧 Spotify & Ascolti Musicali")
  with st.form("f_spot"):
    c1, c2 = st.columns(2)
    with c1:
      ds = st.date_input("Data", datetime.today())
      gen = st.text_input("Genere Principale")
    with c2:
      brani = st.number_input("Brani Ascoltati", 50)
      art = st.text_input("Artista Top")

    nota_spot = st.text_area("Note sugli ascolti (o dettatura vocale):")

    if st.form_submit_button("Registra Ascolti"):
      s_new = pd.DataFrame([{
          "Data": str(ds),
          "Genere Principale": gen,
          "Brani Ascoltati": brani,
          "Artista Top": art,
          "Nota": nota_spot,
      }])
      global df_spotify
      df_spotify = pd.concat([df_spotify, s_new], ignore_index=True)
      df_spotify.to_csv(
          os.path.join(DATA_DIR, "spotify_ascolti.csv"), index=False
      )
      st.success("Dati Spotify salvati!")
      st.rerun()

  if not df_spotify.empty:
    st.dataframe(df_spotify, use_container_width=True)


# --- NAVIGAZIONE ST.NAVIGATION ---
pg = st.navigation({
    "Panoramica": [st.Page(home_page, title="🏠 Home", default=True)],
    "Finanza": [st.Page(finanze_page, title="💰 Finanze & Estratti Conto")],
    "Sport & Musica": [
        st.Page(sport_page, title="⚽ Calcio & Match"),
        st.Page(spotify_page, title="🎧 Spotify & Musica"),
    ],
})

pg.run()
