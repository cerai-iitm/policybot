import pandas as pd

# Load CSV file
df = pd.read_csv("newTemp_batch_evaluation_Deepseek_20250321_152954.csv")

# Group data by context_id
grouped = df.groupby("context_id")

# Create a list to store formatted text
output_lines = []

# Iterate through contexts
for context_id, group in grouped:
    context_text = group["context"].iloc[0]  # All rows in the group have the same context
    
    # Add Context Header
    output_lines.append(f"# Context: \n")
    output_lines.append(f"{context_text}\n")

    # Iterate through questions and their answers
    for _, row in group.iterrows():
        question = row["question"]
        llm_answer = row["llm_answer"]
        human_answer = row["human_answer"]
        scores = (
            f"Similarity: {row['similarity']}, ROUGE-L: {row['rougeL']}, "
            f"BLEU: {row['bleu']}, METEOR: {row['meteor']}, "
            f"BERT Precision: {row['bert_precision']}, BERT Recall: {row['bert_recall']}, BERT F1: {row['bert_f1']}"
        )

        output_lines.append(f"**Question:** {question}\n")
        output_lines.append(f"**LLM Answer:** {llm_answer}\n")
        output_lines.append(f"**Human Answer:** {human_answer}\n")
        output_lines.append(f"**Scores:** {scores}\n")

    output_lines.append("\n" + "-"*80 + "\n")  # Separator between contexts

# Save to text file
output_text = "\n".join(output_lines)
with open("formatted_output_deepseek.txt", "w", encoding="utf-8") as f:
    f.write(output_text)

print("Formatted text saved to 'formatted_output.txt'. Copy-paste it into Google Docs!")
