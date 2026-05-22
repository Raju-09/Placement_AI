"""
Interactive Streamlit Dashboard for Placement Prediction
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler

# Configure Streamlit
st.set_page_config(
    page_title="Placement AI Dashboard",
    page_icon="🎓",
    layout="wide"
)

# Load models and scaler
@st.cache_resource
def load_models_and_scaler():
    """Load trained models and scaler"""
    models_dir = Path(__file__).parent / 'models'
    
    models = {}
    model_files = ['logistic_regression.pkl', 'knn.pkl', 'naive_bayes.pkl', 'svm.pkl']
    
    for file in model_files:
        path = models_dir / file
        if path.exists():
            with open(path, 'rb') as f:
                model_name = file.replace('.pkl', '').replace('_', ' ').title()
                models[model_name] = pickle.load(f)
    
    scaler_path = Path(__file__).parent / 'data' / 'processed' / 'scaler.pkl'
    scaler = None
    if scaler_path.exists():
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
    
    return models, scaler

@st.cache_data
def load_dataset():
    """Load original dataset for statistics"""
    data_path = Path(__file__).parent / 'data' / 'raw' / 'student_data.csv'
    if data_path.exists():
        return pd.read_csv(data_path)
    return None

# Load resources
models, scaler = load_models_and_scaler()
dataset = load_dataset()

if not models:
    st.error("⚠️ Models not found. Please run `python train.py` first.")
    st.stop()

# ============================================================================
# THEME CONFIGURATION & CUSTOM CSS INJECTION
# ============================================================================

# Sidebar for navigation and theme
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h2 style="margin: 0; background: linear-gradient(135deg, #3B82F6, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 1.75rem;">Placement AI</h2>
    <p style="color: gray; margin: 0.25rem 0 0 0; font-size: 0.85rem;">Intelligent Student Insights</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.subheader("📍 Navigation")
page = st.sidebar.radio("Select Page:", [
    "🎯 Prediction",
    "📊 Analytics",
    "📚 About"
])

st.sidebar.markdown("<div class='custom-divider' style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
st.sidebar.subheader("🎨 Customize Dashboard")
theme = st.sidebar.selectbox("Select Theme", ["Dark Theme", "Light Theme"])

# Set theme variables
if theme == "Dark Theme":
    theme_css = """
    :root {
        --background: #0B0F19;
        --sidebar-background: #111827;
        --card-background: #1E293B;
        --text-color: #F9FAFB;
        --text-secondary: #9CA3AF;
        --primary: #3B82F6;
        --accent: #8B5CF6;
        --success: #10B981;
        --warning: #F59E0B;
        --error: #EF4444;
        --border: #334155;
    }
    """
    fig_facecolor = '#0B0F19'
    ax_facecolor = '#1E293B'
    grid_color = '#334155'
    plt_text_color = '#F9FAFB'
    accent_color = '#3B82F6'
    accent_color_2 = '#10B981'
else:
    theme_css = """
    :root {
        --background: #F9FAFB;
        --sidebar-background: #FFFFFF;
        --card-background: #FFFFFF;
        --text-color: #111827;
        --text-secondary: #4B5563;
        --primary: #2563EB;
        --accent: #7C3AED;
        --success: #059669;
        --warning: #D97706;
        --error: #DC2626;
        --border: #E5E7EB;
    }
    """
    fig_facecolor = '#F9FAFB'
    ax_facecolor = '#FFFFFF'
    grid_color = '#E5E7EB'
    plt_text_color = '#111827'
    accent_color = '#2563EB'
    accent_color_2 = '#059669'

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');
    
    {theme_css}
    
    /* Core Layout Styles */
    .stApp, [data-testid="stAppViewContainer"] {{
        background-color: var(--background) !important;
        color: var(--text-color) !important;
        font-family: 'Inter', sans-serif !important;
    }}
    
    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: var(--sidebar-background) !important;
        border-right: 1px solid var(--border) !important;
    }}
    
    /* Typography */
    h1, h2, h3, h4, h5, h6, [data-testid="stWidgetLabel"] p, .stMarkdown p {{
        font-family: 'Outfit', sans-serif !important;
        color: var(--text-color) !important;
    }}
    
    .stMarkdown p, .stSlider p {{
        font-family: 'Inter', sans-serif !important;
    }}
    
    /* Strict override for radio label colors (fix low-contrast white labels) */
    div[data-testid="stRadio"] label p, div[data-testid="stRadio"] p, div[data-testid="stRadio"] span {{
        color: var(--text-color) !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }}
    
    /* Slider active styles */
    .stSlider [data-testid="stWidgetLabel"] p {{
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }}
    .stSlider [data-baseweb="slider"] > div {{
        background-color: var(--primary) !important;
    }}
    .stSlider [data-baseweb="slider"] [role="slider"] {{
        background-color: var(--primary) !important;
        border-color: var(--primary) !important;
    }}
    
    /* BaseWeb Selectbox / Dropdown fixes */
    div[data-baseweb="select"] > div {{
        background-color: var(--background) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border) !important;
    }}
    div[data-baseweb="select"] span {{
        color: var(--text-color) !important;
    }}
    
    /* Style Native st.container borders into beautiful dashboard cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: var(--card-background) !important;
        border: 1px solid var(--border) !important;
        border-radius: 1.25rem !important;
        padding: 2rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 1.5rem !important;
    }}
    
    /* Hero Header Banner */
    .hero-container {{
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(139, 92, 246, 0.12));
        border: 1px solid var(--border);
        border-radius: 1.25rem;
        padding: 2.25rem;
        margin-bottom: 2.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
    }}
    
    .hero-badge {{
        display: inline-block;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        color: white !important;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.35rem 0.85rem;
        border-radius: 50px;
        margin-bottom: 1.25rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.2);
    }}
    
    .hero-title {{
        font-size: 2.75rem !important;
        font-weight: 800 !important;
        margin: 0 0 0.75rem 0 !important;
        line-height: 1.2 !important;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }}
    
    .hero-subtitle {{
        font-size: 1.15rem;
        color: var(--text-secondary);
        margin: 0 0 1.75rem 0;
        font-weight: 500;
        line-height: 1.5;
    }}
    
    .hero-features {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
    }}
    
    .hero-feature-tag {{
        background-color: var(--card-background);
        border: 1px solid var(--border);
        color: var(--text-color);
        font-size: 0.85rem;
        font-weight: 600;
        padding: 0.45rem 1rem;
        border-radius: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.35rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
    }}
    
    /* Consensus Prediction CSS */
    .consensus-card {{
        padding: 1.75rem;
        border-radius: 1.25rem;
        border: 1px solid var(--border);
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }}
    
    .consensus-success {{
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(16, 185, 129, 0.04));
        border-left: 6px solid var(--success);
    }}
    
    .consensus-warning {{
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(245, 158, 11, 0.04));
        border-left: 6px solid var(--warning);
    }}
    
    .consensus-danger {{
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.12), rgba(239, 68, 68, 0.04));
        border-left: 6px solid var(--error);
    }}
    
    /* Recommendations Layout CSS */
    .rec-container {{
        display: flex;
        flex-direction: column;
        gap: 0.85rem;
        margin-top: 1.25rem;
    }}
    
    .rec-item {{
        background-color: var(--card-background);
        border: 1px solid var(--border);
        border-radius: 0.85rem;
        padding: 1.15rem 1.4rem;
        display: flex;
        align-items: center;
        gap: 1.15rem;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.01);
    }}
    
    .rec-item:hover {{
        transform: translateX(6px);
        border-color: var(--primary);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.05);
    }}
    
    .rec-icon {{
        font-size: 1.6rem;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2.75rem;
        height: 2.75rem;
        border-radius: 0.65rem;
        background: rgba(59, 130, 246, 0.1);
        color: var(--primary);
        flex-shrink: 0;
    }}
    
    .rec-text {{
        font-size: 1rem;
        font-weight: 500;
        color: var(--text-color);
        line-height: 1.4;
    }}
    
    /* Metric overrides */
    [data-testid="stMetricValue"] {{
        font-family: 'Outfit', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: var(--primary) !important;
    }}
    
    [data-testid="stMetricLabel"] p {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        font-size: 0.95rem !important;
    }}
    
    /* Custom divider */
    .custom-divider {{
        height: 1px;
        background: var(--border);
        margin: 2.5rem 0;
    }}
    
    /* About list items */
    .about-card {{
        background-color: var(--card-background);
        border: 1px solid var(--border);
        border-radius: 1rem;
        padding: 1.75rem;
        margin-bottom: 1.5rem;
    }}
    
    .about-card li {{
        margin-bottom: 0.65rem;
        line-height: 1.6;
    }}
</style>
""", unsafe_allow_html=True)

