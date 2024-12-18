import pandas as pd


input_file = '2Milestone/adultAdded.csv'  
output_file = 'deploy/cleaned_adultAdded1.csv'  


df = pd.read_csv(input_file)

df_cleaned = df.drop_duplicates(subset='title', keep='first')

#save the cleaned data to a new file
df_cleaned.to_csv(output_file, index=False)

print(f"Duplicates removed. Cleaned file saved to {output_file}")
