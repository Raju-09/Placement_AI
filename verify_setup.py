"""
Verification script - Check if all files are created correctly
"""

import os
from pathlib import Path

def verify_setup():
    """Verify all project files are created"""
    
    project_dir = Path(__file__).parent
    
    print("\n" + "="*70)
    print("🔍 PROJECT SETUP VERIFICATION")
    print("="*70 + "\n")
    
    # Files to check
    required_files = {
        'requirements.txt': 'Python dependencies',
        'README.md': 'Project documentation',
        'QUICKSTART.md': 'Quick start guide',
        'data_generator.py': 'Dataset generation',
        'preprocessing.py': 'Data preprocessing',
        'model_trainer.py': 'Model training & evaluation',
        'run_pipeline.py': 'Complete pipeline orchestrator',
        'train.py': 'Alternative pipeline runner',
        'dashboard.py': 'Streamlit UI',
    }
    
    print("📋 Checking Core Files:")
    print("-" * 70)
    
    all_exist = True
    for filename, description in required_files.items():
        filepath = project_dir / filename
        exists = filepath.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {filename:25s} - {description}")
        if not exists:
            all_exist = False
    
    print("\n📁 Directory Structure:")
    print("-" * 70)
    
    expected_dirs = [
        'data/raw',
        'data/processed',
        'models',
    ]
    
    for dir_name in expected_dirs:
        dirpath = project_dir / dir_name
        print(f"  📂 {dir_name:30s} (will be created by pipeline)")
    
    print("\n" + "="*70)
    
    if all_exist:
        print("✅ ALL FILES CREATED SUCCESSFULLY!")
        print("="*70)
        print("""
🚀 NEXT STEPS:

1. Install Dependencies:
   pip install pandas numpy scikit-learn matplotlib seaborn streamlit

2. Run Complete Pipeline:
   python run_pipeline.py

3. Launch Dashboard:
   streamlit run dashboard.py

4. Visit: http://localhost:8501

📚 For detailed information, read: QUICKSTART.md
        """)
        return True
    else:
        print("❌ SOME FILES ARE MISSING!")
        print("="*70)
        return False

if __name__ == "__main__":
    verify_setup()
