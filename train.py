"""
Main Training Pipeline Orchestrator
Runs: Data Generation → Preprocessing → Model Training
"""

import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def run_pipeline():
    """Execute complete ML pipeline"""
    
    print("\n" + "="*80)
    print(" " * 20 + "🎓 PLACEMENT AI - COMPLETE PIPELINE")
    print("="*80)
    
    project_dir = Path(__file__).parent
    scripts = [
        ('data_generator.py', 'Generating Synthetic Dataset'),
        ('preprocessing.py', 'Data Preprocessing & Scaling'),
        ('model_trainer.py', 'Training & Evaluating Models'),
    ]
    
    for script, description in scripts:
        script_path = project_dir / script
        
        if not script_path.exists():
            print(f"\n❌ Script not found: {script}")
            continue
        
        print(f"\n" + "-"*80)
        print(f"📍 {description}")
        print("-"*80)
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(project_dir),
                capture_output=False
            )
            if result.returncode != 0:
                print(f"❌ Script failed: {script}")
                return False
        except Exception as e:
            print(f"❌ Error running {script}: {e}")
            return False
    
    print("\n" + "="*80)
    print(" " * 25 + "✅ PIPELINE COMPLETE!")
    print("="*80)
    print("\n📁 Output Files Created:")
    print("   • data/raw/student_data.csv - Synthetic dataset")
    print("   • data/processed/X_train.csv, X_test.csv - Processed features")
    print("   • models/ - Trained model files (.pkl)")
    print("\n📊 Next Steps:")
    print("   1. Run Jupyter notebooks for detailed EDA")
    print("   2. Launch Streamlit dashboard: streamlit run app/dashboard.py")
    print("   3. Review model performance in reports/")
    print("\n")
    
    return True

if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
