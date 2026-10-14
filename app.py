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


# --- UTILITY DI UPLOAD E STORICIZZAZIONE PERMANENTE ---
def gestisci_upload_persistente(nome_file_salvataggio, colonne_default):
  file_path = os.path.join(DATA_DIR, nome_file_salvataggio)

  uploaded_file = st.file_uploader(
      f"📁 Carica/Aggiorna ({nome_file_salvataggio}):",
      type=["csv", "xlsx", "json"],
      key=f"up_{nome_file_salvataggio}",
  )

  if uploaded_file is not None:
    try:
      if uploaded_file.name.endswith(".csv"):
        df_new = pd.read_csv(uploaded_file)
      elif uploaded_file.name.endswith((".xls", ".xlsx")):
        df_new = pd.read_excel(uploaded_file)
      else:
        df_new = pd.read_json(uploaded_file)

      df_new.to_csv(file_path, index=False)
      st.success(
          f"File '{nome_file_salvataggio}' aggiornato e salvato permanentemente!"
      )
      return df_new
    except Exception as e:
      st.error(f"Errore caricamento: {e}")

  if os.path.exists(file_path):
    try:
      return pd.read_csv(file_path)
    except Exception:
      pass

  return pd.DataFrame(columns=colonne_default)


# --- CARICAMENTO DATI PERSISTENTI ---
df_finanze = gestisci_upload_persistente(
    "movimenti_finanziari.csv", ["Data", "Descrizione", "Importo (€)", "Categoria"]
)
if df_finanze.empty:
  try:
    df_finanze = pd.read_csv("movimenti_estratti_conto_2026.csv")
  except Exception:
    pass

df_abbonamenti = gestisci_upload_persistente(
    "abbonamenti.csv", ["Servizio", "Costo (€)", "Frequenza", "Scadenza"]
)
df_partite = gestisci_upload_persistente(
    "partite_calcio.csv",
    ["Data", "Avversario", "Competizione", "Risultato", "Gol Fatti", "Voto", "Nota"],
)
df_allenamenti = gestisci_upload_persistente(
    "allenamenti_calcio.csv", ["Data", "Tipo", "Durata (min)", "Note"]
)
df_spotify = gestisci_upload_persistente(
    "spotify_ascolti.csv",
    ["Data", "Genere Principale", "Brani Ascoltati", "Artista Top", "Nota"],
)
df_libri = gestisci_upload_persistente(
    "libri_corsi.csv", ["Titolo", "Tipologia", "Stato", "Voto / Valutazione"]
)
df_link = gestisci_upload_persistente(
    "link_utili.csv", ["Nome Portale", "URL", "Note / Credenziali"]
)


# Inizializzazioni in memoria per task e note se non presenti
if "todo_list" not in st.session_state:
  st.session_state.todo_list = [
      {"Attività": "Aggiornare estratti conto", "Completata": False},
      {"Attività": "Preparare report Bpoint", "Completata": True},
  ]

if "archivio_file" not in st.session_state:
  st.session_state.archivio_file = []

if "note_personali" not in st.session_state:
  st.session_state.note_personali = "Note rapide del workspace..."


# --- FUNZIONI DELLE SEZIONI ---
def home_page():
  st.title("🌐 Google Command Center")
  st.markdown(
      "Il tuo hub centrale con tutti i dati storicizzati in modo permanente."
  )
  st.markdown("---")

  tot_spese = (
      df_finanze[df_finanze["Importo (€)"] < 0]["Importo (€)"].sum()
      if not df_finanze.empty
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
      "💡 Tutte le modifiche e i file caricati rimangono salvati nella cartella"
      " di sistema."
  )


def finanze_page():
  st.title("💰 Finanze & Abbonamenti")
  tab1, tab2 = st.tabs(["📊 Conto Corrente", "🔄 Costi Fissi & Abbonamenti"])

  with tab1:
    st.subheader("Movimenti Conto Corrente")
    if not df_finanze.empty:
      st.dataframe(df_finanze, use_container_width=True)
      df_uscite = df_finanze[df_finanze["Importo (€)"] < 0].copy()
      df_uscite["Assoluto"] = df_uscite["Importo (€)"].abs()
      st.bar_chart(df_uscite.groupby("Categoria")["Assoluto"].sum())
    else:
      st.warning("Nessun movimento finanziario presente.")

  with tab2:
    st.subheader("Abbonamenti Attivi")
    with st.form("form_abbonamenti"):
      c1, c2, c3 = st.columns(3)
      with c1:
        servizio = st.text_input("Nome Servizio")
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
        global df_abbonamenti
        df_abbonamenti = pd.concat(
            [df_abbonamenti, nuovo_abb], ignore_index=True
        )
        df_abbonamenti.to_csv(
            os.path.join(DATA_DIR, "abbonamenti.csv"), index=False
        )
        st.success("Abbonamento salvato!")
        st.rerun()

    if not df_abbonamenti.empty:
      st.dataframe(df_abbonamenti, use_container_width=True)


