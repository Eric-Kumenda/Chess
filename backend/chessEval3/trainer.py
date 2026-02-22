# import csv
# import numpy as np

# cleaned_rows = []

# # Read and clean the CSV manually
# with open('games.csv', 'r', encoding='utf-8') as f:
#     reader = csv.reader(f)
#     header = next(reader)  # skip header
#     for row in reader:
#         if len(row) == 16:
#             cleaned_rows.append(row)

# # Convert to NumPy array
# data = np.array(cleaned_rows)

# # Select first 10 rows and the desired columns
# selected = data[:10, [1, 5, 6, 9, 11, 12]]

# # Display
# # for row in selected:
# #     print(row)

# print(selected[0])

import pandas as pd

# Load the CSV file
df = pd.read_csv('games.csv')

# Select first 10 rows and specific columns
selected = df.loc[:9, ['rated', 'victory_status', 'winner', 'white_rating', 'black_rating', 'moves']]

print(selected.moves)