# Styled Hero Header Banner
st.markdown(f"""
<div class="hero-container">
    <div class="hero-badge">🎓 RESEARCH-QUALITY ML SYSTEM</div>
    <h1 class="hero-title">Placement AI</h1>
    <p class="hero-subtitle">Predict student placement probability, evaluate individual risk scores, and obtain tailored action items with an advanced multi-model consensus pipeline.</p>
    <div class="hero-features">
        <span class="hero-feature-tag">🎯 Multi-Model Consensus</span>
        <span class="hero-feature-tag">📈 Real-Time Analytics</span>
        <span class="hero-feature-tag">💡 Actionable Insights</span>
        <span class="hero-feature-tag">⚡ Edge ML Models</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Helper function to create clean styled matplotlib/seaborn plots
def create_styled_plot(figsize=(6, 4)):
    # Configure rcParams dynamically
    plt.rcParams['figure.facecolor'] = fig_facecolor
    plt.rcParams['axes.facecolor'] = ax_facecolor
    plt.rcParams['axes.edgecolor'] = grid_color
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.color'] = grid_color
    plt.rcParams['text.color'] = plt_text_color
    plt.rcParams['axes.labelcolor'] = plt_text_color
    plt.rcParams['xtick.color'] = plt_text_color
    plt.rcParams['ytick.color'] = plt_text_color
    
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(fig_facecolor)
    ax.set_facecolor(ax_facecolor)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(grid_color)
    ax.spines['bottom'].set_color(grid_color)
    return fig, ax

# ============================================================================
# PAGE 1: PREDICTION
# ============================================================================
if page == "🎯 Prediction":
    st.header("Student Profile & Placement Prediction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.subheader("📝 Enter Your Profile")
            
            cgpa = st.slider("CGPA", 5.5, 10.0, 7.5, 0.1)
            dsa_score = st.slider("DSA Score (0-100)", 0, 100, 60, 1)
            aptitude = st.slider("Aptitude Score (0-100)", 0, 100, 70, 1)
            communication = st.slider("Communication Skills (0-10)", 0.0, 10.0, 6.0, 0.1)
            attendance = st.slider("Attendance (%)", 0, 100, 85, 1)
            internships = st.slider("Internship Count", 0, 3, 1, 1)
            projects = st.slider("Project Count", 0, 5, 2, 1)
            hackathons = st.slider("Hackathon Participations", 0, 3, 0, 1)
            certifications = st.slider("Certifications", 0, 3, 1, 1)
            backlogs = st.slider("Backlogs", 0, 10, 0, 1)
    
    # Prepare input data
    input_data = np.array([[
        cgpa, dsa_score, aptitude, communication, attendance,
        internships, projects, hackathons, certifications, backlogs
    ]])
    
    # Scale input
    if scaler:
        input_data_scaled = scaler.transform(input_data)
    else:
        input_data_scaled = input_data
    
    with col2:
        with st.container(border=True):
            st.subheader("🔮 Predictions & Confidence")
            
            # Make predictions
            predictions = {}
            probabilities = {}
            
            for model_name, model in models.items():
                pred = model.predict(input_data_scaled)[0]
                predictions[model_name] = pred
                
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(input_data_scaled)[0]
                    probabilities[model_name] = proba[1]
                else:
                    probabilities[model_name] = None
            
            # Custom styled HTML Predictions Table
            pred_html = f"""
            <table style="width: 100%; border-collapse: collapse; margin-top: 1rem; margin-bottom: 1.5rem; color: var(--text-color); font-family: 'Inter', sans-serif;">
                <thead>
                    <tr style="border-bottom: 2px solid var(--border); text-align: left;">
                        <th style="padding: 0.75rem 1rem; font-weight: 700; font-family: 'Outfit'; font-size: 0.95rem;">Model Name</th>
                        <th style="padding: 0.75rem 1rem; font-weight: 700; font-family: 'Outfit'; font-size: 0.95rem;">Result Status</th>
                        <th style="padding: 0.75rem 1rem; font-weight: 700; font-family: 'Outfit'; font-size: 0.95rem; text-align: right;">Placement Probability</th>
                    </tr>
                </thead>
                <tbody>
            """
            for model_name, model in models.items():
                pred = predictions[model_name]
                status_text = "✅ PLACED" if pred == 1 else "❌ UNPLACED"
                status_color = "var(--success)" if pred == 1 else "var(--error)"
                prob_text = f"{probabilities[model_name]*100:.1f}%" if probabilities[model_name] is not None else "N/A"
                
                pred_html += f"""
                    <tr style="border-bottom: 1px solid var(--border);">
                        <td style="padding: 0.75rem 1rem; font-weight: 600; font-size: 0.9rem;">{model_name}</td>
                        <td style="padding: 0.75rem 1rem; font-weight: 700; font-size: 0.9rem; color: {status_color};">{status_text}</td>
                        <td style="padding: 0.75rem 1rem; font-weight: 800; font-size: 0.9rem; text-align: right; color: var(--primary);">{prob_text}</td>
                    </tr>
                """
            pred_html += "</tbody></table>"
            st.markdown(pred_html, unsafe_allow_html=True)
            
            # Consensus prediction
            avg_prob = np.mean([p for p in probabilities.values() if p is not None])
            
            if avg_prob > 0.6:
                consensus_class = "consensus-success"
                consensus_title = "✅ STRONG CANDIDATE Profile"
                consensus_desc = "Excellent metrics! The ensemble consensus predicts a very high likelihood of successful placement. Keep up the high standard!"
            elif avg_prob > 0.4:
                consensus_class = "consensus-warning"
                consensus_title = "⚠️ AT-RISK Profile (Borderline)"
                consensus_desc = "You have a solid foundation, but there is noticeable risk. Focus on targeting the critical improvement areas identified below."
            else:
                consensus_class = "consensus-danger"
                consensus_title = "❌ CRITICAL RISK Profile"
                consensus_desc = "Significant risk identified. Important metrics in core engineering features fall below typical placement thresholds."

            st.markdown(f"""
            <div class="consensus-card {consensus_class}">
                <h3 style="margin-top: 0; font-weight: 700; color: var(--text-color);">{consensus_title}</h3>
                <p style="font-size: 1.15rem; font-weight: 600; margin-bottom: 0.5rem;">Average Placement Probability: <span style="font-size: 1.45rem; color: var(--primary); font-weight: 800;">{avg_prob*100:.1f}%</span></p>
                <p style="margin: 0; color: var(--text-secondary); font-size: 0.95rem;">{consensus_desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Risk Analysis
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    st.header("📋 Detailed Academic & Technical Review")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("CGPA Metric", cgpa, delta="Strong (>= 8.0)" if cgpa >= 8 else "Average (7.0 - 8.0)" if cgpa >= 7 else "Needs Improvement (< 7.0)")
    with col2:
        st.metric("DSA Score", f"{dsa_score}/100", delta="Excellent (>= 70)" if dsa_score >= 70 else "Competent (50 - 70)" if dsa_score >= 50 else "Requires Focus (< 50)")
    with col3:
        st.metric("Communication Skill", f"{communication}/10", delta="Fluent (>= 7.0)" if communication >= 7 else "Average (5.0 - 7.0)" if communication >= 5 else "Needs Development (< 5.0)")
    
    # Recommendations
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.subheader("💡 Actionable Personalized Recommendations")
    
    recommendations = []
    
    if dsa_score < 70:
        recommendations.append(("📚", "Master Data Structures & Algorithms (DSA)", "Solve structured problems on platforms like LeetCode and GeeksforGeeks. Focus heavily on Trees, Graphs, and Dynamic Programming."))
    if communication < 7:
        recommendations.append(("🎤", "Enhance Verbal & Interview Communication", "Join mock interview groups, practice explaining technical code blocks aloud, and focus on non-verbal presentation cues."))
    if cgpa < 7.5:
        recommendations.append(("📖", "Boost Cumulative Academic Grade Point", "Focus intently on upcoming core curriculum subjects, laboratory exams, and theoretical assessments to elevate your overall CGPA."))
    if internships == 0:
        recommendations.append(("🏢", "Secure Practical Internship Experience", "Apply to early career programs and startup roles. Practical industrial experience is a highly influential placement indicator."))
    if projects < 2:
        recommendations.append(("💻", "Build Quality Engineering Portfolio Projects", "Develop full-stack or data science portfolio projects with real-world utility. Push clean, documented code to your public GitHub profile."))
    if backlogs > 0:
        recommendations.append(("✅", "Prioritize Clearing Outstanding Backlogs", "Set up study milestones to systematically clear any outstanding backlogs, as several recruiters mandate zero-active-backlog policies."))
    
    if not recommendations:
        recommendations.append(("✨", "Outstanding Student Profile!", "You meet or exceed all critical technical and academic criteria. Maintain your high CGPA and keep refining your system design knowledge."))
    
    # Render customized HTML cards for recommendations
    recommendations_html = ""
    for icon, title, desc in recommendations:
        recommendations_html += f"""
        <div class="rec-item">
            <div class="rec-icon">{icon}</div>
            <div>
                <div class="rec-text" style="font-weight: 700; font-size: 1.05rem; margin-bottom: 0.15rem;">{title}</div>
                <div style="font-size: 0.9rem; color: var(--text-secondary);">{desc}</div>
            </div>
        </div>
        """
    
    st.markdown(f"<div class='rec-container'>{recommendations_html}</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE 2: ANALYTICS
# ============================================================================
elif page == "📊 Analytics":
    st.header("📊 Analytical Distribution & Insights")
    
    if dataset is None:
        st.error("Dataset not found")
        st.stop()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Sample Size", len(dataset))
    with col2:
        placed_count = dataset['Placed'].sum()
        st.metric("Successful Placements", placed_count, f"{placed_count/len(dataset)*100:.1f}% Ratio")
    with col3:
        not_placed = len(dataset) - placed_count
        st.metric("Risk/Unplaced Group", not_placed, f"{not_placed/len(dataset)*100:.1f}% Ratio")
    
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    st.subheader("📈 Technical & Academic Feature Distributions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = create_styled_plot()
        sns.histplot(data=dataset, x='CGPA', hue='Placed', multiple='stack', kde=True, ax=ax, palette=[ '#EF4444', '#10B981'])
        ax.set_title('CGPA Distribution by Placement Result', fontsize=12, fontweight='bold', pad=12)
        ax.set_xlabel('CGPA', fontweight='semibold')
        ax.set_ylabel('Student Count', fontweight='semibold')
        st.pyplot(fig)
    
    with col2:
        fig, ax = create_styled_plot()
        sns.histplot(data=dataset, x='DSA_Score', hue='Placed', multiple='stack', kde=True, ax=ax, palette=['#EF4444', '#10B981'])
        ax.set_title('DSA Score Distribution by Placement Result', fontsize=12, fontweight='bold', pad=12)
        ax.set_xlabel('DSA Score', fontweight='semibold')
        ax.set_ylabel('Student Count', fontweight='semibold')
        st.pyplot(fig)
    
    # Correlations
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.subheader("🔗 Feature Correlation with Successful Placement")
    correlations = dataset.corr()['Placed'].drop('Placed').sort_values(ascending=True)
    
    fig, ax = create_styled_plot(figsize=(10, 6.5))
    colors = ['#10B981' if x > 0 else '#EF4444' for x in correlations.values]
    
    ax.barh(correlations.index, correlations.values, color=colors, edgecolor=grid_color, height=0.6)
    ax.axvline(x=0, color=plt_text_color, linestyle='--', alpha=0.3)
    ax.set_title('Feature Correlation Strengths relative to Placement Status', fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel('Correlation Coefficient value (r)', fontweight='semibold')
    
    # Add values on bars
    for i, val in enumerate(correlations.values):
        align = 'left' if val < 0 else 'right'
        offset = -0.04 if val < 0 else 0.04
        ax.text(val + offset, i, f"{val:+.2f}", va='center', ha='center', fontsize=9, fontweight='bold', color=plt_text_color)
        
    st.pyplot(fig)

# ============================================================================
# PAGE 3: ABOUT
# ============================================================================
elif page == "📚 About":
    st.header("📚 About This Project")
    
    st.markdown(f"""
    <div class="about-card">
        <h2 style="margin-top: 0; color: var(--primary);">🎓 Placement AI - Enterprise Grade Machine Learning Pipeline</h2>
        <p style="font-size: 1.05rem; line-height: 1.6; color: var(--text-color);">
            Placement AI is a production-level student evaluation dashboard powered by 4 optimized machine learning algorithms. 
            By standardizing and scaling academic grades, coding evaluations, and behavioral indicators, 
            the application provides a multi-model consensus prediction on early career placement prospects.
        </p>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1.5rem;">
        <div class="about-card" style="margin-bottom:0;">
            <h3 style="margin-top:0; color:var(--accent);">🔬 Key System Features</h3>
            <ul style="color: var(--text-secondary); padding-left: 1.25rem;">
                <li><strong>Algorithm Ensembling:</strong> Aggregates predictions across Logistic Regression, K-Nearest Neighbors, Naive Bayes, and Support Vector Machines (SVM).</li>
                <li><strong>Feature Scaling:</strong> Employs an offline-fitted <code>StandardScaler</code> to cleanly translate user input features before model scoring.</li>
                <li><strong>Risk Assessment:</strong> Computes probability scores using calibrated classifiers to isolate critical improvement fields.</li>
                <li><strong>Dynamic Recommendations:</strong> Employs threshold-based expert criteria to yield specific actionable goals.</li>
            </ul>
        </div>
        <div class="about-card" style="margin-bottom:0;">
            <h3 style="margin-top:0; color:var(--accent);">📊 Synthetic Student Dataset</h3>
            <ul style="color: var(--text-secondary); padding-left: 1.25rem;">
                <li><strong>Dimensions:</strong> 800 distinct synthesized student profiles.</li>
                <li><strong>Features:</strong> 10 academic, technical, extracurricular, and demographic indicators.</li>
                <li><strong>Evaluation Framework:</strong> Split-fold validation ensuring high precision, high recall, and realistic placement ratios.</li>
            </ul>
        </div>
    </div>
    
    <div class="about-card" style="margin-top: 1.5rem;">
        <h3 style="margin-top:0; color:var(--primary);">🔬 Critical Research Objectives</h3>
        <p style="color: var(--text-secondary); margin-bottom: 1rem;">The system is architected to address three crucial early-career research objectives:</p>
        <ol style="color: var(--text-secondary); padding-left: 1.25rem; line-height: 1.7;">
            <li><strong>Objective 1:</strong> Identify which student metrics (CGPA, DSA coding scores, internship frequency) correlate most strongly with recruiter placement patterns.</li>
            <li><strong>Objective 2:</strong> Evaluate which machine learning classifier yields the most consistent, robust metrics under diverse profile variations.</li>
            <li><strong>Objective 3:</strong> Provide a highly reliable, early warning framework for identifying at-risk students before placement cycles begin.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: var(--text-secondary); font-size: 0.9rem; font-weight: 500;'>🎓 Placement AI System • Designed for Academic & Career Growth</div>", unsafe_allow_html=True)
