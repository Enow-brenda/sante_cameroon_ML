
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SanteCameroon",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── STATE MANAGEMENT ─────────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "FR"

# ─── TRANSLATIONS ─────────────────────────────────────────────────────────────
T = {
    "EN": {
        "brand": "SanteCam Intelligence",
        "tagline": "Cameroon Public Health Analysis Platform",
        "nav_summary": "Executive Summary",
        "nav_univariate": "Univariate Analysis",
        "nav_bivariate": "Bivariate Analysis",
        "nav_about": "Project Context",
        "kpi_mortality": "Avg. Mortality",
        "kpi_vaccination": "Vaccination Rate",
        "kpi_income": "Avg. Income",
        "kpi_access": "Health Access",
        "top_districts": "Top Performing Districts",
        "univariate_title": "Indicator Distributions",
        "univariate_stats": "Stats Summary",
        "bivariate_title": "Correlation & Risk Factors",
        "bivariate_corr": "Pearson Correlation Matrix",
        "data_dictionary": "Data Dictionary",
        "insight_title": "Insight",
        "labels": {
            "revenu_moyen": "Avg. Income (XAF)",
            "acces_sante": "Healthcare Access",
            "taux_vaccination": "Vaccination Rate",
            "nombre_medecins": "No. of Doctors",
            "pollution": "Pollution Index",
            "taux_mortalite_infantile": "Infant Mortality Rate",
        },
        "about_text": "This dashboard presents a comprehensive Exploratory Data Analysis (EDA) of Cameroon's public health indicators. Based on the analysis of 200 districts, we identified key socio-economic and environmental drivers of infant mortality.",
         "insights": [
            ("Vaccination Shield", "Vaccination rate is the #1 protective factor (r = -0.56). Higher coverage consistently drives down mortality."),
            ("Economic Gradient", "Wealthier districts (r = -0.47) have significantly better survival outcomes due to better infrastructure."),
            ("Urban Paradox", "Pollution (r = +0.34) and Physician counts (r = +0.30) are positively linked to mortality, indicating urban industrial risks."),
            ("Data Integrity", "No significant outliers detected. Distributions are symmetric and ready for advanced modeling.")
        ]
    },
    "FR": {
        "brand": "SanteCam Intelligence",
        "tagline": "Plateforme d'Analyse de la Santé Publique au Cameroun",
        "nav_summary": "Résumé Exécutif",
        "nav_univariate": "Analyse Univariée",
        "nav_bivariate": "Analyse Bivariée",
        "nav_about": "Contexte du Projet",
        "kpi_mortality": "Mortalité Moyenne",
        "kpi_vaccination": "Taux de Vaccination",
        "kpi_income": "Revenu Moyen",
        "kpi_access": "Accès Santé",
        "insight_title": "Apercu",
        "top_districts": "Districts les Plus Performants",
        "univariate_title": "Distributions des Indicateurs",
        "univariate_stats": "Résumé Statistique",
        "bivariate_title": "Corrélations & Facteurs de Risque",
        "bivariate_corr": "Matrice de Corrélation de Pearson",
        "data_dictionary": "Dictionnaire des Données",
        "labels": {
            "revenu_moyen": "Revenu Moyen (XAF)",
            "acces_sante": "Accès Santé",
            "taux_vaccination": "Taux Vaccination",
            "nombre_medecins": "Nb. de Médecins",
            "pollution": "Indice de Pollution",
            "taux_mortalite_infantile": "Mortalité Infantile",
        },
        "about_text": "Ce tableau de bord présente une analyse exploratoire des indicateurs de santé publique au Cameroun. Basé sur l'analyse de 200 districts, nous avons identifié les principaux facteurs socio-économiques et environnementaux de la mortalité infantile.",
           "insights": [
            ("Bouclier Vaccinal", "La vaccination est le facteur #1 (r = -0,56). Une meilleure couverture réduit systématiquement la mortalité."),
            ("Gradient Économique", "Les districts riches (r = -0,47) ont de meilleurs résultats grâce aux infrastructures."),
            ("Paradoxe Urbain", "La pollution (r = +0,34) et le nombre de médecins (r = +0,30) sont liés à la mortalité, indiquant des risques industriels."),
            ("Intégrité des Données", "Aucune valeur aberrante détectée. Les données sont symétriques et prêtes pour la modélisation.")
        ]
    }
}

