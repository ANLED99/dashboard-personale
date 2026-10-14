from datetime import datetime
import pandas as pd
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Google Command Center", page_icon="🌐", layout="wide"
)

# --- STILE GRAFICO PULITO "GOOGLE STYLE" ---
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


# --- UTILITY DI UPLOAD UNIVERSALE ---
def carica_file_universale(chiave_sessione, colonne_standard):
  """Permette di caricare qualsiasi file (csv, xlsx, txt, json) e lo converte in DataFrame unendolo ai dati esistenti."""
  uploaded_file = st.file_uploader(
      "📁 Carica dati da file (CSV, Excel, TXT, JSON):",
      type=["csv", "xlsx", "txt", "json"],
      key=chiave_sessione,
  )
  if uploaded_file is not None:
    try:
      if uploaded_file.name.endswith(".csv"):
        df_new = pd.read_csv(uploaded_file)
      elif uploaded_file.name.endswith((".xls", ".xlsx")):
        df_new = pd.read_excel(uploaded_file)
      elif uploaded_file.name.endswith(".json"):
        df_new = pd.read_json(uploaded_file)
      else:
        df_new = pd.read_csv(uploaded_file, sep=None, engine="python")

      # Unisce o sostituisce
      if not df_new.empty:
        st.success(
            f"File '{uploaded_file.name}' caricato ed elaborato con successo!"
        )
        return df_new
    except Exception as e:
      st.error(f"Errore nella lettura del file: {e}")
  return None


# --- INIZIALIZZAZIONE SESSION STATE ---
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

if "abbonamenti" not in st.session_state:
  st.session_state.abbonamenti = pd.DataFrame(
      columns=["Servizio", "Costo (€)", "Frequenza", "Scadenza"]
  )

if "partite_calcio" not in st.session_state:
  st.session_state.partite_calcio = pd.DataFrame(
      columns=[
          "Data",
          "Avversario",
          "Competizione",
          "Risultato",
          "Gol Fatti",
          "Voto",
      ]
  )

if "allenamenti_calcio" not in st.session_state:
  st.session_state.allenamenti_calcio = pd.DataFrame(
      columns=["Data", "Tipo", "Durata (min)", "Note"]
  )

if "spotify_ascolti" not in st.session_state:
  st.session_state.spotify_ascolti = pd.DataFrame(
      columns=["Data", "Genere Principale", "Brani Ascoltati", "Artista Top"]
  )

if "todo_list" not in st.session_state:
  st.session_state.todo_list = [
      {"Attività": "Aggiornare estratti conto", "Completata": False},
      {"Attività": "Preparare report Bpoint", "Completata": True},
  ]

if "libri_corsi" not in st.session_state:
  st.session_state.libri_corsi = pd.DataFrame(
      columns=["Titolo", "Tipologia", "Stato", "Voto / Valutazione"]
  )

if "link_utili" not in st.session_state:
  st.session_state.link_utili = pd.DataFrame(
      columns=["Nome Portale", "URL", "Note / Credenziali"]
  )

if "archivio_file" not in st.session_state:
  st.session_state.archivio_file = []

if "note_personali" not in st.session_state:
  st.session_state.note_personali = "Note rapide del workspace..."


# --- FUNZIONI DELLE SEZIONI ---
def home_page():
  st.title("🌐 Google Command Center")
  st.markdown(
      "Il tuo hub centrale integrato per la gestione di finanze, sport, lavoro"
      " e passioni."
  )
  st.markdown("---")

  df_fin = st.session_state.dati_finanziari
  tot_spese = (
      df_fin[df_fin["Importo (€)"] < 0]["Importo (€)"].sum()
      if not df_fin.empty
      else 0.0
  )
  num_part = len(st.session_state.partite_calcio)
  num_tasks = sum(1 for t in st.session_state.todo_list if not t["Completata"])
  num_libri = len(st.session_state.libri_corsi)

  c1, c2, c3, c4 = st.columns(4)
  with c1:
    st.metric(label="💰 Spese Totali", value=f"€ {tot_spese:,.2f}")
  with c2:
    st.metric(label="⚽ Partite Registrate", value=f"{num_part}")
  with c3:
    st.metric(label="📌 Task Pendenti", value=f"{num_tasks}")
  with c4:
    st.metric(label="📚 Elementi in Libreria", value=f"{num_libri}")

  st.markdown("---")
  st.info(
      "💡 Usa la barra di navigazione laterale per accedere a tutti i moduli"
      " operativi."
  )


