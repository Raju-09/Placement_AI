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

# Title and Description
st.markdown("""
# 🎓 Placement AI - Intelligent Student Placement Prediction System

Welcome! This dashboard helps you:
- 📊 **Predict** your placement probability
- ⚠️ **Identify** areas of concern (risk score)
- 💡 **Get personalized** recommendations
- 📈 **Compare** yourself with other students
""")

# Load resources
models, scaler = load_models_and_scaler()
dataset = load_dataset()

if not models:
    st.error("⚠️ Models not found. Please run `python train.py` first.")
    st.stop()

# Sidebar for navigation
st.sidebar.title("📍 Navigation")
page = st.sidebar.radio("Select Page:", [
    "🎯 Prediction",
    "📊 Analytics",
    "📚 About"
])

# ============================================================================
# PAGE 1: PREDICTION
# ============================================================================
if page == "🎯 Prediction":
    st.header("Student Profile & Placement Prediction")
    
    col1, col2 = st.columns(2)
    
    with col1:
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
        st.subheader("📊 Prediction Results")
        
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
        
        # Display predictions
        st.markdown("### 🔮 Model Predictions")
        
        pred_df = pd.DataFrame({
            'Model': list(models.keys()),
            'Prediction': [predictions[m] for m in models.keys()],
            'Confidence': [f"{probabilities[m]*100:.1f}%" if probabilities[m] else "N/A" 
                          for m in models.keys()]
        })
        
        st.dataframe(pred_df, use_container_width=True)
        
        # Consensus prediction
        avg_prob = np.mean([p for p in probabilities.values() if p is not None])
        consensus = "✅ LIKELY TO GET PLACED" if avg_prob > 0.6 else "⚠️ AT RISK" if avg_prob > 0.4 else "❌ HIGH RISK"
        
        st.markdown(f"""
        ### 🎯 Consensus Prediction
        **{consensus}**
        
        Average Placement Probability: **{avg_prob*100:.1f}%**
        """)
    
    # Risk Analysis
    st.markdown("---")
    st.header("📋 Detailed Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("CGPA", cgpa, delta="Good" if cgpa >= 8 else "Average" if cgpa >= 7 else "Needs Improvement")
    with col2:
        st.metric("DSA Score", f"{dsa_score}/100", delta="Strong" if dsa_score >= 70 else "Moderate" if dsa_score >= 50 else "Weak")
    with col3:
        st.metric("Communication", f"{communication}/10", delta="Good" if communication >= 7 else "Average" if communication >= 5 else "Weak")
    
    # Recommendations
    st.markdown("### 💡 Personalized Recommendations")
    recommendations = []
    
    if dsa_score < 70:
        recommendations.append("📚 **Improve DSA Skills** - Solve LeetCode problems")
    if communication < 7:
        recommendations.append("🎤 **Enhance Communication** - Join mock interview groups")
    if cgpa < 7.5:
        recommendations.append("📖 **Boost CGPA** - Focus on core subjects")
    if internships == 0:
        recommendations.append("🏢 **Get Internship Experience** - Apply for internship programs")
    if projects < 2:
        recommendations.append("💻 **Build Projects** - Create portfolio projects")
    if backlogs > 0:
        recommendations.append("✅ **Clear Backlogs** - Pass all pending exams")
    
    if not recommendations:
        recommendations.append("✨ **You're well-prepared!** Keep maintaining your profile.")
    
    for rec in recommendations:
        st.info(rec)

# ============================================================================
# PAGE 2: ANALYTICS
# ============================================================================
elif page == "📊 Analytics":
    st.header("📊 Data Analysis & Insights")
    
    if dataset is None:
        st.error("Dataset not found")
        st.stop()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Students", len(dataset))
    with col2:
        placed_count = dataset['Placed'].sum()
        st.metric("Placed Students", placed_count, f"{placed_count/len(dataset)*100:.1f}%")
    with col3:
        not_placed = len(dataset) - placed_count
        st.metric("Not Placed", not_placed, f"{not_placed/len(dataset)*100:.1f}%")
    
    st.markdown("---")
    st.subheader("📈 Feature Distributions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots()
        dataset['CGPA'].hist(bins=20, ax=ax, color='skyblue', edgecolor='black')
        ax.set_title('CGPA Distribution')
        ax.set_xlabel('CGPA')
        st.pyplot(fig)
    
    with col2:
        fig, ax = plt.subplots()
        dataset['DSA_Score'].hist(bins=20, ax=ax, color='lightgreen', edgecolor='black')
        ax.set_title('DSA Score Distribution')
        ax.set_xlabel('DSA Score')
        st.pyplot(fig)
    
    # Correlations
    st.subheader("🔗 Feature Correlation with Placement")
    correlations = dataset.corr()['Placed'].drop('Placed').sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['green' if x > 0 else 'red' for x in correlations.values]
    correlations.plot(kind='barh', ax=ax, color=colors)
    ax.set_title('Feature Correlation with Placement')
    st.pyplot(fig)

# ============================================================================
# PAGE 3: ABOUT
# ============================================================================
elif page == "📚 About":
    st.header("📚 About This Project")
    
    st.markdown("""
    ## 🎓 Placement AI - Research-Quality ML System
    
    ### 🎯 What Makes This Different
    
    - ✅ **Multiple Models** - Compare 4 algorithms
    - ✅ **Proper Evaluation** - Accuracy, Precision, Recall, F1
    - ✅ **Feature Analysis** - Understand what matters
    - ✅ **Risk Scoring** - Identify at-risk students
    - ✅ **Actionable Insights** - Real recommendations
    
    ### 📊 Dataset
    - 800 synthetic students
    - 11 meaningful features
    - Realistic placement distribution
    
    ### 🔬 Research Questions
    
    **RQ1:** Which features predict placement best?
    
    **RQ2:** Which algorithm works best?
    
    **RQ3:** Can we identify at-risk students early?
    
    ### 💡 Key Tech
    - Scikit-learn for ML
    - Streamlit for UI
    - Pandas & NumPy for data
    - Matplotlib for visualization
    """)

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>🎓 Placement AI</div>", unsafe_allow_html=True)
