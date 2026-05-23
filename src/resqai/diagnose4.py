import pandas as pd
from sklearn.metrics import classification_report
import joblib
from .train import split_dataset
from .model import load_dataset, load_model

data = load_dataset()
train_data, test_data = split_dataset(data)

model = load_model()
predictions = model.predict(test_data["metin"])

test_data["tahmin"] = predictions
misclassified = test_data[test_data["niyet"] != test_data["tahmin"]]

print("Hatalı Sınıflandırılan Örnekler:")
for idx, row in misclassified.iterrows():
    print(f"Metin: '{row['metin']}' | Gerçek: '{row['niyet']}' | Tahmin: '{row['tahmin']}'")