def finanze_page():
  st.title("💰 Finanze & Abbonamenti")
  tab1, tab2 = st.tabs(
      ["📊 Transazioni & Conto Corrente", "🔄 Costi Fissi & Abbonamenti"]
  )

  with tab1:
    st.subheader("Movimenti Conto")
    df_upload = carica_file_universale(
        "up_fin", ["Data", "Descrizione", "Importo (€)", "Categoria"]
    )
    if df_upload is not None:
      st.session_state.dati_finanziari = pd.concat(
          [st.session_state.dati_finanziari, df_upload], ignore_index=True
      )
      st.rerun()

    df = st.session_state.dati_finanziari
    if not df.empty:
      st.dataframe(df, use_container_width=True)
      df_uscite = df[df["Importo (€)"] < 0].copy()
      df_uscite["Assoluto"] = df_uscite["Importo (€)"].abs()
      st.bar_chart(df_uscite.groupby("Categoria")["Assoluto"].sum())
    else:
      st.warning("Nessun dato finanziario disponibile.")

  with tab2:
    st.subheader("Gestione Abbonamenti & Uscite Fisse")
    with st.form("form_abbonamenti"):
      c1, c2, c3 = st.columns(3)
      with c1:
        servizio = st.text_input("Nome Servizio (es. Netflix, Spotify)")
      with c2:
        costo = st.number_input("Costo (€)", value=9.99)
      with c3:
        freq = st.selectbox("Frequenza", ["Mensile", "Annuale"])
        scad = st.text_input("Giorno / Mese Scadenza")

      if st.form_submit_button("Aggiungi Abbonamento"):
        nuovo_abb = pd.DataFrame([{
            "Servizio": servizio,
            "Costo (€)": costo,
            "Frequenza": freq,
            "Scadenza": scad,
        }])
        st.session_state.abbonamenti = pd.concat(
            [st.session_state.abbonamenti, nuovo_abb], ignore_index=True
        )
        st.success("Abbonamento aggiunto!")
        st.rerun()

    if not st.session_state.abbonamenti.empty:
      st.dataframe(st.session_state.abbonamenti, use_container_width=True)


def sport_page():
  st.title("⚽ Sport & Calcio (Tuttocampo Style)")
  tab1, tab2 = st.tabs(["📋 Partite", "🏃‍♂️ Allenamenti"])

  with tab1:
    df_up = carica_file_universale(
        "up_part",
        ["Data", "Avversario", "Competizione", "Risultato", "Gol Fatti", "Voto"],
    )
    if df_up is not None:
      st.session_state.partite_calcio = pd.concat(
          [st.session_state.partite_calcio, df_up], ignore_index=True
      )
      st.rerun()

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

      if st.form_submit_button("Registra Partita"):
        p_new = pd.DataFrame([{
            "Data": str(dp),
            "Avversario": avv,
            "Competizione": comp,
            "Risultato": ris,
            "Gol Fatti": gol,
            "Voto": voto,
        }])
        st.session_state.partite_calcio = pd.concat(
            [st.session_state.partite_calcio, p_new], ignore_index=True
        )
        st.success("Partita salvata!")
        st.rerun()

    if not st.session_state.partite_calcio.empty:
      st.dataframe(st.session_state.partite_calcio, use_container_width=True)

  with tab2:
    with st.form("f_all"):
      da = st.date_input("Data All.", datetime.today())
      ta = st.selectbox(
          "Tipo", ["Seduta Atletica", "Tattica", "Rifinitura", "Palestra"]
      )
      dur = st.number_input("Durata (min)", 90)
      if st.form_submit_button("Aggiungi Allenamento"):
        a_new = pd.DataFrame(
            [{"Data": str(da), "Tipo": ta, "Durata (min)": dur, "Note": ""}]
        )
        st.session_state.allenamenti_calcio = pd.concat(
            [st.session_state.allenamenti_calcio, a_new], ignore_index=True
        )
        st.success("Allenamento registrato!")
        st.rerun()

    if not st.session_state.allenamenti_calcio.empty:
      st.dataframe(st.session_state.allenamenti_calcio, use_container_width=True)


