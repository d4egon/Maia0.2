
# Filename: /mycelium_core/signal_classifier.py
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

# Example data placeholder
X = np.random.rand(100, 3)  # Features: [rms, spectral_centroid, zero_crossing_rate]
y = np.random.randint(0, 2, 100)  # Labels: 0 = Calm, 1 = Active

def train_classifier(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = SVC(kernel='linear')
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    return model
