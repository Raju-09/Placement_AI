"""
Synthetic Student Placement Dataset Generator
Generates realistic student data with meaningful placement patterns
"""

import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

def generate_student_data(n_students=800):
    """
    Generate synthetic student data with realistic placement patterns.
    
    Logic:
    - Students with high DSA + Communication + reasonable CGPA get placed
    - Internships and projects increase placement chances
    - Low CGPA + high backlogs reduce placement chances
    - DSA is the strongest predictor
    """
    
    data = {
        'CGPA': np.random.uniform(5.5, 10.0, n_students),
        'DSA_Score': np.random.uniform(20, 100, n_students),
        'Aptitude_Score': np.random.uniform(30, 100, n_students),
        'Communication': np.random.uniform(0, 10, n_students),
        'Attendance': np.random.uniform(40, 100, n_students),
        'Internship_Count': np.random.randint(0, 4, n_students),
        'Project_Count': np.random.randint(0, 6, n_students),
        'Hackathons': np.random.randint(0, 4, n_students),
        'Certifications': np.random.randint(0, 4, n_students),
        'Backlogs': np.random.randint(0, 11, n_students),
    }
    
    df = pd.DataFrame(data)
    
    # Placement logic (ensures realistic patterns)
    placed = []
    for idx, row in df.iterrows():
        score = 0
        
        # Strong predictors
        if row['DSA_Score'] >= 70:
            score += 3
        elif row['DSA_Score'] >= 50:
            score += 1.5
            
        if row['Communication'] >= 7:
            score += 2
        elif row['Communication'] >= 5:
            score += 1
            
        # Moderate predictors
        if row['CGPA'] >= 8:
            score += 2
        elif row['CGPA'] >= 7:
            score += 1
            
        score += row['Internship_Count'] * 0.8
        score += row['Project_Count'] * 0.6
        score += row['Hackathons'] * 0.5
        score += row['Certifications'] * 0.7
        
        # Negative factors
        score -= row['Backlogs'] * 0.5
        if row['Attendance'] < 75:
            score -= 1.5
        
        # Add some randomness (real life isn't deterministic)
        score += np.random.normal(0, 0.5)
        
        # Placement threshold
        placed.append(1 if score >= 5 else 0)
    
    df['Placed'] = placed
    
    return df

def main():
    print("🎓 Generating Synthetic Student Placement Dataset...")
    
    # Create data directory
    data_dir = Path(__file__).parent / 'data' / 'raw'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate dataset
    df = generate_student_data(n_students=800)
    
    # Save to CSV
    output_path = data_dir / 'student_data.csv'
    df.to_csv(output_path, index=False)
    
    print(f"\n✅ Dataset created: {output_path}")
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total Students: {len(df)}")
    print(f"   Placed: {df['Placed'].sum()} ({100*df['Placed'].sum()/len(df):.1f}%)")
    print(f"   Not Placed: {len(df) - df['Placed'].sum()} ({100*(1-df['Placed'].mean()):.1f}%)")
    print(f"\n📈 Feature Ranges:")
    print(df.describe().round(2))
    print(f"\n🔗 Feature Correlations with Placement:")
    correlations = df.corr()['Placed'].sort_values(ascending=False)
    for feature, corr in correlations.items():
        if feature != 'Placed':
            print(f"   {feature:20s}: {corr:+.3f}")

if __name__ == "__main__":
    main()
