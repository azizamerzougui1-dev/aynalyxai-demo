# AynalyxAI Demo - Streamlit Cloud Version
# Sample data only - no file upload

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo

# Page config - WIDE layout for better visibility
st.set_page_config(
    page_title="AynalyxAI Demo",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for wider sidebar and colored results
st.markdown("""
<style>
    /* Wider sidebar */
    [data-testid="stSidebar"] {
        min-width: 320px;
        max-width: 400px;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }
    
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Demo notice */
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
    
    /* Sample buttons styling */
    .sample-btn-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin: 1rem 0;
    }
    
    /* Anomaly level colors - matching real app */
    .anomaly-critical {
        background-color: #dc2626 !important;
        color: white !important;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    .anomaly-high {
        background-color: #ef4444 !important;
        color: white !important;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    .anomaly-medium {
        background-color: #f59e0b !important;
        color: white !important;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    .anomaly-low {
        background-color: #22c55e !important;
        color: white !important;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    /* Results table styling */
    .results-container {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
    }
    
    /* Stats cards */
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
    
    /* Sidebar title */
    .sidebar-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1e293b;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    /* CTA Box */
    .cta-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 2px solid #667eea;
        margin-top: 2rem;
    }
    
    .cta-box h3 {
        color: #667eea;
        margin-bottom: 0.5rem;
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
    
    /* Hide file uploader completely */
    .stFileUploader {
        display: none !important;
    }
    
    /* Aggregation box styling */
    .agg-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 2px solid #0ea5e9;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .agg-box h4 {
        color: #0369a1;
        margin: 0 0 1rem 0;
    }
    
    /* Scrollable result table with visible scrollbar */
    [data-testid="stDataFrame"] > div {
        max-height: 450px;
        overflow-y: auto !important;
        overflow-x: auto !important;
    }
    
    [data-testid="stDataFrame"] > div::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    [data-testid="stDataFrame"] > div::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 5px;
    }
    
    [data-testid="stDataFrame"] > div::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 5px;
    }
    
    [data-testid="stDataFrame"] > div::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
""", unsafe_allow_html=True)

# Language selection in sidebar
with st.sidebar:
    st.markdown('<p class="sidebar-title">🌐 Language / Langue</p>', unsafe_allow_html=True)
    lang = st.selectbox("", ["English", "Français"], label_visibility="collapsed")
    is_fr = lang == "Français"

# Translations
t = {
    "title": "AynalyxAI Demo" if not is_fr else "Démo AynalyxAI",
    "subtitle": "AI-Powered Anomaly Detection" if not is_fr else "Détection d'Anomalies par IA",
    "demo_notice": "🎯 FREE DEMO — Try with our sample data below!" if not is_fr else "🎯 DÉMO GRATUITE — Essayez avec nos données d'exemple ci-dessous!",
    "sample_title": "📊 Select Sample Data" if not is_fr else "📊 Sélectionner des Données",
    "sample_invoices": "📄 Invoices" if not is_fr else "📄 Factures",
    "sample_expenses": "💰 Expenses" if not is_fr else "💰 Dépenses",
    "sample_payroll": "👥 Payroll" if not is_fr else "👥 Paie",
    "sample_inventory": "📦 Inventory" if not is_fr else "📦 Inventaire",
    "run_analysis": "🔍 Run Anomaly Detection" if not is_fr else "🔍 Lancer la Détection",
    "results": "🎯 Detection Results" if not is_fr else "🎯 Résultats de Détection",
    "anomalies_found": "anomalies detected" if not is_fr else "anomalies détectées",
    "download_excel": "📥 Download Results (Excel)" if not is_fr else "📥 Télécharger (Excel)",
    "data_preview": "📋 Data Preview" if not is_fr else "📋 Aperçu des Données",
    "critical": "CRITICAL" if not is_fr else "CRITIQUE",
    "high": "HIGH" if not is_fr else "ÉLEVÉ",
    "medium": "MEDIUM" if not is_fr else "MOYEN", 
    "low": "LOW" if not is_fr else "FAIBLE",
    "normal": "Normal" if not is_fr else "Normal",
    "explanation": "Explanation" if not is_fr else "Explication",
    "level": "Level" if not is_fr else "Niveau",
    "ai_score": "AI Score" if not is_fr else "Score IA",
    "deviation_score": "Deviation" if not is_fr else "Déviation",
    "welcome_title": "👈 Select Sample Data to Begin" if not is_fr else "👈 Sélectionnez des Données pour Commencer",
    "welcome_text": "Click one of the 4 sample data buttons in the sidebar to see the AI anomaly detection in action." if not is_fr else "Cliquez sur l'un des 4 boutons de données dans la barre latérale pour voir la détection d'anomalies en action.",
    "get_full": "Get Full Desktop Version" if not is_fr else "Obtenir la Version Complète",
    "full_features": "The full version includes: Advanced AI (Isolation Forest), Data Aggregation, Custom Ratios, 100% Offline Privacy, Unlimited Files" if not is_fr else "La version complète inclut: IA Avancée (Isolation Forest), Agrégation, Ratios Personnalisés, 100% Hors-ligne, Fichiers Illimités",
    "security_title": "⚠️ Security Notice" if not is_fr else "⚠️ Avis de Sécurité",
    "security_text": "**Windows may show a security warning** when you download and run the app. This is completely normal for new software from independent developers. AynalyxAI is safe and built with standard open-source tools. To proceed: click **'More info'** → **'Run anyway'**. Your antivirus may also scan the file — this is normal." if not is_fr else "**Windows peut afficher un avertissement de sécurité** lorsque vous téléchargez et lancez l'application. C'est tout à fait normal pour les nouveaux logiciels de développeurs indépendants. AynalyxAI est sécuritaire et construit avec des outils open-source standards. Pour continuer : cliquez sur **« Plus d'infos »** → **« Exécuter quand même »**. Votre antivirus peut aussi scanner le fichier — c'est normal.",
    "aggregation_title": "📊 Data Aggregation (Optional)" if not is_fr else "📊 Agrégation des Données (Optionnel)",
    "aggregation_help": "Group your data by a column before analysis. This lets you detect anomalies at the group level (e.g., per vendor, per department)." if not is_fr else "Regroupez vos données par une colonne avant l'analyse. Cela permet de détecter les anomalies au niveau du groupe (ex: par fournisseur, par département).",
    "group_by": "Group by" if not is_fr else "Regrouper par",
    "no_aggregation": "No aggregation (analyze raw rows)" if not is_fr else "Pas d'agrégation (analyser les lignes brutes)",
    "aggregation_method": "Aggregation method" if not is_fr else "Méthode d'agrégation",
    "sum": "Sum" if not is_fr else "Somme",
    "mean": "Average" if not is_fr else "Moyenne",
    "count": "Count" if not is_fr else "Comptage",
}

# Explanation templates - clean, no column prefix
def get_explanation(value, mean, std, col_name, is_fr):
    z_score = abs((value - mean) / std) if std > 0 else 0
    pct_diff = ((value - mean) / mean * 100) if mean != 0 else 0
    
    if z_score > 3:
        if value > mean:
            return f"{col_name}: {abs(pct_diff):.0f}% {'above average' if not is_fr else 'au-dessus de la moyenne'}"
        else:
            return f"{col_name}: {abs(pct_diff):.0f}% {'below average' if not is_fr else 'en-dessous de la moyenne'}"
    elif z_score > 2.5:
        if value > mean:
            return f"{col_name}: {'exceeds avg by' if not is_fr else 'dépasse moy de'} {abs(pct_diff):.0f}%"
        else:
            return f"{col_name}: {'below avg by' if not is_fr else 'sous moy de'} {abs(pct_diff):.0f}%"
    elif z_score > 2:
        return f"{col_name}: {'+' if pct_diff > 0 else ''}{pct_diff:.0f}% {'vs avg' if not is_fr else 'vs moy'}"
    elif z_score > 1.5:
        return f"{col_name}: {'+' if pct_diff > 0 else ''}{pct_diff:.0f}%"
    else:
        return ""

# Sample data generators with realistic anomalies
def generate_sample_invoices():
    np.random.seed(42)
    n = 100
    
    # Normal data
    amounts = np.random.normal(1500, 400, n-8)
    quantities = np.random.randint(1, 25, n-8)
    
    # Add clear anomalies
    anomaly_amounts = [18500, 22000, 15, 8, 19800, 25, 16500, 12]  # High and low anomalies
    anomaly_quantities = [180, 250, 1, 1, 200, 1, 150, 1]
    
    all_amounts = np.concatenate([amounts, anomaly_amounts])
    all_quantities = np.concatenate([quantities, anomaly_quantities])
    
    data = {
        'Invoice_ID': [f'INV-{1000+i}' for i in range(n)],
        'Client': np.random.choice(['Acme Corp', 'TechStart Inc', 'Global Services', 'Local Shop', 'Big Enterprise', 'Quick Mart', 'Pro Solutions'], n),
        'Amount': all_amounts,
        'Quantity': all_quantities,
        'Date': pd.date_range('2024-01-01', periods=n, freq='D').strftime('%Y-%m-%d').tolist()
    }
    return pd.DataFrame(data)

def generate_sample_expenses():
    np.random.seed(43)
    n = 80
    
    amounts = np.random.normal(280, 120, n-6)
    anomaly_amounts = [5800, 7200, 5, 3, 6500, 8]  # Anomalies
    all_amounts = np.concatenate([amounts, anomaly_amounts])
    
    data = {
        'Expense_ID': [f'EXP-{2000+i}' for i in range(n)],
        'Category': np.random.choice(['Travel', 'Office Supplies', 'Software', 'Marketing', 'Utilities', 'Meals'], n),
        'Vendor': np.random.choice(['Amazon', 'Office Depot', 'Google Ads', 'Airlines Inc', 'Power Co', 'Staples'], n),
        'Amount': all_amounts,
        'Date': pd.date_range('2024-01-01', periods=n, freq='D').strftime('%Y-%m-%d').tolist()
    }
    return pd.DataFrame(data)

def generate_sample_payroll():
    np.random.seed(44)
    n = 50
    
    salaries = np.random.normal(5200, 800, n-5)
    hours = np.random.normal(160, 12, n-5)
    bonuses = np.random.normal(400, 150, n-5)
    
    # Anomalies
    anomaly_salaries = [28000, 32000, 450, 380, 26000]
    anomaly_hours = [280, 310, 35, 42, 260]
    anomaly_bonuses = [8500, 12000, 0, 0, 9000]
    
    data = {
        'Employee_ID': [f'EMP-{100+i}' for i in range(n)],
        'Department': np.random.choice(['Sales', 'Engineering', 'HR', 'Marketing', 'Finance', 'Operations'], n),
        'Salary': np.concatenate([salaries, anomaly_salaries]),
        'Hours_Worked': np.concatenate([hours, anomaly_hours]),
        'Bonus': np.concatenate([bonuses, anomaly_bonuses])
    }
    return pd.DataFrame(data)

def generate_sample_inventory():
    np.random.seed(45)
    n = 60
    
    quantities = np.random.randint(80, 400, n-6)
    unit_costs = np.random.normal(28, 8, n-6)
    
    # Anomalies
    anomaly_qty = [5500, 8200, 2, 1, 6800, 3]
    anomaly_cost = [380, 520, 2, 1, 450, 3]
    
    data = {
        'SKU': [f'SKU-{3000+i}' for i in range(n)],
        'Product': np.random.choice(['Widget A', 'Gadget B', 'Tool C', 'Part D', 'Supply E', 'Component F'], n),
        'Quantity': np.concatenate([quantities, anomaly_qty]),
        'Unit_Cost': np.concatenate([unit_costs, anomaly_cost]),
    }
    df = pd.DataFrame(data)
    df['Total_Value'] = df['Quantity'] * df['Unit_Cost']
    return df

# Header
st.markdown(f"""
<div class="main-header">
    <h1>🔬 {t['title']}</h1>
    <p>{t['subtitle']}</p>
</div>
""", unsafe_allow_html=True)

# Demo notice
st.markdown(f'<div class="demo-badge">{t["demo_notice"]}</div>', unsafe_allow_html=True)

# Sidebar - Sample Data Selection (NO FILE UPLOAD)
with st.sidebar:
    st.markdown("---")
    st.markdown(f'<p class="sidebar-title">{t["sample_title"]}</p>', unsafe_allow_html=True)
    
    # 2x2 grid of sample buttons
    col1, col2 = st.columns(2)
    
    with col1:
        btn_invoices = st.button(t['sample_invoices'], use_container_width=True, type="primary")
        btn_payroll = st.button(t['sample_payroll'], use_container_width=True, type="primary")
    
    with col2:
        btn_expenses = st.button(t['sample_expenses'], use_container_width=True, type="primary")
        btn_inventory = st.button(t['sample_inventory'], use_container_width=True, type="primary")
    
    # Track which sample is selected
    if btn_invoices:
        st.session_state['sample_type'] = 'invoices'
        st.session_state['run_clicked'] = False
    elif btn_expenses:
        st.session_state['sample_type'] = 'expenses'
        st.session_state['run_clicked'] = False
    elif btn_payroll:
        st.session_state['sample_type'] = 'payroll'
        st.session_state['run_clicked'] = False
    elif btn_inventory:
        st.session_state['sample_type'] = 'inventory'
        st.session_state['run_clicked'] = False

# Load data based on selection
df = None
data_name = ""
if 'sample_type' in st.session_state:
    sample = st.session_state['sample_type']
    if sample == 'invoices':
        df = generate_sample_invoices()
        data_name = "Invoices" if not is_fr else "Factures"
    elif sample == 'expenses':
        df = generate_sample_expenses()
        data_name = "Expenses" if not is_fr else "Dépenses"
    elif sample == 'payroll':
        df = generate_sample_payroll()
        data_name = "Payroll" if not is_fr else "Paie"
    elif sample == 'inventory':
        df = generate_sample_inventory()
        data_name = "Inventory" if not is_fr else "Inventaire"

# Main content
if df is not None:
    # Data preview
    st.subheader(f"{t['data_preview']} — {data_name}")
    st.dataframe(df.head(10), use_container_width=True, height=300)
    st.caption(f"{'Affichage de 10 sur' if is_fr else 'Showing 10 of'} {len(df)} {'lignes' if is_fr else 'rows'}")
    
    # Get numeric and text columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    st.markdown("---")
    
    # Aggregation Options
    st.markdown(f"""
    <div class="agg-box">
        <h4>📊 {t['aggregation_title']}</h4>
        <p style="color: #0369a1; margin: 0; font-size: 0.9rem;">{t['aggregation_help']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        group_options = [t['no_aggregation']] + text_cols
        group_by = st.selectbox(t['group_by'], group_options, key="group_by_select")
    
    with col2:
        agg_method = st.selectbox(
            t['aggregation_method'], 
            [t['sum'], t['mean'], t['count']], 
            key="agg_method_select"
        )
    
    # Map aggregation method
    agg_func_map = {t['sum']: 'sum', t['mean']: 'mean', t['count']: 'count'}
    agg_func = agg_func_map.get(agg_method, 'sum')
    
    # Run button
    st.markdown("<br>", unsafe_allow_html=True)
    run_analysis = st.button(t['run_analysis'], type="primary", use_container_width=True)
    
    if run_analysis:
        st.session_state['run_clicked'] = True
    
    # Run analysis when button is clicked
    if st.session_state.get('run_clicked', False) and numeric_cols:
        st.markdown("---")
        st.subheader(t['results'])
        
        with st.spinner("🔍 " + ("Analyse en cours..." if is_fr else "Analyzing...")):
            # Apply aggregation if selected
            if group_by != t['no_aggregation']:
                # Aggregate the data
                if agg_func == 'count':
                    analysis_df = df.groupby(group_by).size().reset_index(name='Count')
                    numeric_cols = ['Count']
                else:
                    analysis_df = df.groupby(group_by)[numeric_cols].agg(agg_func).reset_index()
                
                # Round aggregated values to 2 decimals
                for col in numeric_cols:
                    if col in analysis_df.columns:
                        analysis_df[col] = analysis_df[col].round(2)
                
                original_columns = analysis_df.columns.tolist()
                st.info(f"📊 {'Données agrégées par' if is_fr else 'Data aggregated by'} **{group_by}** ({agg_method}) — **{len(analysis_df)}** {'groupes' if is_fr else 'groups'}")
            else:
                analysis_df = df.copy()
                # Round numeric columns to 2 decimals
                for col in numeric_cols:
                    if col in analysis_df.columns:
                        analysis_df[col] = analysis_df[col].round(2)
                original_columns = df.columns.tolist()
            
            # Perform anomaly detection
            results = analysis_df.copy()
            results['Deviation_Score'] = 0.0
            results['AI_Score'] = 0.0
            results['Anomaly_Level'] = t['normal']
            results['Anomaly_Explanation'] = ""
            
            # Calculate anomaly scores for each numeric column
            for idx in range(len(analysis_df)):
                row_explanations = []
                max_z_score = 0
                total_score = 0
                score_count = 0
                
                for col in numeric_cols:
                    if col not in analysis_df.columns:
                        continue
                    mean = analysis_df[col].mean()
                    std = analysis_df[col].std()
                    if std > 0:
                        z_score = abs((analysis_df[col].iloc[idx] - mean) / std)
                        if z_score > max_z_score:
                            max_z_score = z_score
                        total_score += z_score
                        score_count += 1
                        if z_score > 1.5:  # Lower threshold to show more anomalies
                            explanation = get_explanation(analysis_df[col].iloc[idx], mean, std, col, is_fr)
                            if explanation:
                                row_explanations.append(explanation)
                
                # Deviation Score = max Z-score (statistical deviation) - round to 2 decimals
                results.loc[idx, 'Deviation_Score'] = round(max_z_score, 2)
                # AI Score = weighted combination (simulating ML model output) - round to 2 decimals
                ai_score = min(100, max_z_score * 25) if max_z_score > 1.5 else max_z_score * 10
                results.loc[idx, 'AI_Score'] = round(ai_score, 2)
                results.loc[idx, 'Anomaly_Explanation'] = " | ".join(row_explanations) if row_explanations else ""
            
            # Classify anomaly levels based on Deviation Score - adjusted thresholds
            results.loc[results['Deviation_Score'] > 3.0, 'Anomaly_Level'] = t['critical']
            results.loc[(results['Deviation_Score'] > 2.3) & (results['Deviation_Score'] <= 3.0), 'Anomaly_Level'] = t['high']
            results.loc[(results['Deviation_Score'] > 1.8) & (results['Deviation_Score'] <= 2.3), 'Anomaly_Level'] = t['medium']
            results.loc[(results['Deviation_Score'] > 1.5) & (results['Deviation_Score'] <= 1.8), 'Anomaly_Level'] = t['low']
            
            # Sort results by Deviation Score (anomalies first, then normal)
            results_sorted = results.sort_values('Deviation_Score', ascending=False)
            
            # Count anomalies by level
            anomalies = results_sorted[results_sorted['Anomaly_Level'] != t['normal']]
            n_critical = len(anomalies[anomalies['Anomaly_Level'] == t['critical']])
            n_high = len(anomalies[anomalies['Anomaly_Level'] == t['high']])
            n_medium = len(anomalies[anomalies['Anomaly_Level'] == t['medium']])
            n_low = len(anomalies[anomalies['Anomaly_Level'] == t['low']])
            n_total = len(anomalies)
            n_normal = len(results_sorted) - n_total
            
            # Statistics cards
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"""
                <div class="stat-card stat-critical">
                    <div style="font-size: 2rem; font-weight: bold; color: #dc2626;">{n_critical}</div>
                    <div style="color: #666;">🔴 {t['critical']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="stat-card stat-high">
                    <div style="font-size: 2rem; font-weight: bold; color: #ef4444;">{n_high}</div>
                    <div style="color: #666;">🟠 {t['high']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="stat-card stat-medium">
                    <div style="font-size: 2rem; font-weight: bold; color: #f59e0b;">{n_medium}</div>
                    <div style="color: #666;">🟡 {t['medium']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="stat-card stat-low">
                    <div style="font-size: 2rem; font-weight: bold; color: #22c55e;">{n_low}</div>
                    <div style="color: #666;">🟢 {t['low']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col5:
                st.markdown(f"""
                <div class="stat-card" style="border-color: #667eea;">
                    <div style="font-size: 2rem; font-weight: bold; color: #667eea;">{n_total}</div>
                    <div style="color: #666;">📊 Total</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Show summary - ALL ROWS will be displayed
            st.info(f"📊 {'Affichage de toutes les' if is_fr else 'Showing all'} **{len(results_sorted)}** {'lignes' if is_fr else 'rows'} — **{n_total}** {'anomalies détectées' if is_fr else 'anomalies detected'}, **{n_normal}** {'normales' if is_fr else 'normal'}")
            
            # Create display dataframe with ALL rows and ALL columns
            display_df = results_sorted.reset_index(drop=True).copy()
            
            # Reorder columns: original columns first, then result columns
            result_columns = ['Anomaly_Level', 'Deviation_Score', 'AI_Score', 'Anomaly_Explanation']
            ordered_columns = [c for c in original_columns if c in display_df.columns] + result_columns
            display_df = display_df[ordered_columns]
            
            # Round all numeric columns to 2 decimals for display
            for col in display_df.select_dtypes(include=[np.number]).columns:
                display_df[col] = display_df[col].round(2)
            
            # Rename only the result columns for display
            col_rename = {
                'Anomaly_Level': t['level'],
                'Deviation_Score': t['deviation_score'],
                'AI_Score': t['ai_score'],
                'Anomaly_Explanation': t['explanation']
            }
            display_df = display_df.rename(columns=col_rename)
            
            # Apply color styling function
            def color_level(val):
                if val == t['critical']:
                    return 'background-color: #dc2626; color: white; font-weight: bold;'
                elif val == t['high']:
                    return 'background-color: #ef4444; color: white; font-weight: bold;'
                elif val == t['medium']:
                    return 'background-color: #f59e0b; color: white; font-weight: bold;'
                elif val == t['low']:
                    return 'background-color: #22c55e; color: white; font-weight: bold;'
                return ''
            
            def color_row(row):
                level = row[t['level']]
                if level == t['critical']:
                    return ['background-color: #fee2e2;'] * len(row)
                elif level == t['high']:
                    return ['background-color: #fef2f2;'] * len(row)
                elif level == t['medium']:
                    return ['background-color: #fffbeb;'] * len(row)
                elif level == t['low']:
                    return ['background-color: #f0fdf4;'] * len(row)
                return [''] * len(row)
            
            # Style and display ALL results
            styled_df = display_df.style.apply(color_row, axis=1).map(
                color_level, subset=[t['level']]
            ).format(precision=2)
            
            # Display ALL rows with scrollbar (fixed height)
            st.dataframe(styled_df, use_container_width=True, height=450)
            
            # Download button with formatted Excel
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Create formatted Excel file
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                display_df.to_excel(writer, index=False, sheet_name='Results', startrow=0)
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Results']
                
                # Define color fills for each level
                fill_critical = PatternFill(start_color='DC2626', end_color='DC2626', fill_type='solid')
                fill_critical_row = PatternFill(start_color='FEE2E2', end_color='FEE2E2', fill_type='solid')
                fill_high = PatternFill(start_color='EF4444', end_color='EF4444', fill_type='solid')
                fill_high_row = PatternFill(start_color='FEF2F2', end_color='FEF2F2', fill_type='solid')
                fill_medium = PatternFill(start_color='F59E0B', end_color='F59E0B', fill_type='solid')
                fill_medium_row = PatternFill(start_color='FFFBEB', end_color='FFFBEB', fill_type='solid')
                fill_low = PatternFill(start_color='22C55E', end_color='22C55E', fill_type='solid')
                fill_low_row = PatternFill(start_color='F0FDF4', end_color='F0FDF4', fill_type='solid')
                fill_header = PatternFill(start_color='667EEA', end_color='667EEA', fill_type='solid')
                
                font_white = Font(color='FFFFFF', bold=True)
                font_header = Font(color='FFFFFF', bold=True, size=11)
                thin_border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
                
                # Style header row
                for col_num, cell in enumerate(worksheet[1], 1):
                    cell.fill = fill_header
                    cell.font = font_header
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    cell.border = thin_border
                
                # Find the Level column index
                level_col_idx = None
                for idx, col in enumerate(display_df.columns, 1):
                    if col == t['level']:
                        level_col_idx = idx
                        break
                
                # Apply conditional formatting to each row
                for row_num in range(2, len(display_df) + 2):
                    level_value = worksheet.cell(row=row_num, column=level_col_idx).value if level_col_idx else None
                    
                    # Determine row fill based on level
                    row_fill = None
                    level_fill = None
                    if level_value == t['critical']:
                        row_fill = fill_critical_row
                        level_fill = fill_critical
                    elif level_value == t['high']:
                        row_fill = fill_high_row
                        level_fill = fill_high
                    elif level_value == t['medium']:
                        row_fill = fill_medium_row
                        level_fill = fill_medium
                    elif level_value == t['low']:
                        row_fill = fill_low_row
                        level_fill = fill_low
                    
                    # Apply formatting to all cells in row
                    for col_num in range(1, len(display_df.columns) + 1):
                        cell = worksheet.cell(row=row_num, column=col_num)
                        cell.border = thin_border
                        cell.alignment = Alignment(vertical='center')
                        
                        if row_fill:
                            cell.fill = row_fill
                        
                        # Special formatting for Level column
                        if col_num == level_col_idx and level_fill:
                            cell.fill = level_fill
                            cell.font = font_white
                            cell.alignment = Alignment(horizontal='center', vertical='center')
                
                # Auto-fit column widths
                for col_num, column in enumerate(display_df.columns, 1):
                    max_length = len(str(column))
                    for row in worksheet.iter_rows(min_row=2, max_row=len(display_df) + 1, min_col=col_num, max_col=col_num):
                        for cell in row:
                            if cell.value:
                                max_length = max(max_length, len(str(cell.value)))
                    worksheet.column_dimensions[worksheet.cell(row=1, column=col_num).column_letter].width = min(50, max_length + 2)
                
                # Add auto-filter
                worksheet.auto_filter.ref = f"A1:{worksheet.cell(row=1, column=len(display_df.columns)).column_letter}{len(display_df) + 1}"
                
                # Freeze header row
                worksheet.freeze_panes = 'A2'
            
            output.seek(0)
            
            st.download_button(
                label=t['download_excel'],
                data=output,
                file_name=f"aynalyxai_{data_name.lower()}_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
        
        # CTA Box
        st.markdown(f"""
        <div class="cta-box">
            <h3>🚀 {t['get_full']}</h3>
            <p style="color: #555; font-size: 0.95rem;">{t['full_features']}</p>
            <a href="https://mubsira.gumroad.com/l/aynalyxai" target="_blank" class="cta-button">
                💎 {'Obtenir AynalyxAI Pro' if is_fr else 'Get AynalyxAI Pro'}
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # Security Notice
        st.markdown(f"""
        <div style="background: #fef3c7; border: 2px solid #f59e0b; border-radius: 12px; padding: 1rem 1.5rem; margin-top: 1.5rem;">
            <h4 style="color: #92400e; margin: 0 0 0.5rem 0; font-size: 1rem;">{t['security_title']}</h4>
            <p style="color: #78350f; margin: 0; font-size: 0.9rem; line-height: 1.5;">{t['security_text']}</p>
        </div>
        """, unsafe_allow_html=True)

else:
    # Welcome screen when no data selected
    st.markdown(f"""
    <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 16px; margin-top: 2rem;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">👈</div>
        <h2 style="color: #1e293b; margin-bottom: 1rem;">{t['welcome_title']}</h2>
        <p style="font-size: 1.1rem; color: #64748b; max-width: 500px; margin: 0 auto;">
            {t['welcome_text']}
        </p>
        <div style="margin-top: 2rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
            <span style="background: #667eea20; color: #667eea; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 500;">📄 {'Factures' if is_fr else 'Invoices'}</span>
            <span style="background: #667eea20; color: #667eea; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 500;">💰 {'Dépenses' if is_fr else 'Expenses'}</span>
            <span style="background: #667eea20; color: #667eea; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 500;">👥 {'Paie' if is_fr else 'Payroll'}</span>
            <span style="background: #667eea20; color: #667eea; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 500;">📦 {'Inventaire' if is_fr else 'Inventory'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94a3b8; padding: 1rem;">
    <p>© 2025 Mubsira Analytics | <a href="https://mubsira.gumroad.com/l/aynalyxai" target="_blank" style="color: #667eea;">Get Full Version</a></p>
</div>
""", unsafe_allow_html=True)
