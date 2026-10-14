from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Archivio & Caricamento", page_icon="📁", layout="wide"
)

st.title("📁 Archivio Universale e Storico File")
st.markdown(
    "Carica i tuoi file in formato multiplo (Excel, CSV, PDF, Word). I file"
    " tabulari aggiorneranno automaticamente le finanze."
)

uploaded_files = st.file_uploader(
    "Seleziona i file da caricare:",
    accept_multiple_files=True,
    type=["pdf", "docx", "xlsx", "xls", "csv", "txt"],
)

if uploaded_files:
  st.write(f"📁 Hai selezionato {len(uploaded_files)} file.")

  if st.button("🚀 Conferma Upload e Storicizza"):
    for uploaded_file in uploaded_files:
      file_name = uploaded_file.name
      file_size = f"{uploaded_file.size / 1024:.1f} KB"
      data_caricamento = datetime.now().strftime("%Y-%m-%d %H:%M")

      # Aggiungi allo storico permanente
      archivio_nomi = [
          item["Nome File"] for item in st.session_state.archivio_file
      ]
      if file_name not in archivio_nomi:
        st.session_state.archivio_file.append({
            "Nome File": file_name,
            "Dimensione": file_size,
            "Data Caricamento": data_caricamento,
        })

      # Se è un foglio di calcolo, aggiorna i dati finanziari
      if file_name.endswith((".csv", ".xlsx", ".xls")):
        try:
          if file_name.endswith(".csv"):
            df_temp = pd.read_csv(uploaded_file)
          else:
            df_temp = pd.read_excel(uploaded_file)

          st.session_state.dati_finanziari = pd.concat(
              [st.session_state.dati_finanziari, df_temp], ignore_index=True
          )
        except Exception as e:
          st.error(f"Errore lettura file {file_name}: {e}")

    st.success("✅ File caricati, storicizzati e sincronizzati con successo!")
    st.balloons()

st.markdown("---")
st.subheader("📚 Storico Documenti Salvati")
if len(st.session_state.archivio_file) > 0:
  st.dataframe(
      pd.DataFrame(st.session_state.archivio_file), use_container_width=True
  )
else:
  st.info("Nessun file presente nell'archivio storico.")
