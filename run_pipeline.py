#!/usr/bin/env python3
"""
Complete ML Pipeline - Data Generation → Preprocessing → Model Training
This script runs all steps in sequence
"""

import sys
import os
from pathlib import Path

# Add project to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def main():
    print("\n" + "="*80)
    print(" "*20 + "🎓 PLACEMENT AI - COMPLETE PIPELINE")
    print("="*80)
    
    # Step 1: Data Generation
    print("\n" + "="*80)
    print("STEP 1: Generating Synthetic Dataset")
    print("="*80 + "\n")
    
    try:
        from data_generator import generate_student_data
        
        data_dir = project_dir / 'data' / 'raw'
        data_dir.mkdir(parents=True, exist_ok=True)
        
        df = generate_student_data(n_students=800)
        output_path = data_dir / 'student_data.csv'
        df.to_csv(output_path, index=False)
        
        print(f"✅ Dataset created successfully!")
        print(f"   Location: {output_path}")
        print(f"   Students: {len(df)}")
        print(f"   Placed: {df['Placed'].sum()} ({100*df['Placed'].mean():.1f}%)")
        
    except Exception as e:
        print(f"❌ Error in data generation: {e}")
        return False
    
    # Step 2: Preprocessing
    print("\n" + "="*80)
    print("STEP 2: Preprocessing & Scaling Data")
    print("="*80 + "\n")
    
    try:
        from preprocessing import PreprocessingPipeline
        
        pipeline = PreprocessingPipeline()
        data_path = project_dir / 'data' / 'raw' / 'student_data.csv'
        
        X_train, X_test, y_train, y_test = pipeline.process(str(data_path))
        
        # Save processed data
        processed_dir = project_dir / 'data' / 'processed'
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        X_train.to_csv(processed_dir / 'X_train.csv', index=False)
        X_test.to_csv(processed_dir / 'X_test.csv', index=False)
        y_train.to_csv(processed_dir / 'y_train.csv', index=False)
        y_test.to_csv(processed_dir / 'y_test.csv', index=False)
        
        import pickle
        with open(processed_dir / 'scaler.pkl', 'wb') as f:
            pickle.dump(pipeline.scaler, f)
        
        print("✅ Data preprocessing complete!")
        print(f"   Processed data saved to: {processed_dir}")
        
    except Exception as e:
        print(f"❌ Error in preprocessing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Model Training
    print("\n" + "="*80)
    print("STEP 3: Training & Evaluating Models")
    print("="*80 + "\n")
    
    try:
        import pandas as pd
        from model_trainer import ModelTrainer
        
        # Reload processed data
        processed_dir = project_dir / 'data' / 'processed'
        X_train = pd.read_csv(processed_dir / 'X_train.csv')
        X_test = pd.read_csv(processed_dir / 'X_test.csv')
        y_train = pd.read_csv(processed_dir / 'y_train.csv').squeeze()
        y_test = pd.read_csv(processed_dir / 'y_test.csv').squeeze()
        
        trainer = ModelTrainer()
        trainer.train_models(X_train, y_train)
        
        evaluation_results = trainer.evaluate_all(X_train, X_test, y_train, y_test)
        
        comparison_df, best_model = trainer.compare_models(evaluation_results)
        
        trainer.extract_feature_importance(X_train.columns.tolist())
        
        trainer.save_models()
        
        print("\n✅ Model training complete!")
        
    except Exception as e:
        print(f"❌ Error in model training: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Final summary
    print("\n" + "="*80)
    print(" "*25 + "✅ PIPELINE COMPLETE!")
    print("="*80)
    print("""
📁 Generated Files:
   ✅ data/raw/student_data.csv - 800 student records
   ✅ data/processed/X_train.csv, X_test.csv - Processed features
   ✅ data/processed/y_train.csv, y_test.csv - Target variable
   ✅ data/processed/scaler.pkl - StandardScaler for future use
   ✅ models/*.pkl - Trained model files (4 models)
   ✅ models/results.json - Evaluation metrics

📊 Next Steps:
   1. Review results in models/results.json
   2. Launch Streamlit: streamlit run dashboard.py
   3. Explore data with: jupyter notebook
   4. Read README.md for detailed project info

🔬 Research Questions Answered:
   RQ1: Which features predict placement? → Feature importance analysis
   RQ2: Which algorithm works best? → Model comparison metrics
   RQ3: Identify at-risk students? → Risk scoring in dashboard

📚 Documentation:
   - README.md: Complete project overview
   - data_generator.py: Dataset creation logic
   - preprocessing.py: Data cleaning pipeline
   - model_trainer.py: ML models and evaluation
   - dashboard.py: Interactive UI
    """)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