tx = T[st.session_state.lang]

# ─── THEME & CSS ──────────────────────────────────────────────────────────────
BG = "#0b0e14"
SURFACE = "#151921"
CARD = "#1c222d"
BORDER = "#2d3643"
TEXT = "#ffffff"
SUBTEXT = "#94a3b8"
ACCENT = "#3b82f6"
ACCENT_LIGHT = "#60a5fa"
ACCENT_L = "#58a6ff"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {BG};
        color: {TEXT};
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    
    [data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none; }}
    [data-testid="stSidebar"] {{ display: none; }}
    footer {{ visibility: hidden; }}

    .header-bar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid {BORDER};
    }}
    
    .brand-logo {{
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -1px;
        color: {TEXT};
    }}
    
    .glass-card {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
    }}
    
    .kpi-box {{
        text-align: center;
        padding: 10px;
    }}
    
    .kpi-val {{
        font-size: 2.2rem;
        font-weight: 800;
        color: {ACCENT_LIGHT};
    }}
    
    .kpi-lbl {{
        font-size: 0.8rem;
        color: {SUBTEXT};
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 40px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 60px;
        background-color: transparent !important;
        border: none !important;
        color: {SUBTEXT} !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {ACCENT_LIGHT} !important;
        border-bottom: 3px solid {ACCENT_LIGHT} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    try:
        return pd.read_csv("sante_cameroun.csv")
    except:
        rng = np.random.default_rng(42)
        n = 200
        return pd.DataFrame({
            "revenu_moyen": rng.uniform(100000, 800000, n),
            "acces_sante": rng.uniform(20, 100, n),
            "taux_vaccination": rng.uniform(20, 100, n),
            "nombre_medecins": rng.integers(1, 40, n),
            "pollution": rng.uniform(10, 100, n),
            "taux_mortalite_infantile": rng.uniform(5, 50, n),
        })

df = get_data()
COLS = list(df.columns)

# ─── HEADER ───────────────────────────────────────────────────────────────────
h1, h2 = st.columns([4, 1])
with h1:
    st.markdown(f"<div class='brand-logo'>💠 {tx['brand']}</div>", unsafe_allow_html=True)
with h2:
    lang = st.segmented_control("Lang", ["EN", "FR"], default=st.session_state.lang, label_visibility="collapsed")
    if lang != st.session_state.lang:
        st.session_state.lang = lang
        st.rerun()

# ─── TABS ─────────────────────────────────────────────────────────────────────
tabs = st.tabs([tx[p] for p in ["nav_summary", "nav_univariate", "nav_bivariate","insight_title", "nav_about"]])

# ─── PLOT STYLE ───────────────────────────────────────────────────────────────
def style_fig(fig, title=""):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT, family="Plus Jakarta Sans", size=14),
        margin=dict(t=80, b=50, l=70, r=40),
        title=dict(text=title, font=dict(size=18, weight='bold')),
        xaxis=dict(gridcolor=BORDER, linecolor=BORDER),
        yaxis=dict(gridcolor=BORDER, linecolor=BORDER),
    )
    return fig

