import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
import random
from datetime import datetime

# --- 1. SÉCURITÉ & AUTHENTIFICATION ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# Base de données utilisateurs (Admin: admin123 | Agent: agent123)
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

# --- 2. INTERFACE DE CONNEXION ---
if not st.session_state.logged_in:
    st.title("⚡ JIRAMA : Accès Sécurisé Smart Grid")
    with st.form("login"):
        u = st.text_input("Matricule / Username")
        p = st.text_input("Mot de passe", type='password')
        if st.form_submit_button("Se connecter"):
            if u in users and check_hashes(p, users[u]["pwd"]):
                st.session_state.update({'logged_in': True, 'role': users[u]["role"], 'user': u})
                st.rerun()
            else: st.error("Identifiants incorrects")
    st.stop()

# --- 3. LOGIQUE MÉTIER & DONNÉES (SIMULATION IOT) ---
st.sidebar.title(f"👤 {st.session_state.user}")
lang = st.sidebar.radio("Langue", ["FR", "EN"])

@st.cache_data
def load_network_data():
    regions = ["Analamanga", "Atsinanana", "Diana", "Boeny", "Sava"]
    data = []
    for i in range(15):
        sortie = random.randint(1000, 2500)
        facture = sortie * random.uniform(0.45, 0.98) # Vol si < 0.75
        charge = random.randint(40, 115)
        perte_pct = round((1 - (facture / sortie)) * 100, 1)
        data.append({
            "ID": f"TR-MDG-{100+i}", "Région": random.choice(regions),
            "Charge_%": charge, "Perte_Vol_%": perte_pct,
            "Temp_C": random.randint(40, 95), "Priority": "HAUTE" if perte_pct > 25 or charge > 100 else "NORMAL"
        })
    return pd.DataFrame(data)

df = load_network_data()

# --- 4. BOT DE RECOMMANDATION IA ---
def get_bot_advice(row):
    recos = []
    if row['Perte_Vol_%'] > 25: recos.append("🚩 Fraude suspectée" if lang=="FR" else "🚩 Fraud suspected")
    if row['Charge_%'] > 100: recos.append("⚠️ Surcharge (Délestage imminent)" if lang=="FR" else "⚠️ Overload (Shedding imminent)")
    return " | ".join(recos) if recos else ("✅ Stable" if lang=="FR" else "✅ Clear")

df['Bot_Advice'] = df.apply(get_bot_advice, axis=1)

# --- 5. DASHBOARD PRINCIPAL ---
st.title("📊 JIRAMA Smart Supervision")

# KPI Globaux
c1, c2, c3 = st.columns(3)
c1.metric("Pertes Moyennes (Vols)", f"{df['Perte_Vol_%'].mean():.1f}%", delta="-2% vs mois dernier")
c2.metric("Transfos Critiques", len(df[df['Priority'] == "HAUTE"]))
c3.metric("Stockage Batteries (BESS)", "85%", help="Énergie solaire stockée disponible")

# --- 6. VUE AGENT : MISSIONS TERRAIN ---
st.subheader("📋 Ordres de Mission Prioritaires")
missions = df[df['Priority'] == "HAUTE"]
st.dataframe(missions[['ID', 'Région', 'Perte_Vol_%', 'Bot_Advice']])

if st.button("📥 Générer Rapport d'Intervention CSV"):
    add_audit("EXPORT_MISSIONS", "Fichier_CSV")
    csv = missions.to_csv(index=False).encode('utf-8')
    st.download_button("Télécharger CSV", csv, "missions_jirama.csv", "text/csv")

# --- 7. VUE ADMIN : ANALYSE STRATÉGIQUE & AUDIT ---
if st.session_state.role == "ADMIN":
    st.markdown("---")
    st.subheader("🛡️ Console d'Administration & Audit")
    
    tab1, tab2 = st.tabs(["Analyse des Vols", "Journal d'Audit"])
    
    with tab1:
        fig = px.scatter(df, x="Région", y="Perte_Vol_%", size="Charge_%", color="Bot_Advice", hover_name="ID")
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        if st.session_state.audit_log:
            st.table(pd.DataFrame(st.session_state.audit_log))
        else: st.write("Aucune activité enregistrée.")

# Déconnexion
if st.sidebar.button("Déconnexion / Logout"):
    st.session_state.logged_in = False
    st.rerun()
