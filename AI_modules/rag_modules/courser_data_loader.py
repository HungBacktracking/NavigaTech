from llama_index.core import  Document, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import pandas as pd
import re

df = pd.read_json(r"C:\Users\leduc\OneDrive\Desktop\NLP\grab-capstone-project\NavigaTech\AI_modules\data\rag_data\course\it_courses.json", encoding="latin1")
english_alphabet_pattern = re.compile(r'^[a-zA-Z0-9\s!@#$%^&*()_+\-={}[\]:;"\'<>,.?/]+$')
def decode_text(text):
    """
    Attempt to decode corrupted text by trying common encodings.
    """
    try:
        # Decode from Latin-1 to UTF-8
        text = text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    
    return text
def contains_only_english(text):
    text = decode_text(text)
    return bool(english_alphabet_pattern.search(text))
filtered_df = df[df['description'].apply(contains_only_english)]
filtered_df = filtered_df[filtered_df["title"].apply(contains_only_english)]

embbeding_model = HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5")



documents = []
for index, row in filtered_df.iterrows():
    learn = "\n".join(row["what_you_will_learn"])
    merge_text = f"""
    Course name: {row["title"]}
    Skills: {", ".join(row["skills"])}
    What you will learn: 
    {learn}
    Description: {row["description"]}
    """

    meta = {
        "name": row["title"],
        "skills": row["skills"],
        "course_url": row["url"],
        "what_you_will_learn": row["what_you_will_learn"],
        # "description": row["description"],

    }
    doc = Document(text = merge_text, metadata=meta)
    documents.append(doc)

index = VectorStoreIndex.from_documents(documents ,embed_model= embbeding_model ,show_progress=True)
index.storage_context.persist(r"C:\Users\leduc\OneDrive\Desktop\NLP\grab-capstone-project\NavigaTech\AI_modules\rag_modules\course_db")