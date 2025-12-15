# AynalyxAI Demo - Streamlit Cloud Version
# Sample data only - no file upload

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# Page config - WIDE layout for better visibility
st.set_page_config(
    page_title="AynalyxAI Demo",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for wider sidebar and colored results
st.markdown('''
<style>
    [data-testid="stSidebar"] {
        min-width: 320px;
        max-width: 400px;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .demo-badge {
        background: #fef3c7;
        color: #92400e;
        padding: 0.75rem 1.25rem;
        border-radius: 10px;
        font-weight: 600;
        display: block;
        text-align: center;
        margin-bottom: 1.5rem;
        border: 2px solid #f59e0b;
    }
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid;
    }
    .stat-critical { border-color: #dc2626; }
    .stat-high { border-color: #ef4444; }
    .stat-medium { border-color: #f59e0b; }
    .stat-low { border-color: #22c55e; }
    .sidebar-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1e293b;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    .cta-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 2px solid #667eea;
        margin-top: 2rem;
    }
    .cta-button {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        text-decoration: none;
        font-weight: bold;
        margin-top: 1rem;
    }
</style>
''', unsafe_allow_html=True)

# Language selection
with st.sidebar:
    st.markdown('<p class="sidebar-title"> Language / Langue</p>', unsafe_allow_html=True)
    lang = st.selectbox("", ["English", "Français"], label_visibility="collapsed")
    is_fr = lang == "Français"

# Translations
t = {
    "title": "AynalyxAI Demo" if not is_fr else "Démo AynalyxAI",
    "subtitle": "AI-Powered Anomaly Detection" if not is_fr else "Détection d'Anomalies par IA",
    "demo_notice": " FREE DEMO  Try with our sample data!" if not is_fr else " DÉMO GRATUITE  Essayez avec nos données!",
    "sample_title": " Select Sample Data" if not is_fr else " Sélectionner des Données",
    "sample_invoices": " Invoices" if not is_fr else " Factures",
    "sample_expenses": " Expenses" if not is_fr else " Dépenses",
    "sample_payroll": " Payroll" if not is_fr else " Paie",
    "sample_inventory": " Inventory" if not is_fr else " Inventaire",
    "results": " Detection Results" if not is_fr else " Résultats",
    "download_excel": " Download Excel" if not is_fr else " Télécharger Excel",
    "data_preview": " Data Preview" if not is_fr else " Aperçu",
    "critical": "CRITICAL" if not is_fr else "CRITIQUE",
    "high": "HIGH" if not is_fr else "ÉLEVÉ",
    "medium": "MEDIUM" if not is_fr else "MOYEN",
    "low": "LOW" if not is_fr else "FAIBLE",
    "normal": "Normal" if not is_fr else "Normal",
    "explanation": "Explanation" if not is_fr else "Explication",
    "level": "Level" if not is_fr else "Niveau",
    "score": "Score" if not is_fr else "Score",
    "welcome_title": " Select Sample Data" if not is_fr else " Sélectionnez des Données",
    "welcome_text": "Click a sample button in the sidebar." if not is_fr else "Cliquez sur un bouton dans la barre latérale.",
    "get_full": "Get Full Version" if not is_fr else "Version Complète",
    "full_features": "Advanced AI, Aggregation, Ratios, 100% Offline" if not is_fr else "IA Avancée, Agrégation, Ratios, 100% Hors-ligne",
}

def get_explanation(value, mean, std, col_name, is_fr):
    z_score = abs((value - mean) / std) if std > 0 else 0
    pct_diff = ((value - mean) / mean * 100) if mean != 0 else 0
    if z_score > 3:
        if value > mean:
            return f"EXTREME: {value:,.2f} is {abs(pct_diff):.0f}% above avg ({mean:,.2f})" if not is_fr else f"EXTRÊME: {value:,.2f} est {abs(pct_diff):.0f}% au-dessus de la moy ({mean:,.2f})"
        else:
            return f"EXTREME: {value:,.2f} is {abs(pct_diff):.0f}% below avg ({mean:,.2f})" if not is_fr else f"EXTRÊME: {value:,.2f} est {abs(pct_diff):.0f}% en-dessous de la moy ({mean:,.2f})"
    elif z_score > 2.5:
        return f"Very {'high' if value > mean else 'low'}: {value:,.2f} vs avg {mean:,.2f}" if not is_fr else f"Très {'élevé' if value > mean else 'bas'}: {value:,.2f} vs moy {mean:,.2f}"
    else:
        return f"Unusual: {value:,.2f} vs avg {mean:,.2f}" if not is_fr else f"Inhabituel: {value:,.2f} vs moy {mean:,.2f}"

def generate_sample_invoices():
    np.random.seed(42)
    n = 100
    amounts = list(np.random.normal(1500, 400, n-8)) + [18500, 22000, 15, 8, 19800, 25, 16500, 12]
    quantities = list(np.random.randint(1, 25, n-8)) + [180, 250, 1, 1, 200, 1, 150, 1]
    return pd.DataFrame({
        'Invoice_ID': [f'INV-{1000+i}' for i in range(n)],
        'Client': np.random.choice(['Acme Corp', 'TechStart', 'Global Svc', 'Local Shop', 'Big Corp'], n),
        'Amount': amounts,
        'Quantity': quantities,
        'Date': pd.date_range('2024-01-01', periods=n, freq='D').strftime('%Y-%m-%d').tolist()
    })

def generate_sample_expenses():
    np.random.seed(43)
    n = 80
    amounts = list(np.random.normal(280, 120, n-6)) + [5800, 7200, 5, 3, 6500, 8]
    return pd.DataFrame({
        'Expense_ID': [f'EXP-{2000+i}' for i in range(n)],
        'Category': np.random.choice(['Travel', 'Office', 'Software', 'Marketing'], n),
        'Vendor': np.random.choice(['Amazon', 'Office Depot', 'Google', 'Airlines'], n),
        'Amount': amounts,
        'Date': pd.date_range('2024-01-01', periods=n, freq='D').strftime('%Y-%m-%d').tolist()
    })

def generate_sample_payroll():
    np.random.seed(44)
    n = 50
    salaries = list(np.random.normal(5200, 800, n-5)) + [28000, 32000, 450, 380, 26000]
    hours = list(np.random.normal(160, 12, n-5)) + [280, 310, 35, 42, 260]
    bonuses = list(np.random.normal(400, 150, n-5)) + [8500, 12000, 0, 0, 9000]
    return pd.DataFrame({
        'Employee_ID': [f'EMP-{100+i}' for i in range(n)],
        'Department': np.random.choice(['Sales', 'Engineering', 'HR', 'Finance'], n),
        'Salary': salaries,
        'Hours': hours,
        'Bonus': bonuses
    })

def generate_sample_inventory():
    np.random.seed(45)
    n = 60
    quantities = list(np.random.randint(80, 400, n-6)) + [5500, 8200, 2, 1, 6800, 3]
    unit_costs = list(np.random.normal(28, 8, n-6)) + [380, 520, 2, 1, 450, 3]
    df = pd.DataFrame({
        'SKU': [f'SKU-{3000+i}' for i in range(n)],
        'Product': np.random.choice(['Widget A', 'Gadget B', 'Tool C', 'Part D'], n),
        'Quantity': quantities,
        'Unit_Cost': unit_costs,
    })
    df['Total_Value'] = df['Quantity'] * df['Unit_Cost']
    return df

# Header
st.markdown(f'<div class="main-header"><h1> {t["title"]}</h1><p>{t["subtitle"]}</p></div>', unsafe_allow_html=True)
st.markdown(f'<div class="demo-badge">{t["demo_notice"]}</div>', unsafe_allow_html=True)

# Sidebar buttons
with st.sidebar:
    st.markdown("---")
    st.markdown(f'<p class="sidebar-title">{t["sample_title"]}</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        btn_inv = st.button(t['sample_invoices'], use_container_width=True, type="primary")
        btn_pay = st.button(t['sample_payroll'], use_container_width=True, type="primary")
    with col2:
        btn_exp = st.button(t['sample_expenses'], use_container_width=True, type="primary")
        btn_inv2 = st.button(t['sample_inventory'], use_container_width=True, type="primary")
    
    if btn_inv:
        st.session_state['sample'] = 'invoices'
    elif btn_exp:
        st.session_state['sample'] = 'expenses'
    elif btn_pay:
        st.session_state['sample'] = 'payroll'
    elif btn_inv2:
        st.session_state['sample'] = 'inventory'

# Load data
df = None
name = ""
if 'sample' in st.session_state:
    s = st.session_state['sample']
    if s == 'invoices':
        df = generate_sample_invoices()
        name = "Invoices" if not is_fr else "Factures"
    elif s == 'expenses':
        df = generate_sample_expenses()
        name = "Expenses" if not is_fr else "Dépenses"
    elif s == 'payroll':
        df = generate_sample_payroll()
        name = "Payroll" if not is_fr else "Paie"
    elif s == 'inventory':
        df = generate_sample_inventory()
        name = "Inventory" if not is_fr else "Inventaire"

if df is not None:
    st.subheader(f"{t['data_preview']}  {name}")
    st.dataframe(df.head(10), use_container_width=True, height=280)
    st.caption(f"{'Showing' if not is_fr else 'Affichage de'} 10 / {len(df)}")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    st.markdown("---")
    st.subheader(t['results'])
    
    results = df.copy()
    results['Anomaly_Score'] = 0.0
    results['Anomaly_Level'] = t['normal']
    results['Anomaly_Explanation'] = ""
    
    for idx in range(len(df)):
        row_exp = []
        max_score = 0
        for col in numeric_cols:
            mean = df[col].mean()
            std = df[col].std()
            if std > 0:
                z = abs((df[col].iloc[idx] - mean) / std)
                if z > max_score:
                    max_score = z
                if z > 1.8:
                    row_exp.append(f"[{col}] " + get_explanation(df[col].iloc[idx], mean, std, col, is_fr))
        results.loc[idx, 'Anomaly_Score'] = max_score
        results.loc[idx, 'Anomaly_Explanation'] = " | ".join(row_exp) if row_exp else ""
    
    results.loc[results['Anomaly_Score'] > 3.0, 'Anomaly_Level'] = t['critical']
    results.loc[(results['Anomaly_Score'] > 2.5) & (results['Anomaly_Score'] <= 3.0), 'Anomaly_Level'] = t['high']
    results.loc[(results['Anomaly_Score'] > 2.0) & (results['Anomaly_Score'] <= 2.5), 'Anomaly_Level'] = t['medium']
    results.loc[(results['Anomaly_Score'] > 1.8) & (results['Anomaly_Score'] <= 2.0), 'Anomaly_Level'] = t['low']
    
    anomalies = results[results['Anomaly_Level'] != t['normal']].sort_values('Anomaly_Score', ascending=False)
    
    n_crit = len(anomalies[anomalies['Anomaly_Level'] == t['critical']])
    n_high = len(anomalies[anomalies['Anomaly_Level'] == t['high']])
    n_med = len(anomalies[anomalies['Anomaly_Level'] == t['medium']])
    n_low = len(anomalies[anomalies['Anomaly_Level'] == t['low']])
    n_tot = len(anomalies)
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(f'<div class="stat-card stat-critical"><div style="font-size:2rem;font-weight:bold;color:#dc2626;">{n_crit}</div><div> {t["critical"]}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card stat-high"><div style="font-size:2rem;font-weight:bold;color:#ef4444;">{n_high}</div><div> {t["high"]}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card stat-medium"><div style="font-size:2rem;font-weight:bold;color:#f59e0b;">{n_med}</div><div> {t["medium"]}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card stat-low"><div style="font-size:2rem;font-weight:bold;color:#22c55e;">{n_low}</div><div> {t["low"]}</div></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="stat-card" style="border-color:#667eea;"><div style="font-size:2rem;font-weight:bold;color:#667eea;">{n_tot}</div><div> Total</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if n_tot > 0:
        disp = anomalies.copy()
        disp['Anomaly_Score'] = disp['Anomaly_Score'].round(2)
        disp = disp.rename(columns={'Anomaly_Level': t['level'], 'Anomaly_Score': t['score'], 'Anomaly_Explanation': t['explanation']})
        
        def color_row(row):
            lv = row[t['level']]
            if lv == t['critical']:
                return ['background-color: #fee2e2;'] * len(row)
            elif lv == t['high']:
                return ['background-color: #fef2f2;'] * len(row)
            elif lv == t['medium']:
                return ['background-color: #fffbeb;'] * len(row)
            elif lv == t['low']:
                return ['background-color: #f0fdf4;'] * len(row)
            return [''] * len(row)
        
        def color_lv(val):
            if val == t['critical']:
                return 'background-color:#dc2626;color:white;font-weight:bold;'
            elif val == t['high']:
                return 'background-color:#ef4444;color:white;font-weight:bold;'
            elif val == t['medium']:
                return 'background-color:#f59e0b;color:white;font-weight:bold;'
            elif val == t['low']:
                return 'background-color:#22c55e;color:white;font-weight:bold;'
            return ''
        
        styled = disp.style.apply(color_row, axis=1).applymap(color_lv, subset=[t['level']])
        st.dataframe(styled, use_container_width=True, height=500)
        
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as w:
            disp.to_excel(w, index=False, sheet_name='Anomalies')
        out.seek(0)
        st.download_button(t['download_excel'], out, f"aynalyxai_{name.lower()}.xlsx", type="primary")
    
    st.markdown(f'''
    <div class="cta-box">
        <h3> {t['get_full']}</h3>
        <p style="color:#555;">{t['full_features']}</p>
        <a href="https://mubsira.gumroad.com/l/aynalyxai" target="_blank" class="cta-button">
             {'Get AynalyxAI Pro  $79' if not is_fr else 'Obtenir AynalyxAI Pro  79 $'}
        </a>
    </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown(f'''
    <div style="text-align:center;padding:4rem 2rem;background:#f8fafc;border-radius:16px;margin-top:2rem;">
        <div style="font-size:4rem;"></div>
        <h2>{t['welcome_title']}</h2>
        <p style="color:#64748b;">{t['welcome_text']}</p>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div style="text-align:center;color:#94a3b8;">© 2025 Mubsira Analytics | <a href="https://mubsira.gumroad.com/l/aynalyxai" style="color:#667eea;">Get Full Version</a></div>', unsafe_allow_html=True)