# ─── TAB 1: SUMMARY ───────────────────────────────────────────────────────────
with tabs[0]:
    k1, k2, k3, k4 = st.columns(4)
    for col, (val, lbl) in zip([k1, k2, k3, k4], [
        (f"{df['taux_mortalite_infantile'].mean():.1f}", tx["kpi_mortality"]),
        (f"{df['taux_vaccination'].mean():.1f}%", tx["kpi_vaccination"]),
        (f"{int(df['revenu_moyen'].mean()/1000)}k", tx["kpi_income"]),
        (f"{df['acces_sante'].mean():.1f}", tx["kpi_access"])
    ]):
        with col:
            st.markdown(f"""
            <div class="glass-card kpi-box">
                <div class="kpi-lbl">{lbl}</div>
                <div class="kpi-val">{val}</div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown(f"### {tx['top_districts']}")
    st.dataframe(df.nsmallest(10, 'taux_mortalite_infantile').rename(columns=tx['labels']), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─── TAB 2: UNIVARIATE ────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown(f"### {tx['univariate_title']}")
    u_sel = st.selectbox("Choose Indicator", COLS, format_func=lambda x: tx['labels'].get(x, x))
    
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_hist = px.histogram(df, x=u_sel, nbins=25, marginal="box", color_discrete_sequence=[ACCENT])
        style_fig(fig_hist, f"Distribution of {tx['labels'][u_sel]}")
        st.plotly_chart(fig_hist, use_container_width=True)
    with c2:
        st.markdown(f"#### {tx['univariate_stats']}")
        st.write(df[u_sel].describe())
        skew = df[u_sel].skew()
        st.metric("Skewness", f"{skew:.4f}", "Symmetric" if abs(skew) < 0.5 else "Skewed")

# ─── TAB 3: BIVARIATE ─────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown(f"### {tx['bivariate_title']}")
    b_tab1, b_tab2 = st.tabs(["Regression Analysis", "Correlation Matrix"])
    
    with b_tab1:
        cc1, cc2 = st.columns(2)
        x_var = cc1.selectbox("Predictor (X)", COLS, index=2, format_func=lambda x: tx['labels'].get(x, x))
        y_var = cc2.selectbox("Target (Y)", COLS, index=5, format_func=lambda x: tx['labels'].get(x, x))
        
        fig_scatter = px.scatter(df, x=x_var, y=y_var, trendline="ols", color_discrete_sequence=[ACCENT_LIGHT])
        style_fig(fig_scatter, f"{tx['labels'][x_var]} vs {tx['labels'][y_var]}")
        fig_scatter.update_traces(marker=dict(size=10, opacity=0.7))
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with b_tab2:
        corr = df.corr().round(2)
        fig_heat = px.imshow(corr, text_auto=True, color_continuous_scale="Blues")
        style_fig(fig_heat, f"{tx['bivariate_corr']}")
        st.plotly_chart(fig_heat, use_container_width=True)

# ─── TAB 4: INSIGHTS ─────────────────────────────────────────────────────────────

with tabs[3]:
    # st.markdown(f"### {tx['insight_title']}")
    for title, desc in tx["insights"]:
        st.markdown(f"""
        <div style="padding: 24px; border-radius: 12px; background: {CARD}; border-left: 5px solid {ACCENT_L}; margin-bottom: 16px;">
            <h4 style="margin:0; color:{ACCENT_L}; text-transform:uppercase; font-size:0.9rem; letter-spacing:1px;">{title}</h4>
            <p style="margin:8px 0 0 0; color:{TEXT}; font-size:1.1rem; line-height:1.6;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# ─── TAB 5: ABOUT ─────────────────────────────────────────────────────────────
with tabs[4]:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown(f"### About {tx['brand']}")
    st.write(tx["about_text"])
    st.markdown("---")
    st.markdown(f"#### {tx['data_dictionary']}")
    for k, v in tx['labels'].items():
        st.markdown(f"**{k}**: {v}")
    st.markdown("</div>", unsafe_allow_html=True)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown(f"<div style='text-align:center; padding:3rem; color:{SUBTEXT}; font-size:0.8rem;'>SANTECAMEROON • 2026</div>", unsafe_allow_html=True)
