#using bert-base-uncased to predict the "importance" field of given requirement
#datasets used: r"ModelTraining\integration_requirements_dataset.json",
#    r"ModelTraining\regulatory_compliance_dataset.json",
#    r"ModelTraining\user_centric_requirements_dataset.json"

# Step 1: Convert JSON files to CSV
import json
import pandas as pd
import os

files = [
    r"AnalytiCrew-s-Biz-Analyst\analytiCrew-ai-requirements-system\backend\models\integration_requirements_dataset.json",
    r"AnalytiCrew-s-Biz-Analyst\analytiCrew-ai-requirements-system\backend\models\regulatory_compliance_dataset.json",
    r"AnalytiCrew-s-Biz-Analyst\analytiCrew-ai-requirements-system\backend\models\user_centric_requirements_dataset.json"
]

data = []
for file in files:
    with open(file, "r", encoding="utf-8") as f:
        items = json.load(f)
        for item in items:
            sentence = item["text"]
            importance = item["entities"][0]["importance"]
            data.append({"sentence": sentence, "importance": importance})

df = pd.DataFrame(data)
df.to_csv("importance_dataset.csv", index=False)

# Step 2: Map Importance to MoSCoW Category
def importance_to_moscow(importance):
    return {
        "High": "Must have",
        "Medium": "Should have",
        "Low": "Could have"
    }.get(importance, "Could have")

df["moscow_category"] = df["importance"].map(importance_to_moscow)
df.to_csv("moscow_classification_dataset.csv", index=False)

# Step 3: Fine-tune BERT to classify importance
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer, DataCollatorWithPadding
from sklearn.preprocessing import LabelEncoder
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import joblib

# Encode importance labels
label_encoder = LabelEncoder()
df["label"] = label_encoder.fit_transform(df["importance"])
dataset = Dataset.from_pandas(df[["sentence", "label"]])

# Tokenize
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
dataset = dataset.map(lambda e: tokenizer(e["sentence"], truncation=True), batched=True)

# Split
dataset = dataset.train_test_split(test_size=0.3)
train_dataset = dataset["train"]
test_dataset = dataset["test"]

# Load BERT
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=3)
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# Metrics
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average="weighted")
    acc = accuracy_score(labels, predictions)
    return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}

# Training args
training_args = TrainingArguments(
    output_dir="./importance_classifier",
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    learning_rate=2e-5,
    num_train_epochs=5,
    weight_decay=0.01,
    logging_dir="./logs",
    report_to="none"
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics
)

# Train model
trainer.train()

# Save model/tokenizer/label encoder
model.save_pretrained("./importance_classifier")
tokenizer.save_pretrained("./importance_classifier")
joblib.dump(label_encoder, "label_encoder.joblib")

# Step 4: Predict Importance → MoSCoW category
preds = trainer.predict(test_dataset)
pred_labels = np.argmax(preds.predictions, axis=1)
decoded_labels = label_encoder.inverse_transform(pred_labels)
moscow_preds = [importance_to_moscow(imp) for imp in decoded_labels]

output_df = pd.DataFrame({
    "sentence": test_dataset["sentence"],
    "predicted_importance": decoded_labels,
    "moscow_category": moscow_preds
})
output_df.to_csv("predicted_moscow_output.csv", index=False)
print("✅ Output saved to 'predicted_moscow_output.csv'")
print("✅ Model, tokenizer, and label encoder saved successfully.")
