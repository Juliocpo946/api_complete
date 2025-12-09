import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, 
    roc_curve, precision_recall_curve, f1_score, precision_score, recall_score
)
import joblib
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    df = pd.read_csv('../output/abandonment_features.csv')
    print(f"Datos cargados: {df.shape}")
    return df

def prepare_features(df):
    target = 'abandoned'
    exclude_cols = ['activity_uuid', 'user_id', 'external_activity_id', 'abandoned', 'cluster_name']
    
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols].copy()
    y = df[target].copy()
    
    print(f"\nFeatures seleccionadas: {len(feature_cols)}")
    print(f"Target distribution:")
    print(y.value_counts())
    print(f"Abandonment rate: {y.mean():.2%}")
    
    return X, y, feature_cols

def train_random_forest(X_train, y_train, X_test, y_test):
    print("\n" + "="*60)
    print("ENTRENANDO RANDOM FOREST")
    print("="*60)
    
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    
    y_pred = rf.predict(X_test)
    y_proba = rf.predict_proba(X_test)[:, 1]
    
    print("\nMétricas en Test Set:")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.4f}")
    print(f"F1-Score: {f1_score(y_test, y_pred):.4f}")
    
    return rf, y_proba

def train_xgboost(X_train, y_train, X_test, y_test):
    print("\n" + "="*60)
    print("ENTRENANDO XGBOOST")
    print("="*60)
    
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    
    xgb = XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        n_jobs=-1,
        eval_metric='logloss'
    )
    xgb.fit(X_train, y_train)
    
    y_pred = xgb.predict(X_test)
    y_proba = xgb.predict_proba(X_test)[:, 1]
    
    print("\nMétricas en Test Set:")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.4f}")
    print(f"F1-Score: {f1_score(y_test, y_pred):.4f}")
    
    return xgb, y_proba

# Reemplazar función plot_feature_importance en train_abandonment_model.py:

def plot_feature_importance(model, feature_names, model_name):
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        top_n = min(20, len(indices))
        top_indices = indices[:top_n]
        
        plt.figure(figsize=(12, 8))
        plt.title(f'Top {top_n} Feature Importances - {model_name}')
        plt.barh(range(top_n), importances[top_indices])
        plt.yticks(range(top_n), [feature_names[i] for i in top_indices])
        plt.xlabel('Importance')
        plt.tight_layout()
        plt.savefig(f'../output/feature_importance_{model_name.lower().replace(" ", "_")}.png', dpi=300)
        plt.close()
        
        print(f"\nTop 10 features - {model_name}:")
        for i in range(min(10, len(indices))):
            print(f"{i+1}. {feature_names[indices[i]]}: {importances[indices[i]]:.4f}")
            
def plot_roc_curve(y_test, y_proba_rf, y_proba_xgb):
    plt.figure(figsize=(10, 8))
    
    fpr_rf, tpr_rf, _ = roc_curve(y_test, y_proba_rf)
    fpr_xgb, tpr_xgb, _ = roc_curve(y_test, y_proba_xgb)
    
    plt.plot(fpr_rf, tpr_rf, label=f'Random Forest (AUC = {roc_auc_score(y_test, y_proba_rf):.4f})', linewidth=2)
    plt.plot(fpr_xgb, tpr_xgb, label=f'XGBoost (AUC = {roc_auc_score(y_test, y_proba_xgb):.4f})', linewidth=2)
    plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
    
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curves - Abandonment Prediction')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('../output/roc_curves_abandonment.png', dpi=300)
    plt.close()

def plot_confusion_matrix(y_test, y_pred, model_name):
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
    plt.title(f'Confusion Matrix - {model_name}')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(f'../output/confusion_matrix_{model_name.lower().replace(" ", "_")}.png', dpi=300)
    plt.close()

def save_model(model, scaler, feature_cols, metrics, model_name):
    joblib.dump(model, '../models/abandonment_classifier.pkl')
    joblib.dump(scaler, '../models/abandonment_scaler.pkl')
    
    metadata = {
        'model_type': model_name,
        'features': feature_cols,
        'n_features': len(feature_cols),
        'metrics': {
            'roc_auc': float(metrics['roc_auc']),
            'f1_score': float(metrics['f1_score']),
            'precision': float(metrics['precision']),
            'recall': float(metrics['recall'])
        },
        'trained_on': datetime.now().isoformat(),
        'target': 'abandoned'
    }
    
    with open('../models/abandonment_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n{'='*60}")
    print("MODELO GUARDADO")
    print(f"{'='*60}")
    print("  - models/abandonment_classifier.pkl")
    print("  - models/abandonment_scaler.pkl")
    print("  - models/abandonment_metadata.json")

def main():
    df = load_data()
    X, y, feature_cols = prepare_features(df)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTrain set: {X_train.shape}")
    print(f"Test set: {X_test.shape}")
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    rf_model, y_proba_rf = train_random_forest(X_train_scaled, y_train, X_test_scaled, y_test)
    xgb_model, y_proba_xgb = train_xgboost(X_train_scaled, y_train, X_test_scaled, y_test)
    
    plot_feature_importance(rf_model, feature_cols, "Random Forest")
    plot_feature_importance(xgb_model, feature_cols, "XGBoost")
    
    plot_roc_curve(y_test, y_proba_rf, y_proba_xgb)
    
    y_pred_rf = rf_model.predict(X_test_scaled)
    y_pred_xgb = xgb_model.predict(X_test_scaled)
    
    plot_confusion_matrix(y_test, y_pred_rf, "Random Forest")
    plot_confusion_matrix(y_test, y_pred_xgb, "XGBoost")
    
    roc_auc_rf = roc_auc_score(y_test, y_proba_rf)
    roc_auc_xgb = roc_auc_score(y_test, y_proba_xgb)
    
    print(f"\n{'='*60}")
    print("COMPARACIÓN FINAL")
    print(f"{'='*60}")
    print(f"Random Forest ROC-AUC: {roc_auc_rf:.4f}")
    print(f"XGBoost ROC-AUC: {roc_auc_xgb:.4f}")
    
    if roc_auc_xgb > roc_auc_rf:
        print("\nMejor modelo: XGBoost")
        best_model = xgb_model
        best_name = "XGBoost"
        y_pred_best = y_pred_xgb
        y_proba_best = y_proba_xgb
    else:
        print("\nMejor modelo: Random Forest")
        best_model = rf_model
        best_name = "Random Forest"
        y_pred_best = y_pred_rf
        y_proba_best = y_proba_rf
    
    metrics = {
        'roc_auc': roc_auc_score(y_test, y_proba_best),
        'f1_score': f1_score(y_test, y_pred_best),
        'precision': precision_score(y_test, y_pred_best),
        'recall': recall_score(y_test, y_pred_best)
    }
    
    save_model(best_model, scaler, feature_cols, metrics, best_name)
    
    print(f"\n{'='*60}")
    print("ENTRENAMIENTO COMPLETADO")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()