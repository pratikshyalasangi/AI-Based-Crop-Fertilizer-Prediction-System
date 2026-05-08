import pandas as pd
import numpy as np
import os
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.utils import to_categorical


DATASET_CSV = "sugarcane_dataset.csv"     
MODEL_PATH = "sugarcane_model.h5"           
LABEL_ENCODER_PATH = "label_encoder.pkl"    
FEATURE_COLUMNS_PATH = "feature_columns.pkl"  


if not os.path.exists(DATASET_CSV):
    raise FileNotFoundError(f"{DATASET_CSV} not found. Place it in the project folder.")

df = pd.read_csv(DATASET_CSV)
print("Columns in dataset:", df.columns.tolist())

features = df.iloc[:, :-1].copy()
labels = df.iloc[:, -1].copy()


numeric_cols = features.select_dtypes(include=['int64', 'float64']).columns
categorical_cols = features.select_dtypes(include=['object']).columns


features[numeric_cols] = features[numeric_cols].apply(pd.to_numeric, errors='coerce')


if len(categorical_cols) > 0:
    features = pd.get_dummies(features, columns=categorical_cols)


df_clean = pd.concat([features, labels], axis=1).dropna()
features = df_clean.iloc[:, :-1]
labels = df_clean.iloc[:, -1]

print(f"Feature shape after processing: {features.shape}")


with open(FEATURE_COLUMNS_PATH, "wb") as f:
    pickle.dump(features.columns.tolist(), f)
print(f"Feature columns saved to {FEATURE_COLUMNS_PATH}")


le = LabelEncoder()
labels_encoded = le.fit_transform(labels)
labels_categorical = to_categorical(labels_encoded)


with open(LABEL_ENCODER_PATH, "wb") as f:
    pickle.dump(le, f)
print(f"Label encoder saved to {LABEL_ENCODER_PATH}")


X_train, X_test, y_train, y_test = train_test_split(
    features.values, labels_categorical, test_size=0.2, random_state=42
)


input_dim = X_train.shape[1]
num_classes = y_train.shape[1]

model = Sequential([
    Input(shape=(input_dim,)),
    Dense(128, activation="relu"),
    Dropout(0.3),
    Dense(64, activation="relu"),
    Dropout(0.2),
    Dense(num_classes, activation="softmax")
])

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
model.summary()


history = model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=16,
    validation_split=0.1,
    verbose=1
)


y_pred = model.predict(X_test)
y_pred_labels = np.argmax(y_pred, axis=1)
y_true_labels = np.argmax(y_test, axis=1)
acc = accuracy_score(y_true_labels, y_pred_labels)
print(f"Test Accuracy: {acc*100:.2f}%")


model.save(MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")
