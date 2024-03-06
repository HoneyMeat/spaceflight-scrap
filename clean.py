import pandas as pd

# Load the existing CSV data
df = pd.read_csv("spaceflight_data.csv")

# Replace all "N/A" values with an empty string
df.replace("N/A", "", inplace=True)

# Write the cleaned data to a new CSV file
df.to_csv("cleaned_spaceflight_data.csv", index=False)

print("Cleaned data saved to cleaned_spaceflight_data.csv")
