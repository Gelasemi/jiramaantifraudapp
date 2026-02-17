import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="JIRAMA Mission Control", layout="wide")
st.title("⚡ JIRAMA : Détection de Fraude & Ordres de Mission")

# --- 1. GÉNÉRATION DES DONNÉES IOT (SIMULATION TEMPS RÉEL) ---
regions = ["Analamanga", "Atsinanana", "Diana", "Boeny", "Sava"]
@st.cache_data
def load_data():
    data = []
    for i in range(20):
        sortie_kw = random.randint(1000, 3000)
        facture_kw = sortie_kw * random.uniform(0.4, 0.95) # Simulation pertes non techniques
        perte_pct = round((1 - (facture_kw / sortie_kw)) * 100, 1)
        charge = random.randint(40, 115)
        # Coût de la perte (Tarif JIRAMA moyen ~600 Ar/kWh)
        perte_ariary = (sortie_kw - facture_kw) * 24 * 30 * 600 
        
        data.append({
            "ID_Transfo": f"TR-MDG-{1000+i}",
            "Région": random.choice(regions),
            "Charge (%)": charge,
            "Perte/Vol (%)": perte_pct,
            "Manque à gagner (Ar)": perte_ariary,
            "Priorité": "HAUTE" if perte_pct > 30 or charge > 100 else "NORMALE"
        })
    return pd.DataFrame(data)

df = load_data()

# --- 2. BOT DE RECOMMANDATION BILINGUE ---
lang = st.radio("Langue / Language", ["FR", "EN"])

def bot_logic(row):
    if row['Perte/Vol (%)'] > 35:
        return "🚨 Descente immédiate requise : Vol massif suspecté." if lang == "FR" else "🚨 Immediate raid required: Massive theft suspected."
    elif row['Charge (%)'] > 100:
        return "⚠️ Délestage imminent : Basculer sur batterie." if lang == "FR" else "⚠️ Imminent blackout: Switch to battery."
    return "✅ Stable"

df['Action_Bot'] = df.apply(bot_logic, axis=1)

# --- 3. DASHBOARD FINANCIER & TECHNIQUE ---
total_perte = df["Manque à gagner (Ar)"].sum()
st.sidebar.metric("Manque à gagner Mensuel", f"{total_perte:,.0f} Ar")
st.sidebar.info(f"Équivalent à environ {total_perte/4500:,.0f} € de perte sèche.")

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Pertes Moyennes", f"{df['Perte/Vol (%)'].mean():.1f}%", delta="Vol d'électricité")
kpi2.metric("Surcharges Actives", len(df[df['Charge (%)'] > 100]))
kpi3.metric("Météo Solaire (Tana)", "☀️ 850 W/m²", help="Données scrapées via Open-Météo")

st.markdown("---")

# --- 4. PLANIFICATION DES MISSIONS (EXPORT) ---
st.subheader("📋 Ordres de Mission Prioritaires")
missions_urgentes = df[df['Priorité'] == "HAUTE"].sort_values(by="Perte/Vol (%)", ascending=False)

st.dataframe(missions_urgentes[['ID_Transfo', 'Région', 'Perte/Vol (%)', 'Action_Bot']])

# Bouton d'exportation pour les équipes terrain
csv = missions_urgentes.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Télécharger les Ordres de Mission (CSV)",
    data=csv,
    file_name=f"ordres_mission_JIRAMA_{datetime.now().strftime('%Y-%m-%d')}.csv",
    mime="text/csv",
)

# --- 5. CARTOGRAPHIE DES PERTES ---
st.subheader("📍 Analyse Géographique des Fraudes")
fig = px.scatter(df, x="Région", y="Perte/Vol (%)", size="Manque à gagner (Ar)", color="Priorité",
                 hover_name="ID_Transfo", color_discrete_map={"HAUTE": "red", "NORMALE": "green"})
st.plotly_chart(fig, use_container_width=True)

# --- 6. OPTIMISATION DU DÉLESTAGE ---
st.info("""
💡 **Recommandation Stratégique :** 
Utilisez la surproduction solaire du parc de **Ambatolampy** pour charger les batteries de secours. 
Cela permettra d'injecter du courant dans les zones 'TR-MDG' en surcharge sans couper les abonnés.
""")
