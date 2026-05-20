"""
Data Preprocessing Pipeline
Handles cleaning, encoding, scaling, and train-test split
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from pathlib import Path
import pickle

class PreprocessingPipeline:
    """
    Complete preprocessing pipeline for placement dataset
    """
    
    def __init__(self, test_size=0.2, random_state=42):
        self.test_size = test_size
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='median')
        self.feature_names = None
        
    def load_data(self, filepath):
        """Load raw CSV data"""
        df = pd.read_csv(filepath)
        print(f"✅ Loaded data: {filepath}")
        print(f"   Shape: {df.shape}")
        print(f"   Missing values: {df.isnull().sum().sum()}")
        return df
    
    def handle_missing_values(self, df):
        """Handle missing values using median imputation"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if df[numeric_cols].isnull().any().any():
            df[numeric_cols] = self.imputer.fit_transform(df[numeric_cols])
            print("✅ Handled missing values using median imputation")
        return df
    
    def detect_outliers(self, df, method='iqr'):
        """Detect outliers using IQR method"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outliers = pd.DataFrame()
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            col_outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            if len(col_outliers) > 0:
                outliers[col] = len(col_outliers)
        
        if len(outliers) > 0:
            print(f"⚠️  Outliers detected (IQR method):")
            for col, count in outliers.items():
                print(f"   {col}: {count} outliers")
        return outliers
    
    def prepare_features_target(self, df):
        """Separate features and target"""
        X = df.drop('Placed', axis=1)
        y = df['Placed']
        self.feature_names = X.columns.tolist()
        print(f"✅ Features ({len(X.columns)}): {', '.join(X.columns)}")
        print(f"   Target: Placed (Binary Classification)")
        print(f"   Class distribution: {y.value_counts().to_dict()}")
        return X, y
    
    def split_data(self, X, y):
        """Split into train-test sets"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y
        )
        print(f"✅ Train-test split:")
        print(f"   Train: {len(X_train)} samples")
        print(f"   Test: {len(X_test)} samples")
        print(f"   Ratio: {len(X_train)/(len(X_train)+len(X_test)):.1%}")
        return X_train, X_test, y_train, y_test
    
    def scale_features(self, X_train, X_test):
        """Scale features using StandardScaler"""
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns)
        X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns)
        
        print("✅ Features scaled using StandardScaler")
        print(f"   Train mean: {X_train_scaled.mean().mean():.4f}")
        print(f"   Train std: {X_train_scaled.std().mean():.4f}")
        return X_train_scaled, X_test_scaled
    
    def process(self, filepath):
        """
        Run complete preprocessing pipeline
        Returns: X_train, X_test, y_train, y_test
        """
        print("\n" + "="*60)
        print("🔧 PREPROCESSING PIPELINE")
        print("="*60 + "\n")
        
        # Load
        df = self.load_data(filepath)
        print()
        
        # Handle missing values
        df = self.handle_missing_values(df)
        print()
        
        # Detect outliers
        self.detect_outliers(df)
        print()
        
        # Prepare features and target
        X, y = self.prepare_features_target(df)
        print()
        
        # Split
        X_train, X_test, y_train, y_test = self.split_data(X, y)
        print()
        
        # Scale
        X_train_scaled, X_test_scaled = self.scale_features(X_train, X_test)
        print()
        
        return X_train_scaled, X_test_scaled, y_train, y_test

def main():
    """Test preprocessing pipeline"""
    pipeline = PreprocessingPipeline()
    
    # Path to raw data
    data_path = Path(__file__).parent / 'data' / 'raw' / 'student_data.csv'
    
    if not data_path.exists():
        print("❌ Data file not found. Please run data_generator.py first.")
        return
    
    # Run pipeline
    X_train, X_test, y_train, y_test = pipeline.process(str(data_path))
    
    # Save processed data
    processed_dir = Path(__file__).parent / 'data' / 'processed'
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    X_train.to_csv(processed_dir / 'X_train.csv', index=False)
    X_test.to_csv(processed_dir / 'X_test.csv', index=False)
    y_train.to_csv(processed_dir / 'y_train.csv', index=False)
    y_test.to_csv(processed_dir / 'y_test.csv', index=False)
    
    # Save scaler for later use
    with open(processed_dir / 'scaler.pkl', 'wb') as f:
        pickle.dump(pipeline.scaler, f)
    
    print("✅ Processed data saved to data/processed/")

if __name__ == "__main__":
    main()
