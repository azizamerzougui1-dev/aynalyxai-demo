"""
AynalyxAI - Interactive Demo
Streamlit-based demo for the AynalyxAI anomaly detection tool.
Uses the same detection logic as the main application.
"""

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# Page config
st.set_page_config(
    page_title="AynalyxAI Demo",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0d9488;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    .highlight-box {
        background: linear-gradient(135deg, #f0fdfa 0%, #e0f2fe 100%);
        border-radius: 10px;
        padding: 1.5rem;
        border-left: 4px solid #0d9488;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }
    .stDataFrame {
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🔍 AynalyxAI Demo</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload any spreadsheet with headers. Get instant anomaly detection.</p>', unsafe_allow_html=True)

# Info box
st.markdown("""
<div class="highlight-box">
    <strong>💡 How it works:</strong> Upload an Excel or CSV file with headers. 
    Select numeric columns to analyze. Get a color-coded report showing unusual values, 
    with AI-generated explanations for each anomaly.
</div>
""", unsafe_allow_html=True)


def detect_anomalies(df: pd.DataFrame, numeric_cols: list) -> pd.DataFrame:
    """
    Detect anomalies using the same logic as the main AynalyxAI application.
    Uses Z-score based detection with multi-column analysis.
    
    Returns DataFrame with original columns + 4 analytics columns:
    - Anomaly_Level: Critical/High/Medium/Low/Normal
    - Anomaly_Deviation: Percentage deviation from normal
    - Anomaly_AI_Score: Composite anomaly score (0-100)
    - Anomaly_Explanation: Plain-language explanation
    """
    result_df = df.copy()
    n_rows = len(result_df)
    
    if n_rows == 0 or len(numeric_cols) == 0:
        result_df['Anomaly_Level'] = 'Normal'
        result_df['Anomaly_Deviation'] = 0.0
        result_df['Anomaly_AI_Score'] = 0.0
        result_df['Anomaly_Explanation'] = 'No numeric data to analyze'
        return result_df
    
    # Initialize score tracking
    composite_scores = np.zeros(n_rows)
    max_deviations = np.zeros(n_rows)
    anomaly_reasons = [[] for _ in range(n_rows)]
    
    # Analyze each numeric column
    for col in numeric_cols:
        if col not in result_df.columns:
            continue
            
        values = pd.to_numeric(result_df[col], errors='coerce')
        
        # Skip if all NaN or constant
        if values.isna().all() or values.std() == 0:
            continue
        
        mean_val = values.mean()
        std_val = values.std()
        
        # Handle zero std (constant values)
        if std_val == 0 or pd.isna(std_val):
            continue
        
        # Calculate Z-scores
        z_scores = np.abs((values - mean_val) / std_val)
        z_scores = z_scores.fillna(0)
        
        # Calculate percentage deviation from mean
        with np.errstate(divide='ignore', invalid='ignore'):
            pct_deviation = np.abs((values - mean_val) / mean_val) * 100
            pct_deviation = pct_deviation.fillna(0)
            pct_deviation = np.where(np.isinf(pct_deviation), 0, pct_deviation)
        
        # Track maximum deviation across columns
        max_deviations = np.maximum(max_deviations, pct_deviation)
        
        # Add to composite score (weighted by Z-score severity)
        composite_scores += z_scores * 10  # Scale factor
        
        # Track reasons for high Z-scores
        for idx in range(n_rows):
            z = z_scores.iloc[idx] if hasattr(z_scores, 'iloc') else z_scores[idx]
            if z > 2:  # Significant deviation
                val = values.iloc[idx] if hasattr(values, 'iloc') else values[idx]
                direction = "above" if val > mean_val else "below"
                anomaly_reasons[idx].append(f"{col}: {z:.1f}σ {direction} mean")
    
    # Normalize composite score to 0-100 range
    if composite_scores.max() > 0:
        ai_scores = (composite_scores / composite_scores.max()) * 100
    else:
        ai_scores = np.zeros(n_rows)
    
    # Determine anomaly levels based on AI score
    levels = []
    for score in ai_scores:
        if score >= 80:
            levels.append('Critical')
        elif score >= 60:
            levels.append('High')
        elif score >= 40:
            levels.append('Medium')
        elif score >= 20:
            levels.append('Low')
        else:
            levels.append('Normal')
    
    # Generate explanations
    explanations = []
    for idx, reasons in enumerate(anomaly_reasons):
        if not reasons:
            explanations.append("Values within normal range")
        elif len(reasons) == 1:
            explanations.append(f"Unusual: {reasons[0]}")
        else:
            explanations.append(f"Multiple anomalies: {'; '.join(reasons[:3])}")
    
    # Add analytics columns to result
    result_df['Anomaly_Level'] = levels
    result_df['Anomaly_Deviation'] = np.round(max_deviations, 2)
    result_df['Anomaly_AI_Score'] = np.round(ai_scores, 1)
    result_df['Anomaly_Explanation'] = explanations
    
    # Sort by AI Score descending (most anomalous first)
    result_df = result_df.sort_values('Anomaly_AI_Score', ascending=False).reset_index(drop=True)
    
    return result_df


def style_anomaly_level(val):
    """Color-code the anomaly level column."""
    colors = {
        'Critical': 'background-color: #fecaca; color: #991b1b; font-weight: bold',
        'High': 'background-color: #fed7aa; color: #9a3412; font-weight: bold',
        'Medium': 'background-color: #fef08a; color: #854d0e',
        'Low': 'background-color: #d9f99d; color: #3f6212',
        'Normal': 'background-color: #bbf7d0; color: #166534'
    }
    return colors.get(val, '')


def style_ai_score(val):
    """Color-code the AI score column."""
    try:
        score = float(val)
        if score >= 80:
            return 'background-color: #fecaca; color: #991b1b; font-weight: bold'
        elif score >= 60:
            return 'background-color: #fed7aa; color: #9a3412'
        elif score >= 40:
            return 'background-color: #fef08a; color: #854d0e'
        elif score >= 20:
            return 'background-color: #d9f99d; color: #3f6212'
        else:
            return 'background-color: #bbf7d0; color: #166534'
    except:
        return ''


def to_excel(df):
    """Convert DataFrame to Excel bytes for download."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Anomaly Report')
    return output.getvalue()


# File upload section
st.markdown("### 📁 Upload Your File")
uploaded_file = st.file_uploader(
    "Drop your Excel or CSV file here",
    type=['xlsx', 'xls', 'csv'],
    help="File must have headers in the first row"
)

if uploaded_file:
    # Load the data
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Loaded **{uploaded_file.name}** — {len(df):,} rows × {len(df.columns)} columns")
        
        # Show data preview
        with st.expander("📋 Preview Raw Data", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)
        
        # Detect numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            st.warning("⚠️ No numeric columns detected. Please upload a file with numeric data.")
        else:
            st.markdown("### ⚙️ Select Columns to Analyze")
            
            # Column selection
            selected_cols = st.multiselect(
                "Choose numeric columns for anomaly detection:",
                options=numeric_cols,
                default=numeric_cols[:5] if len(numeric_cols) > 5 else numeric_cols,
                help="Select which columns to include in the multi-column anomaly analysis"
            )
            
            if selected_cols:
                # Run analysis button
                if st.button("🔍 Detect Anomalies", type="primary", use_container_width=True):
                    with st.spinner("Analyzing patterns across all selected columns..."):
                        # Run detection
                        results_df = detect_anomalies(df, selected_cols)
                        
                        # Store in session state
                        st.session_state['results'] = results_df
                        st.session_state['analyzed'] = True
        
        # Display results if available
        if st.session_state.get('analyzed') and 'results' in st.session_state:
            results_df = st.session_state['results']
            
            st.markdown("---")
            st.markdown("### 📊 Analysis Results")
            
            # Summary metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            level_counts = results_df['Anomaly_Level'].value_counts()
            
            with col1:
                critical = level_counts.get('Critical', 0)
                st.metric("🔴 Critical", critical)
            with col2:
                high = level_counts.get('High', 0)
                st.metric("🟠 High", high)
            with col3:
                medium = level_counts.get('Medium', 0)
                st.metric("🟡 Medium", medium)
            with col4:
                low = level_counts.get('Low', 0)
                st.metric("🟢 Low", low)
            with col5:
                normal = level_counts.get('Normal', 0)
                st.metric("✅ Normal", normal)
            
            st.markdown("---")
            
            # Reorder columns: original columns first, then analytics columns
            analytics_cols = ['Anomaly_Level', 'Anomaly_Deviation', 'Anomaly_AI_Score', 'Anomaly_Explanation']
            original_cols = [c for c in results_df.columns if c not in analytics_cols]
            ordered_cols = original_cols + analytics_cols
            results_display = results_df[ordered_cols]
            
            # Apply styling
            styled_df = results_display.style.applymap(
                style_anomaly_level, subset=['Anomaly_Level']
            ).applymap(
                style_ai_score, subset=['Anomaly_AI_Score']
            )
            
            # Display results table
            st.markdown("#### 📋 Detailed Results (Original Data → Analytics)")
            st.markdown("*Sorted by AI Score (highest anomalies first). Original columns on left, analytics on right.*")
            st.dataframe(styled_df, use_container_width=True, height=500)
            
            # Download button
            st.markdown("---")
            excel_data = to_excel(results_display)
            st.download_button(
                label="📥 Download Full Report (Excel)",
                data=excel_data,
                file_name=f"AynalyxAI_Report_{uploaded_file.name.rsplit('.', 1)[0]}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
        st.info("Make sure your file has headers in the first row and contains valid data.")

else:
    # Show sample/instructions when no file uploaded
    st.markdown("""
    <div style="background: #f9fafb; border-radius: 12px; padding: 2rem; text-align: center; border: 2px dashed #d1d5db;">
        <h3 style="color: #374151; margin-bottom: 1rem;">👆 Upload a file to get started</h3>
        <p style="color: #6b7280;">
            Supports Excel (.xlsx, .xls) and CSV files.<br>
            Your file must have headers in the first row.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample data generator
    st.markdown("---")
    st.markdown("### 🧪 Or try with sample data")
    
    if st.button("Generate Sample Dataset", use_container_width=True):
        # Create sample data with some anomalies
        np.random.seed(42)
        n = 50
        
        sample_data = {
            'Transaction_ID': [f'TXN-{i:04d}' for i in range(1, n+1)],
            'Vendor': np.random.choice(['Vendor A', 'Vendor B', 'Vendor C', 'Vendor D'], n),
            'Amount': np.concatenate([
                np.random.normal(1000, 200, n-5),  # Normal transactions
                [5000, 8500, 12000, 15, 0.5]  # Anomalies
            ]),
            'Quantity': np.concatenate([
                np.random.normal(50, 10, n-3),
                [200, 1, 500]  # Anomalies
            ]),
            'Unit_Price': np.concatenate([
                np.random.normal(20, 3, n-4),
                [100, 0.5, 85, 2]  # Anomalies
            ])
        }
        
        sample_df = pd.DataFrame(sample_data)
        
        # Store sample data
        st.session_state['sample_df'] = sample_df
        st.success("✅ Sample dataset generated! Preview below:")
        st.dataframe(sample_df.head(10), use_container_width=True)
        
        # Auto-analyze sample
        numeric_cols = ['Amount', 'Quantity', 'Unit_Price']
        results_df = detect_anomalies(sample_df, numeric_cols)
        st.session_state['results'] = results_df
        st.session_state['analyzed'] = True
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #9ca3af; font-size: 0.85rem; padding: 1rem;">
    <p>🔒 This is a limited online demo. Your data is processed in-browser and not stored.</p>
    <p>The full desktop version offers 100% offline privacy, advanced AI, and unlimited file sizes.</p>
    <p style="margin-top: 1rem;">© 2025 Mubsira Analytics — <a href="mailto:technozeeqc@gmail.com" style="color: #0d9488;">Contact</a></p>
</div>
""", unsafe_allow_html=True)
