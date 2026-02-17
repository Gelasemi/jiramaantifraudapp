import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --- CONFIGURATION JIRAMA ---
st.set_page_config(page_title="JIRAMA - Supervision Nationale", layout="wide")
st.title("⚡ JIRAMA : Plateforme de Lutte contre la Fraude & Optimisation")

# --- 1. SIMULATION DONNÉES TRANSFORMATEURS (Surcharge & Fraude) ---
# Dans la réalité, ces données proviennent de compteurs communicants Schneider/Siemens
regions = ["Analamanga", "Atsinanana", "Diana", "Boeny", "Sava"]
data_transfo = []

for i in range(20):
    region = random.choice(regions)
    energie_sortie_kw = random.randint(500, 1500)
    energie_facturee_kw = energie_sortie_kw * random.uniform(0.6, 0.95) # Le reste est de la perte/vol
    perte_pourcentage = (1 - (energie_facturee_kw / energie_sortie_kw)) * 100
    charge_transfo = random.randint(40, 110) # > 100% = Surcharge
    
    data_transfo.append({
        "Transfo_ID": f"TR-{1000+i}",
        "Region": region,
        "Charge (%)": charge_transfo,
        "Perte/Vol (%)": round(perte_pourcentage, 2),
        "Statut": "CRITIQUE" if charge_transfo > 95 or perte_pourcentage > 30 else "OK"
    })

df_jirama = pd.DataFrame(data_transfo)

# --- 2. MODULE WEB SCRAPING (Simulation Météo pour Solaire) ---
# On simule ici la récupération de données météo pour l'ensoleillement à Tana
st.sidebar.header("🌦️ Prévisions Production Solaire")
st.sidebar.info("Données récupérées via [Open-Météo](https://open-meteo.com)")
ensoleillement = st.sidebar.slider("Ensoleillement prévu (W/m²)", 0, 1000, 800)

# --- 3. GESTION SURPRODUCTION & BATTERIES ---
surproduction = 0
if ensoleillement > 700:
    surproduction = (ensoleillement - 700) * 10 # kW excédentaires
    st.sidebar.warning(f"🔋 SURPRODUCTION DÉTECTÉE : {surproduction} kW en cours de stockage.")

# --- 4. DASHBOARD SUPERVISION ---
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric("Pertes Non Techniques (Vol)", f"{df_jirama['Perte/Vol (%)'].mean():.1f}%", delta="⚠️ Critique")
with kpi2:
    transfos_critiques = len(df_jirama[df_jirama['Statut'] == "CRITIQUE"])
    st.metric("Transformateurs en Surcharge", transfos_critiques, delta=f"{transfos_critiques} alertes")
with kpi3:
    st.metric("Énergie Stockée (Batteries)", f"{surproduction * 24:,.0f} kWh")

st.markdown("---")

# --- 5. CARTOGRAPHIE ANALYTIQUE ---
st.subheader("📍 Cartographie des Risques par Région")
fig_map = px.scatter(df_jirama, x="Region", y="Perte/Vol (%)", size="Charge (%)", 
                     color="Statut", hover_name="Transfo_ID",
                     title="Localisation des vols d'électricité et surcharges")
st.plotly_chart(fig_map, use_container_width=True)

# --- 6. PLANIFICATION DES DESCENTES ---
st.subheader("📅 Planification des Descentes Techniques")
priority_targets = df_jirama[df_jirama['Perte/Vol (%)'] > 25].sort_values(by="Perte/Vol (%)", ascending=False)
st.write("Cibles prioritaires pour les agents de contrôle :")
st.dataframe(priority_targets)

# --- 7. AMÉLIORATION : OPTIMISATION CONSOMMATION ---
st.info("💡 **Conseil d'optimisation :** En cas de pic de charge sur Analamanga, basculer le surplus des batteries vers le réseau pour éviter le délestage tournant.")