def sport_page():
  st.title("⚽ Sport & Calcio (Tuttocampo Style)")
  tab1, tab2 = st.tabs(["📋 Partite", "🏃‍♂️ Allenamenti"])

  with tab1:
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
          "Nota / Dettatura Vocale:",
          placeholder="Usa il microfono della tastiera per dettare...",
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
        st.success("Partita salvata permanentemente!")
        st.rerun()

    if not df_partite.empty:
      st.dataframe(df_partite, use_container_width=True)

  with tab2:
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
            "Note": nota_all,
        }])
        global df_allenamenti
        df_allenamenti = pd.concat([df_allenamenti, a_new], ignore_index=True)
        df_allenamenti.to_csv(
            os.path.join(DATA_DIR, "allenamenti_calcio.csv"), index=False
        )
        st.success("Allenamento salvato!")
        st.rerun()

    if not df_allenamenti.empty:
      st.dataframe(df_allenamenti, use_container_width=True)


def spotify_page():
  st.title("🎧 Spotify & Monitoraggio Ascolti")
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
      global df_spotify
      df_spotify = pd.concat([df_spotify, s_new], ignore_index=True)
      df_spotify.to_csv(
          os.path.join(DATA_DIR, "spotify_ascolti.csv"), index=False
      )
      st.success("Dati Spotify salvati!")
      st.rerun()

  if not df_spotify.empty:
    st.dataframe(df_spotify, use_container_width=True)
    st.bar_chart(
        df_spotify.groupby("Genere Principale")["Brani Ascoltati"].sum()
    )


def lavoro_page():
  st.title("⚡ Lavoro & Workspace")
  tab1, tab2 = st.tabs(["📚 Guide Software", "📝 Note Operative"])

  with tab1:
    soft = st.selectbox("Software", ["Bpoint", "Zucchetti Paghe", "AdE"])
    st.text_area(f"Procedure per {soft}:", height=200)

  with tab2:
    st.session_state.note_personali = st.text_area(
        "Blocco note libero (supporta dettatura):",
        value=st.session_state.note_personali,
        height=250,
    )


def task_page():
  st.title("✅ Attività & To-Do List")
  nuovo = st.text_input("Nuova attività:")
  if st.button("Aggiungi Task"):
    if nuovo:
      st.session_state.todo_list.append(
          {"Attività": nuovo, "Completata": False}
      )
      st.rerun()

  for idx, task in enumerate(st.session_state.todo_list):
    comp = st.checkbox(
        task["Attività"], value=task["Completata"], key=f"t_{idx}"
    )
    st.session_state.todo_list[idx]["Completata"] = comp


def cultura_page():
  st.title("📚 Cultura, Libri & Crescita")
  with st.form("f_cultura"):
    tit = st.text_input("Titolo Libro / Corso")
    tip = st.selectbox("Tipologia", ["Libro", "Corso Online", "Podcast"])
    stato = st.selectbox("Stato", ["Da Iniziare", "In Corso", "Completato"])
    voto = st.slider("Valutazione", 1, 10, 8)

    if st.form_submit_button("Aggiungi Elemento"):
      c_new = pd.DataFrame([{
          "Titolo": tit,
          "Tipologia": tip,
          "Stato": stato,
          "Voto / Valutazione": voto,
      }])
      global df_libri
      df_libri = pd.concat([df_libri, c_new], ignore_index=True)
      df_libri.to_csv(os.path.join(DATA_DIR, "libri_corsi.csv"), index=False)
      st.success("Aggiunto!")
      st.rerun()

  if not df_libri.empty:
    st.dataframe(df_libri, use_container_width=True)


def link_page():
  st.title("🔑 Link Vault & Portali Rapidi")
  with st.form("f_link"):
    nome = st.text_input("Nome Portale")
    url = st.text_input("URL / Link web")
    note = st.text_input("Note o credenziali")
    if st.form_submit_button("Salva Link"):
      l_new = pd.DataFrame(
          [{"Nome Portale": nome, "URL": url, "Note / Credenziali": note}]
      )
      global df_link
      df_link = pd.concat([df_link, l_new], ignore_index=True)
      df_link.to_csv(os.path.join(DATA_DIR, "link_utili.csv"), index=False)
      st.success("Link salvato!")
      st.rerun()

  if not df_link.empty:
    st.dataframe(df_link, use_container_width=True)


def archivio_page():
  st.title("📁 Archivio Documenti")
  f_up = st.file_uploader(
      "Carica file nell'archivio", accept_multiple_files=True
  )
  if f_up:
    for f in f_up:
      st.session_state.archivio_file.append(
          {"Nome File": f.name, "Dimensione": f"{f.size / 1024:.1f} KB"}
      )
    st.success("File caricati!")
  if st.session_state.archivio_file:
    st.dataframe(
        pd.DataFrame(st.session_state.archivio_file), use_container_width=True
    )
  else:
    st.info("Archivio vuoto.")


# --- NAVIGAZIONE ST.NAVIGATION ---
pg = st.navigation({
    "Panoramica": [st.Page(home_page, title="🏠 Home", default=True)],
    "Finanza & Patrimonio": [
        st.Page(finanze_page, title="💰 Finanze & Abbonamenti")
    ],
    "Sport & Passioni": [
        st.Page(sport_page, title="⚽ Calcio & Match"),
        st.Page(spotify_page, title="🎧 Spotify & Musica"),
    ],
    "Lavoro & Utility": [
        st.Page(lavoro_page, title="⚡ Lavoro & Workspace"),
        st.Page(task_page, title="✅ Attività & To-Do"),
        st.Page(cultura_page, title="📚 Cultura & Libri"),
        st.Page(link_page, title="🔑 Link & Portali"),
        st.Page(archivio_page, title="📁 Archivio File"),
    ],
})

pg.run()
