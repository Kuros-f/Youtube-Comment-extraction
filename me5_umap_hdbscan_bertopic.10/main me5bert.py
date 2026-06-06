import pandas as pd
import re
import os

from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN

# =========================
# PATHS
# =========================

INPUT_FILE = "comments.xlsx"
OUTPUT_FOLDER = "data"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

# =========================
# LOAD DATA
# =========================

print("Loading dataset...")

df = pd.read_excel(INPUT_FILE)

print("Original shape:", df.shape)

# =========================
# PREPROCESSING
# =========================

# remove null values
df = df[df["text"].notna()]

# convert to string and strip spaces
df["text"] = df["text"].astype(str).str.strip()

# remove empty rows
df = df[df["text"] != ""]

# remove URLs
df["text"] = df["text"].str.replace(
    r"http\S+|www\S+",
    "",
    regex=True
)

# normalize spaces
df["text"] = df["text"].str.replace(
    r"\s+",
    " ",
    regex=True
)

# remove duplicates
df = df.drop_duplicates(subset=["text"])

# remove very short comments
df = df[
    df["text"].str.split().str.len() >= 3
]

# remove emoji-only / symbol-only comments
df = df[
    df["text"].str.contains(
        r"[^\W\d_]",
        regex=True
    )
]

# reset index
df = df.reset_index(drop=True)

print("Cleaned shape:", df.shape)

# =========================
# TEXT LIST
# =========================

texts = df["text"].tolist()

# =========================
# EMBEDDING MODEL
# =========================

print("Loading embedding model...")

model = SentenceTransformer(
    "intfloat/multilingual-e5-base"
)

# =========================
# GENERATE EMBEDDINGS
# =========================

print("Generating embeddings...")

embeddings = model.encode(
    texts,
    batch_size=8,
    show_progress_bar=True
)

print("Embeddings shape:", embeddings.shape)

# =========================
# UMAP
# =========================

print("Creating UMAP model...")

umap_model = UMAP(
    n_neighbors=15,
    n_components=5,
    min_dist=0.0,
    metric="cosine",
    random_state=42
)

# =========================
# HDBSCAN
# =========================

print("Creating HDBSCAN model...")

hdbscan_model = HDBSCAN(
    min_cluster_size=50,
    metric="euclidean",
    cluster_selection_method="eom",
    prediction_data=True
)

# =========================
# BERTopic
# =========================

print("Creating BERTopic model...")

topic_model = BERTopic(
    embedding_model=model,
    umap_model=umap_model,
    hdbscan_model=hdbscan_model,
    nr_topics=10,
    verbose=True
)

# =========================
# FIT MODEL
# =========================

print("Fitting BERTopic model...")

topics, probs = topic_model.fit_transform(
    texts,
    embeddings
)

print("Topic modeling completed.")

# =========================
# TOPIC INFO
# =========================

topic_info = topic_model.get_topic_info()

print("\nTOPIC INFO:")
print(topic_info)

# save topic summary
topic_info.to_excel(
    f"{OUTPUT_FOLDER}/topic_summary.xlsx",
    index=False
)

print("\nSaved topic_summary.xlsx")

# =========================
# AUTOMATIC TOPIC LABELS
# =========================

topic_labels = {}

for topic_id in topic_info["Topic"]:

    if topic_id == -1:
        topic_labels[topic_id] = "Uncategorized"
        continue

    words = topic_model.get_topic(topic_id)

    if words is None:
        topic_labels[topic_id] = f"topic_{topic_id}"
        continue

    # take top 4 semantic words
    top_words = [word for word, _ in words[:4]]

    # generate automatic label
    label = "_".join(top_words)

    topic_labels[topic_id] = label

    print(f"Topic {topic_id} -> {label}")

# =========================
# SAVE FULL RESULTS
# =========================

results_df = pd.DataFrame({
    "text": texts,
    "topic": topics
})

# add topic labels
results_df["topic_label"] = results_df["topic"].map(
    topic_labels
)

# add topic confidence scores
results_df["confidence"] = probs

# save full results
results_df.to_excel(
    f"{OUTPUT_FOLDER}/all_topics_full.xlsx",
    index=False
)

print("\nSaved all_topics_full.xlsx")

# =========================
# CREATE OUTPUT FOLDER
# =========================

topic_folder = f"{OUTPUT_FOLDER}/topic_files"

os.makedirs(
    topic_folder,
    exist_ok=True
)

# =========================
# SAVE EACH TOPIC SEPARATELY
# =========================

print("\nSaving separate topic files...")

unique_topics = results_df["topic"].unique()

for topic_id in unique_topics:

    topic_df = results_df[
        results_df["topic"] == topic_id
    ]

    label_name = topic_labels[topic_id]

    safe_name = (
        label_name
        .replace(" ", "_")
        .replace("/", "_")
        .replace(":", "")
    )

    filename = f"topic_{topic_id}_{safe_name}.xlsx"

    filepath = os.path.join(
        topic_folder,
        filename
    )

    topic_df.to_excel(
        filepath,
        index=False
    )

    print(f"Saved: {filename}")

# =========================
# REPRESENTATIVE DOCUMENTS
# =========================

rep_docs = []

for topic_id in topic_info["Topic"]:

    if topic_id == -1:
        continue

    docs = topic_model.get_representative_docs(topic_id)

    if docs is None:
        continue

    for doc in docs[:5]:

        rep_docs.append({
            "topic_id": topic_id,
            "topic_label": topic_labels[topic_id],
            "document": doc
        })

rep_df = pd.DataFrame(rep_docs)

rep_df.to_excel(
    f"{OUTPUT_FOLDER}/representative_docs.xlsx",
    index=False
)

print("\nSaved representative_docs.xlsx")

# =========================
# DONE
# =========================

print("\nSUCCESS")