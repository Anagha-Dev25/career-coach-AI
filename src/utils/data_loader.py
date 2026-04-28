import pandas as pd
import os

def get_random_resume(csv_path="data/resumes.csv"):
    try:
        if not os.path.exists(csv_path):
            return {"error": f"File not found: {csv_path}"}

        df = pd.read_csv(csv_path)

        # 1. Detect column names (Kaggle formats vary)
        # We look for common names or just take the first two columns
        text_col = next((c for c in df.columns if 'resume' in c.lower() or 'str' in c.lower()), df.columns[1])
        cat_col = next((c for c in df.columns if 'category' in c.lower() or 'class' in c.lower()), df.columns[0])

        # 2. Only drop rows where the actual RESUME TEXT is empty
        df = df.dropna(subset=[text_col])

        if df.empty:
            return {"error": "The CSV is empty after filtering out missing resumes."}

        # 3. Pick a random row
        row = df.sample(n=1).iloc[0]
        
        # 4. Clean up the output
        category = str(row[cat_col]).strip()
        if category.lower() == 'nan' or not category:
            category = "General Professional"

        return {
            "text": str(row[text_col])[:5000],  # Only take the first 5000 characters
            "category": category
        }
    except Exception as e:
        return {"error": f"Data Loader Error: {e}"}

if __name__ == "__main__":
    # Quick test in CMD
    sample = get_random_resume()
    print(f"Category: {sample['category']}")
    print(f"Text Snippet: {sample['text'][:200]}...")