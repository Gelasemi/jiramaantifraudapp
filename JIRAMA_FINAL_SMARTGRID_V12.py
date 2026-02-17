import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
import random
import os
import base64
from gtts import gTTS
from datetime import datetime

# --- 1. SÉCURITÉ ET AUTHENTIFICATION ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# Comptes : admin_jirama / admin123 | agent_tana / agent123
users = {
    "admin_jirama": {"pwd": make_hashes("admin123"), "role": "ADMIN"},
    "agent_tana": {"pwd": make_hashes("agent123"), "role": "AGENT"}
}

if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'role': None, 'user': None, 'audit_log': []})

def add_audit(action, target):
    st.session_state.audit_log.append({
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "User": st.session_state.user,
        "Action": action,
        "Cible": target
    })

# --- 2. FONCTION SYNTHÈSE VOCALE (TTS) ---
def speak_text(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        filename = "temp_speech.mp3"
        tts.save(filename)
        with open(filename, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio controls autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
        os.remove(filename)
    except Exception as e:
        st.error(f"Erreur audio : {e}")

# --- 3. INTERFACE DE CONNEXION ---
if not st.session_state.logged_in:
    st.title("🔐 JIRAMA : Accès Sécurisé Smart Grid")
    with st.form("login"):
        u = st.text_input("Matricule / Identifiant")
        p = st.text_input("Mot de passe", type='password')
        if st.form_submit_button("Se connecter"):
            if u in users and check_hashes(p, users[u]["pwd"]):
                st.session_state.update({'logged_in': True, 'role': users[u]["role"], 'user': u})
                st.rerun()
            else: st.error("Identifiants invalides")
    st.stop()

# --- 4. LOGIQUE MÉTIER (DONNÉES ET IA) ---
st.sidebar.title(f"👤 {st.session_state.user}")
lang = st.sidebar.radio("Langue de l'Assistant", ["FR", "EN"])
lang_code = 'fr' if lang == "FR" else 'en'

@st.cache_data
def load_data():
    regions = ["Analamanga", "Atsinanana", "Diana", "Boeny", "Sava"]
    data = []
    # Ajout du transformateur pilote obligatoire
    data.append({"ID": "TR-PILOTE-01", "Région": "Analamanga (Isotry)", "Charge_%": 105, "Perte_Vol_%": 35.0, "Priorité": "HAUTE"})
    
    for i in range(11):
        sortie = random.randint(1000, 2500)
        facture = sortie * random.uniform(0.40, 0.98)
        perte_pct = round((1 - (facture / sortie)) * 100, 1)
        charge = random.randint(40, 115)
        data.append({
            "ID": f"TR-MDG-{200+i}", "Région": random.choice(regions),
            "Charge_%": charge, "Perte_Vol_%": perte_pct,
            "Priorité": "HAUTE" if perte_pct > 25 or charge > 100 else "NORMAL"
        })
    return pd.DataFrame(data)

df = load_data()

# --- 5. DASHBOARD PRINCIPAL ---
st.title("🎙️ JIRAMA AI : Supervision Vocale & Anti-Fraude")

# Sélection du transformateur
selected_id = st.selectbox("Sélectionner un transformateur pour rapport vocal", df['ID'])
row = df[df['ID'] == selected_id].iloc[0]

def get_diagnosis(r):
    diag = []
    if r['Perte_Vol_%'] > 25: diag.append("🚩 Fraude détectée" if lang=="FR" else "🚩 Fraud detected")
    if r['Charge_%'] > 100: diag.append("⚠️ Surcharge critique" if lang=="FR" else "⚠️ Critical Overload")
    return " | ".join(diag) if diag else ("✅ Stable" if lang=="FR" else "✅ Stable")

diagnosis = get_diagnosis(row)

if lang == "FR":
    script = f"Transformateur {row['ID']}. Région {row['Région']}. Charge {row['Charge_%']} pourcent. Vol suspecté {row['Perte_Vol_%']} pourcent. Diagnostic : {diagnosis}."
else:
    script = f"Transformer {row['ID']}. Region {row['Région']}. Load {row['Charge_%']} percent. Theft suspected {row['Perte_Vol_%']} percent. Diagnosis: {diagnosis}."

col1, col2 = st.columns([2, 1])
with col1:
    st.info(f"**Analyse du Bot :** {diagnosis}")
    st.write(f"**Script vocal :** {script}")
with col2:
    if st.button("🔊 LIRE LE RAPPORT"):
        speak_text(script, lang_code)
        add_audit("LECTURE_VOCALE", row['ID'])

st.markdown("---")

# --- 6. VUES PAR RÔLE ---

# --- VUE ADMIN ---
if st.session_state.role == "ADMIN":
    st.subheader("🛡️ Console Administration & Protocoles")
    tab_map, tab_audit, tab_proto, tab_checklist = st.tabs(["🗺️ Cartographie", "📜 Audit Log", "🧪 Protocole Pilote", "📋 Check-list Go-Live"])
    
    with tab_map:
        fig = px.scatter(df, x="Région", y="Perte_Vol_%", size="Charge_%", color="Priorité", hover_name="ID")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab_audit:
        st.table(pd.DataFrame(st.session_state.audit_log)) if st.session_state.audit_log else st.write("Aucun log.")

    with tab_proto:
        st.markdown("""
        ### 🧪 Protocole de Test Pilote : TR-PILOTE-01
        1. **Configuration** : Emplacement Isotry. Capteur MQTT actif.
        2. **Scénario A (Référence)** : Vérifier 0% fraude -> Bot doit dire "Stable".
        3. **Scénario B (Injection)** : Simuler 35% écart -> Alerte rouge immédiate.
        4. **Scénario C (Surcharge)** : Simuler >100% charge -> Alerte Orange + Batterie.
        """)

    with tab_checklist:
        st.markdown("""
        ### 📋 Check-list Finale Go-Live
        - [ ] **MQTT SSL** : Certificat installé sur le broker.
        - [ ] **Secrets** : Mots de passe déplacés dans `secrets.toml`.
        - [ ] **Requirements** : gTTS, plotly, paho-mqtt installés.
        - [ ] **Backup** : Base de données des logs sauvegardée.
        """)

# --- VUE AGENT ---
else:
    st.subheader("📋 Mes Missions Terrain")
    missions = df[df['Priorité'] == "HAUTE"]
    st.dataframe(missions)
    if st.download_button("📥 Exporter Missions (CSV)", missions.to_csv().encode('utf-8'), "missions_tana.csv", "text/csv"):
        add_audit("EXPORT_CSV", "Liste_Missions")

if st.sidebar.button("Déconnexion"):
    st.session_state.logged_in = False
    st.rerun()
