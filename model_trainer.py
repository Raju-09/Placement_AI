"""
Multi-Model Training and Evaluation Pipeline
Trains 4 different classifiers and compares their performance
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                            f1_score, confusion_matrix, classification_report, roc_auc_score)
import json

class ModelTrainer:
    """
    Trains and evaluates multiple ML models
    """
    
    def __init__(self):
        self.models = {
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'KNN': KNeighborsClassifier(n_neighbors=5),
            'Naive Bayes': GaussianNB(),
            'SVM': SVC(kernel='rbf', probability=True, random_state=42)
        }
        self.results = {}
        self.trained_models = {}
    
    def train_models(self, X_train, y_train):
        """Train all models"""
        print("\n" + "="*60)
        print("🤖 MODEL TRAINING")
        print("="*60 + "\n")
        
        for name, model in self.models.items():
            print(f"Training {name}...", end=' ')
            model.fit(X_train, y_train)
            self.trained_models[name] = model
            print("✅")
        
        print("\n✅ All models trained successfully!")
    
    def evaluate_model(self, name, model, X_train, X_test, y_train, y_test):
        """Evaluate a single model on train and test sets"""
        
        # Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        # For ROC-AUC, we need probabilities
        if hasattr(model, 'predict_proba'):
            y_test_proba = model.predict_proba(X_test)[:, 1]
            roc_auc = roc_auc_score(y_test, y_test_proba)
        else:
            roc_auc = None
        
        # Metrics
        metrics = {
            'Train Accuracy': accuracy_score(y_train, y_train_pred),
            'Test Accuracy': accuracy_score(y_test, y_test_pred),
            'Precision': precision_score(y_test, y_test_pred, zero_division=0),
            'Recall': recall_score(y_test, y_test_pred, zero_division=0),
            'F1-Score': f1_score(y_test, y_test_pred, zero_division=0),
            'ROC-AUC': roc_auc if roc_auc else 'N/A'
        }
        
        self.results[name] = {
            'metrics': metrics,
            'confusion_matrix': confusion_matrix(y_test, y_test_pred).tolist(),
            'y_test': y_test.tolist(),
            'y_pred': y_test_pred.tolist()
        }
        
        return metrics
    
    def evaluate_all(self, X_train, X_test, y_train, y_test):
        """Evaluate all trained models"""
        print("\n" + "="*60)
        print("📊 MODEL EVALUATION")
        print("="*60 + "\n")
        
        evaluation_results = {}
        for name, model in self.trained_models.items():
            print(f"Evaluating {name}...")
            metrics = self.evaluate_model(name, model, X_train, X_test, y_train, y_test)
            evaluation_results[name] = metrics
            print(f"   Test Accuracy: {metrics['Test Accuracy']:.4f}")
            print(f"   Precision: {metrics['Precision']:.4f}")
            print(f"   Recall: {metrics['Recall']:.4f}")
            print(f"   F1-Score: {metrics['F1-Score']:.4f}\n")
        
        return evaluation_results
    
    def compare_models(self, evaluation_results):
        """Compare all models and display rankings"""
        print("\n" + "="*60)
        print("🏆 MODEL COMPARISON")
        print("="*60 + "\n")
        
        # Create comparison dataframe
        comparison_df = pd.DataFrame({
            name: metrics for name, metrics in evaluation_results.items()
        }).T
        
        print("📈 Performance Metrics Summary:\n")
        print(comparison_df.round(4).to_string())
        
        # Rankings
        print("\n\n🥇 Rankings by Test Accuracy:")
        accuracy_ranking = comparison_df['Test Accuracy'].sort_values(ascending=False)
        for i, (model, score) in enumerate(accuracy_ranking.items(), 1):
            print(f"   {i}. {model:20s}: {score:.4f}")
        
        print("\n🥇 Rankings by F1-Score:")
        f1_ranking = comparison_df['F1-Score'].sort_values(ascending=False)
        for i, (model, score) in enumerate(f1_ranking.items(), 1):
            print(f"   {i}. {model:20s}: {score:.4f}")
        
        best_model = accuracy_ranking.idxmax() if len(accuracy_ranking) > 0 else None
        print(f"\n✅ Best Model (by Test Accuracy): {best_model}")
        
        return comparison_df, best_model
    
    def extract_feature_importance(self, feature_names):
        """Extract feature importance from models that support it"""
        print("\n" + "="*60)
        print("🔍 FEATURE IMPORTANCE")
        print("="*60 + "\n")
        
        feature_importance = {}
        
        # Logistic Regression coefficients
        lr_model = self.trained_models.get('Logistic Regression')
        if lr_model:
            coef = np.abs(lr_model.coef_[0])
            importance = (coef / coef.sum()) * 100
            feature_importance['Logistic Regression'] = dict(zip(feature_names, importance))
        
        # SVM coefficients
        svm_model = self.trained_models.get('SVM')
        if svm_model and hasattr(svm_model, 'coef_'):
            coef = np.abs(svm_model.coef_[0])
            importance = (coef / coef.sum()) * 100
            feature_importance['SVM'] = dict(zip(feature_names, importance))
        
        # Display
        if feature_importance:
            print("Feature Importance (Top 5 Features):\n")
            for model_name, importance_dict in feature_importance.items():
                print(f"{model_name}:")
                sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
                for i, (feature, importance) in enumerate(sorted_features[:5], 1):
                    print(f"   {i}. {feature:20s}: {importance:6.2f}%")
                print()
        
        return feature_importance
    
    def save_models(self, output_dir='models'):
        """Save trained models to disk"""
        output_path = Path(__file__).parent / output_dir
        output_path.mkdir(parents=True, exist_ok=True)
        
        for name, model in self.trained_models.items():
            filepath = output_path / f"{name.lower().replace(' ', '_')}.pkl"
            with open(filepath, 'wb') as f:
                pickle.dump(model, f)
            print(f"✅ Saved: {filepath}")
        
        # Save results as JSON
        results_path = output_path / 'results.json'
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"✅ Saved results: {results_path}")

def main():
    """Run complete model training and evaluation"""
    
    # Load processed data
    processed_dir = Path(__file__).parent / 'data' / 'processed'
    
    if not processed_dir.exists():
        print("❌ Processed data not found. Please run preprocessing.py first.")
        return
    
    X_train = pd.read_csv(processed_dir / 'X_train.csv')
    X_test = pd.read_csv(processed_dir / 'X_test.csv')
    y_train = pd.read_csv(processed_dir / 'y_train.csv').squeeze()
    y_test = pd.read_csv(processed_dir / 'y_test.csv').squeeze()
    
    # Initialize trainer
    trainer = ModelTrainer()
    
    # Train models
    trainer.train_models(X_train, y_train)
    
    # Evaluate models
    evaluation_results = trainer.evaluate_all(X_train, X_test, y_train, y_test)
    
    # Compare models
    comparison_df, best_model = trainer.compare_models(evaluation_results)
    
    # Feature importance
    trainer.extract_feature_importance(X_train.columns.tolist())
    
    # Save models
    trainer.save_models()
    
    print("\n" + "="*60)
    print("✅ MODEL TRAINING COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
