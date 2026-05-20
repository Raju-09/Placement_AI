#!/usr/bin/env python3
"""
Execute complete pipeline with detailed output
"""

import sys
import os
import traceback
from pathlib import Path

# Ensure we're in the right directory
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*80)
print(" "*20 + "🎓 PLACEMENT AI - EXECUTING PIPELINE")
print("="*80)

try:
    # ========================================================================
    # STEP 1: DATA GENERATION
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 1: GENERATING SYNTHETIC DATASET")
    print("="*80 + "\n")
    
    from data_generator import generate_student_data
    import pandas as pd
    
    print("📊 Creating 800 student records...")
    df = generate_student_data(n_students=800)
    
    # Create data directory
    data_dir = Path(__file__).parent / 'data' / 'raw'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Save dataset
    output_path = data_dir / 'student_data.csv'
    df.to_csv(output_path, index=False)
    
    print(f"\n✅ Dataset generated successfully!")
    print(f"   Location: {output_path}")
    print(f"   Shape: {df.shape}")
    print(f"   Placement Rate: {df['Placed'].mean()*100:.1f}%")
    print(f"\n📊 Sample Data (First 5 students):")
    print(df.head().to_string())
    print(f"\n📈 Dataset Statistics:")
    print(df.describe().round(2).to_string())
    
except Exception as e:
    print(f"❌ Error in data generation: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    # ========================================================================
    # STEP 2: PREPROCESSING
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 2: PREPROCESSING & SCALING DATA")
    print("="*80 + "\n")
    
    from preprocessing import PreprocessingPipeline
    import pickle
    
    pipeline = PreprocessingPipeline()
    data_path = data_dir / 'student_data.csv'
    
    X_train, X_test, y_train, y_test = pipeline.process(str(data_path))
    
    # Save processed data
    processed_dir = Path(__file__).parent / 'data' / 'processed'
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    X_train.to_csv(processed_dir / 'X_train.csv', index=False)
    X_test.to_csv(processed_dir / 'X_test.csv', index=False)
    y_train.to_csv(processed_dir / 'y_train.csv', index=False)
    y_test.to_csv(processed_dir / 'y_test.csv', index=False)
    
    with open(processed_dir / 'scaler.pkl', 'wb') as f:
        pickle.dump(pipeline.scaler, f)
    
    print("\n✅ Data preprocessing complete!")
    print(f"\n📊 Scaled Data Sample (First 3 rows):")
    print(X_train.head(3).to_string())
    
except Exception as e:
    print(f"❌ Error in preprocessing: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    # ========================================================================
    # STEP 3: MODEL TRAINING
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 3: TRAINING & EVALUATING MODELS")
    print("="*80 + "\n")
    
    from model_trainer import ModelTrainer
    
    trainer = ModelTrainer()
    trainer.train_models(X_train, y_train)
    
    evaluation_results = trainer.evaluate_all(X_train, X_test, y_train, y_test)
    
    comparison_df, best_model = trainer.compare_models(evaluation_results)
    
    trainer.extract_feature_importance(X_train.columns.tolist())
    
    models_dir = Path(__file__).parent / 'models'
    models_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_models('models')
    
    print("\n✅ Model training complete!")
    
except Exception as e:
    print(f"❌ Error in model training: {e}")
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*80)
print(" "*25 + "✅ PIPELINE COMPLETE!")
print("="*80)

print("""
📁 Generated Files:
   ✅ data/raw/student_data.csv
   ✅ data/processed/X_train.csv, X_test.csv
   ✅ data/processed/y_train.csv, y_test.csv
   ✅ data/processed/scaler.pkl
   ✅ models/logistic_regression.pkl
   ✅ models/knn.pkl
   ✅ models/naive_bayes.pkl
   ✅ models/svm.pkl
   ✅ models/results.json

📊 Summary:
   • 800 synthetic students generated
   • Features: CGPA, DSA, Aptitude, Communication, etc.
   • Placement rate: ~65% (realistic)
   • 4 ML models trained
   • 5 evaluation metrics used
   • Feature importance analyzed

🎯 Next Step:
   streamlit run dashboard.py

   Then visit: http://localhost:8501
""")

print("="*80)
print("✅ READY FOR DASHBOARD!")
print("="*80 + "\n")
