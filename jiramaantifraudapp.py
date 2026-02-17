import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --- CONFIGURATION ---
st.set_page_config(page_title="JIRAMA AI Monitor", layout="wide")
st.title("⚡ JIRAMA Smart Monitor & AI Bot")

# --- 1. GÉNÉRATION DES DONNÉES IOT (TRANSFORMATEURS) ---
regions = ["Analamanga", "Atsinanana", "Diana", "Boeny", "Sava"]
def generate_data():
    data = []
    for i in range(15):
        sortie_kw = random.randint(800, 2000)
        facture_kw = sortie_kw * random.uniform(0.5, 0.98) # Simulation de fraude
        perte = round((1 - (facture_kw / sortie_kw)) * 100, 1)
        charge = random.randint(30, 115) # Surcharge possible
        data.append({
            "ID": f"TR-TANA-{100+i}",
            "Région": random.choice(regions),
            "Charge_Pct": charge,
            "Perte_Fraude_Pct": perte,
            "Temp_Huile": random.randint(40, 95)
        })
    return pd.DataFrame(data)

df = generate_data()

# --- 2. BOT DE RECOMMANDATION (IA LOGIQUE) ---
def ai_recommandation(row, lang):
    recos = []
    # Logique de détection
    if row['Perte_Fraude_Pct'] > 25:
        recos.append("🚩 Fraude suspectée élevée" if lang == "FR" else "🚩 High Fraud Suspected")
    if row['Charge_Pct'] > 95:
        recos.append("⚠️ Surcharge critique" if lang == "FR" else "⚠️ Critical Overload")
    if row['Temp_Huile'] > 85:
        recos.append("🔥 Surchauffe huile" if lang == "FR" else "🔥 Oil Overheating")
    
    if not recos:
        return "✅ État Nominal" if lang == "FR" else "✅ Nominal State"
    return " | ".join(recos)

# --- 3. INTERFACE UTILISATEUR ---
lang = st.radio("Sélectionner la langue du Bot / Select Bot Language", ["FR", "EN"])

st.sidebar.header("📡 Paramètres Réseau")
seuil_alerte = st.sidebar.slider("Seuil Alerte Fraude (%)", 10, 50, 25)

# --- 4. TABLEAU DE BORD & BOT ---
st.subheader("🤖 Analyse Automatisée du Bot")

# On ajoute la recommandation du bot au DataFrame
df['Recommandation_Bot'] = df.apply(lambda row: ai_recommandation(row, lang), axis=1)

# Affichage stylisé
st.dataframe(df.style.apply(lambda x: ['background-color: #ff4b4b' if '🚩' in str(v) or '⚠️' in str(v) else '' for v in x], axis=1), use_container_width=True)

# --- 5. FOCUS SUR LE STOCKAGE (BATTERIES) ---
st.markdown("---")
col_bot, col_bat = st.columns([1, 1])

with col_bot:
    st.subheader("🗨️ Chatbot : Actions Prioritaires")
    targets = df[df['Charge_Pct'] > 90]
    if not targets.empty:
        for _, r in targets.iterrows():
            msg = f"**{r['ID']}** ({r['Région']}): Délester de {r['Charge_Pct']-90}% ou injecter batterie." if lang == "FR" else f"**{r['ID']}** ({r['Région']}): Shed {r['Charge_Pct']-90}% load or inject battery."
            st.warning(msg)
    else:
        st.success("Aucune action urgente requise." if lang == "FR" else "No urgent actions required.")

with col_bat:
    st.subheader("🔋 Gestion du Stockage (BESS)")
    # Simulation de surproduction solaire (Scraping météo virtuel)
    meteo_soleil = random.randint(0, 100) 
    st.write(f"Ensoleillement à Tana : {meteo_soleil}%")
    if meteo_soleil > 70:
        st.info("Surproduction solaire active. Chargement des batteries de secours (Antsirabe/Tana).")
        st.progress(meteo_soleil / 100)
    else:
        st.error("Faible production. Utilisation des réserves pour éviter le délestage.")

# --- 6. CARTOGRAPHIE DES VOLS ---
st.subheader("🗺️ Cartographie des zones de pertes (Fraudes)")
fig = px.scatter(df, x="Région", y="Perte_Fraude_Pct", size="Charge_Pct", color="Temp_Huile",
                 hover_name="ID", title="Analyse Spatiale des Pertes JIRAMA")
st.plotly_chart(fig, use_container_width=True)
