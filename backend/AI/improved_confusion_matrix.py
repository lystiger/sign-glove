#!/usr/bin/env python3
"""
Improved Confusion Matrix Analysis Script

This script analyzes gesture data to create a more accurate confusion matrix
that properly handles datasets with varying label distributions and edge cases.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import json
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_and_analyze_data(csv_path):
    """Load and analyze the gesture data."""
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded dataset with {len(df)} rows and {len(df.columns)} columns")
        
        # Check if 'label' column exists
        if 'label' not in df.columns:
            raise ValueError("Dataset must contain a 'label' column")
        
        # Analyze label distribution
        label_counts = df['label'].value_counts()
        unique_labels = df['label'].unique()
        
        logger.info(f"Found {len(unique_labels)} unique labels: {list(unique_labels)}")
        logger.info(f"Label distribution:\n{label_counts}")
        
        return df, unique_labels, label_counts
        
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def prepare_features_and_labels(df):
    """Prepare features and labels for training."""
    try:
        # Separate features and labels
        X = df.drop(['label'], axis=1)
        y = df['label']
        
        # Handle non-numeric columns by dropping them or encoding
        numeric_columns = X.select_dtypes(include=[np.number]).columns
        X = X[numeric_columns]
        
        logger.info(f"Using {len(numeric_columns)} numeric features")
        
        # Encode labels
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)
        
        return X, y, y_encoded, label_encoder
        
    except Exception as e:
        logger.error(f"Error preparing features: {e}")
        raise

def train_and_evaluate_model(X, y_encoded, label_encoder):
    """Train model and generate confusion matrix."""
    try:
        unique_labels = len(np.unique(y_encoded))
        
        # Handle single label case
        if unique_labels == 1:
            logger.warning("Dataset contains only one unique label - cannot create meaningful confusion matrix")
            return None, None, None, None, None
        
        # Split data
        test_size = min(0.3, max(0.1, 100 / len(X)))  # Adaptive test size
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
        )
        
        logger.info(f"Training set: {len(X_train)}, Test set: {len(X_test)}")
        
        # Train RandomForest model
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2
        )
        
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)
        
        # Get classification report
        target_names = label_encoder.classes_
        class_report = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
        
        logger.info(f"Model accuracy: {accuracy:.4f}")
        
        return cm, accuracy, class_report, target_names, (y_test, y_pred)
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise

def create_confusion_matrix_plot(cm, labels, accuracy, save_path):
    """Create and save confusion matrix visualization."""
    try:
        plt.figure(figsize=(10, 8))
        
        # Create heatmap
        sns.heatmap(
            cm, 
            annot=True, 
            fmt='d', 
            cmap='Blues',
            xticklabels=labels,
            yticklabels=labels,
            cbar_kws={'label': 'Count'}
        )
        
        plt.title(f'Improved Confusion Matrix\nAccuracy: {accuracy:.4f}', fontsize=16, pad=20)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.ylabel('True Label', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        # Add timestamp
        plt.figtext(0.99, 0.01, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
                   ha='right', va='bottom', fontsize=8, alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Confusion matrix plot saved to {save_path}")
        
    except Exception as e:
        logger.error(f"Error creating plot: {e}")
        raise

def save_results(results_data, save_path):
    """Save detailed results to JSON file."""
    try:
        with open(save_path, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        logger.info(f"Results saved to {save_path}")
        
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        raise

def main():
    """Main execution function."""
    try:
        # Define paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, '..', 'data', 'gesture_data.csv')
        results_dir = os.path.join(base_dir, 'results')
        
        # Create results directory if it doesn't exist
        os.makedirs(results_dir, exist_ok=True)
        
        plot_path = os.path.join(results_dir, 'improved_confusion_matrix.png')
        json_path = os.path.join(results_dir, 'confusion_matrix_results.json')
        
        logger.info("Starting improved confusion matrix analysis...")
        
        # Load and analyze data
        df, unique_labels, label_counts = load_and_analyze_data(csv_path)
        
        # Prepare features and labels
        X, y, y_encoded, label_encoder = prepare_features_and_labels(df)
        
        # Train model and evaluate
        cm, accuracy, class_report, target_names, test_data = train_and_evaluate_model(X, y_encoded, label_encoder)
        
        if cm is None:
            # Handle single label case
            results_data = {
                'status': 'insufficient_data',
                'message': 'Dataset contains only one unique label - cannot create meaningful confusion matrix',
                'labels_found': list(unique_labels),
                'total_samples': len(df),
                'label_distribution': label_counts.to_dict(),
                'timestamp': datetime.now().isoformat()
            }
            
            save_results(results_data, json_path)
            logger.warning("Analysis completed with insufficient data warning")
            return
        
        # Create visualization
        create_confusion_matrix_plot(cm, target_names, accuracy, plot_path)
        
        # Prepare detailed results
        results_data = {
            'status': 'success',
            'accuracy': float(accuracy),
            'labels_found': list(unique_labels),
            'total_samples': len(df),
            'test_samples': len(test_data[0]),
            'confusion_matrix': cm.tolist(),
            'classification_report': class_report,
            'label_distribution': label_counts.to_dict(),
            'feature_count': len(X.columns),
            'timestamp': datetime.now().isoformat()
        }
        
        save_results(results_data, json_path)
        
        logger.info("Improved confusion matrix analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        
        # Save error results
        error_results = {
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }
        
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
        os.makedirs(results_dir, exist_ok=True)
        json_path = os.path.join(results_dir, 'confusion_matrix_results.json')
        
        try:
            save_results(error_results, json_path)
        except:
            pass
        
        raise

if __name__ == "__main__":
    main()