def spotify_page():
  st.title("🎧 Spotify & Monitoraggio Ascolti")
  df_up = carica_file_universale(
      "up_spot", ["Data", "Genere Principale", "Brani Ascoltati", "Artista Top"]
  )
  if df_up is not None:
    st.session_state.spotify_ascolti = pd.concat(
        [st.session_state.spotify_ascolti, df_up], ignore_index=True
    )
    st.rerun()

  with st.form("f_spot"):
    c1, c2 = st.columns(2)
    with c1:
      ds = st.date_input("Data", datetime.today())
      gen = st.text_input("Genere Principale (es. Techno, Pop)")
    with c2:
      brani = st.number_input("Brani Ascoltati", 50)
      art = st.text_input("Artista Top")

    if st.form_submit_button("Registra Dati Spotify"):
      s_new = pd.DataFrame([{
          "Data": str(ds),
          "Genere Principale": gen,
          "Brani Ascoltati": brani,
          "Artista Top": art,
      }])
      st.session_state.spotify_ascolti = pd.concat(
          [st.session_state.spotify_ascolti, s_new], ignore_index=True
      )
      st.success("Registrato!")
      st.rerun()

  if not st.session_state.spotify_ascolti.empty:
    st.dataframe(st.session_state.spotify_ascolti, use_container_width=True)
    st.bar_chart(
        st.session_state.spotify_ascolti.groupby("Genere Principale")[
            "Brani Ascoltati"
        ].sum()
    )


def lavoro_page():
  st.title("⚡ Lavoro & Workspace")
  tab1, tab2 = st.tabs(["📚 Guide Software", "📝 Note Operative"])

  with tab1:
    soft = st.selectbox("Software", ["Bpoint", "Zucchetti Paghe", "AdE"])
    st.text_area(f"Procedure per {soft}:", height=200)

  with tab2:
    st.session_state.note_personali = st.text_area(
        "Blocco note libero:", value=st.session_state.note_personali, height=250
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
    stato = st.selectbox(
        "Stato", ["Da Iniziare", "In Corso", "Completato"]
    )
    voto = st.slider("Valutazione", 1, 10, 8)

    if st.form_submit_button("Aggiungi Elemento"):
      c_new = pd.DataFrame([{
          "Titolo": tit,
          "Tipologia": tip,
          "Stato": stato,
          "Voto / Valutazione": voto,
      }])
      st.session_state.libri_corsi = pd.concat(
          [st.session_state.libri_corsi, c_new], ignore_index=True
      )
      st.success("Aggiunto!")
      st.rerun()

  if not st.session_state.libri_corsi.empty:
    st.dataframe(st.session_state.libri_corsi, use_container_width=True)


def link_page():
  st.title("🔑 Link Vault & Portali Rapidi")
  with st.form("f_link"):
    nome = st.text_input("Nome Portale (es. Agenzia Entrate, Tuttocampo)")
    url = st.text_input("URL / Link web")
    note = st.text_input("Note o credenziali rapide")
    if st.form_submit_button("Salva Link"):
      l_new = pd.DataFrame(
          [{"Nome Portale": nome, "URL": url, "Note / Credenziali": note}]
      )
      st.session_state.link_utili = pd.concat(
          [st.session_state.link_utili, l_new], ignore_index=True
      )
      st.success("Link salvato!")
      st.rerun()

  if not st.session_state.link_utili.empty:
    st.dataframe(st.session_state.link_utili, use_container_width=True)


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


# --- NAVIGAZIONE NATIVA ST.NAVIGATION ---
pg = st.navigation({
    "Panoramica": [st.Page(home_page, title="🏠 Home", default=True)],
    "Finanza & Patrimonio": [st.Page(finanze_page, title="💰 Finanze & Abbonamenti")],
    "Sport & Passioni": [
        st.Page(sport_page, title="⚽ Sport & Calcio"),
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
