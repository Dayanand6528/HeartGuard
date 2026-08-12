import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

def generate_kaggle_heart_dataset(filepath):
    """Generates synthetic dataset following Kaggle UCI Heart Disease Dataset distributions."""
    np.random.seed(42)
    n_samples = 500

    age = np.random.randint(29, 78, n_samples)
    sex = np.random.choice([0, 1], n_samples, p=[0.32, 0.68]) # 0: Female, 1: Male
    cp = np.random.choice([0, 1, 2, 3], n_samples, p=[0.47, 0.17, 0.28, 0.08]) # Chest pain type (0-3)
    trestbps = np.random.randint(94, 200, n_samples) # Resting blood pressure
    chol = np.random.randint(126, 564, n_samples) # Serum cholesterol in mg/dl
    fbs = np.random.choice([0, 1], n_samples, p=[0.85, 0.15]) # Fasting blood sugar > 120 mg/dl
    restecg = np.random.choice([0, 1, 2], n_samples, p=[0.48, 0.50, 0.02])
    thalach = np.random.randint(71, 202, n_samples) # Max heart rate achieved
    exang = np.random.choice([0, 1], n_samples, p=[0.67, 0.33]) # Exercise induced angina
    oldpeak = np.round(np.random.uniform(0.0, 6.2, n_samples), 1) # ST depression
    slope = np.random.choice([0, 1, 2], n_samples, p=[0.07, 0.46, 0.47])
    ca = np.random.choice([0, 1, 2, 3, 4], n_samples, p=[0.58, 0.21, 0.12, 0.07, 0.02]) # Major vessels
    thal = np.random.choice([0, 1, 2, 3], n_samples, p=[0.01, 0.06, 0.54, 0.39])

    # Calculate realistic target based on clinical risk factors
    risk_score = (
        (age > 55).astype(int) * 1.2 +
        (cp > 0).astype(int) * 2.5 +
        (trestbps > 140).astype(int) * 1.5 +
        (chol > 240).astype(int) * 1.2 +
        (thalach < 140).astype(int) * 1.8 +
        (exang == 1).astype(int) * 2.2 +
        (oldpeak > 1.5).astype(int) * 2.0 +
        (ca > 0).astype(int) * 2.1 +
        (thal == 3).astype(int) * 1.5
    )

    # Probabilistic heart disease presence
    prob = 1 / (1 + np.exp(-(risk_score - 6.5)))
    target = (np.random.rand(n_samples) < prob).astype(int)

    df = pd.DataFrame({
        'age': age,
        'sex': sex,
        'cp': cp,
        'trestbps': trestbps,
        'chol': chol,
        'fbs': fbs,
        'restecg': restecg,
        'thalach': thalach,
        'exang': exang,
        'oldpeak': oldpeak,
        'slope': slope,
        'ca': ca,
        'thal': thal,
        'target': target
    })

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"Dataset saved successfully to {filepath} ({len(df)} records)")
    return df

def train_and_save_model():
    dataset_path = os.path.join('dataset', 'heart.csv')
    if not os.path.exists(dataset_path):
        df = generate_kaggle_heart_dataset(dataset_path)
    else:
        df = pd.read_csv(dataset_path)

    X = df.drop('target', axis=1)
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)

    print(f"Model Training Complete!")
    print(f"Accuracy: {acc * 100:.2f}%")
    print(classification_report(y_test, y_pred))

    model_dir = 'models'
    os.makedirs(model_dir, exist_ok=True)

    with open(os.path.join(model_dir, 'model.pkl'), 'wb') as f:
        pickle.dump(model, f)

    with open(os.path.join(model_dir, 'scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)

    print(f"Model and Scaler saved in '{model_dir}' directory.")

if __name__ == '__main__':
    train_and_save_model()
