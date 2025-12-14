# %%

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme()

# %%

"""
## Pre-preprocessing
Before even loading the file, we need to remove trailing commas from each line in a CSV file.
"""

input_path = "sleep.csv"
output_path = "sleep_pre.csv"

with open(input_path, "r", encoding="utf-8") as fin, open(output_path, "w", encoding="utf-8") as fout:
    for line in fin:
        fout.write(line.rstrip(",\n") + "\n")


# %%

data = pd.read_csv('sleep_pre.csv')

# Important variables: 
cols = [
    'sleep_score',
    'sleep_duration',
    'nap_score',
    'physical_recovery',
    'com.samsung.health.sleep.start_time',
    'com.samsung.health.sleep.end_time',
]

features = data.loc[:, cols]

features.rename(
    columns={
        'com.samsung.health.sleep.start_time': 'sleep_start_time',
        'com.samsung.health.sleep.end_time': 'sleep_end_time'
        },
    inplace=True
)

cleaned = features.dropna(subset=['sleep_score']).copy()  # Drops rows where sleep_score is NaN

"""
## Timezone conversion

The sleep start and end times are in UTC timezone. We will convert them to 'America/Santiago' timezone.
"""

cleaned['sleep_start_time'] = pd.to_datetime(cleaned['sleep_start_time'])
cleaned['sleep_end_time'] = pd.to_datetime(cleaned['sleep_end_time'])

cleaned['sleep_start_time'] = (
    cleaned['sleep_start_time']
   .dt.tz_localize('UTC')
    .dt.tz_convert('America/Santiago')
)

cleaned['sleep_end_time'] = (
    cleaned['sleep_end_time']
    .dt.tz_localize('UTC')
    .dt.tz_convert('America/Santiago')
)

"""
## Imputing nap_score
We will impute missing values in the `nap_score` column based on the `sleep_duration` column.

If `sleep_duration` is under 3 hours (180 minutes) or more, we will set `nap_score` to 1 (indicating a nap was taken).
Otherwise, we will set `nap_score` to 0 (indicating no nap was taken) and in fact the person had a full sleep.
"""
mask = cleaned['nap_score'].isna()

cleaned.loc[mask, 'nap_score'] = (
        cleaned.loc[mask, 'sleep_duration'] <= 3 * 60  # 3 hours in minutes
    ).astype(int)

print(cleaned.info())

# Also add a new col 'is_nap' for easier analysis
cleaned['is_nap'] = (cleaned['nap_score'] >= 1).astype(bool)

# %%
cleaned.to_csv('sleep_full_cleaned.csv', index=False)

# %%

sleep_duration_hours = cleaned['sleep_duration'] / 60  # Convert minutes to hours

plot = sns.scatterplot(data=cleaned, x=sleep_duration_hours, y='sleep_score', hue='is_nap', style='is_nap', alpha=0.7)

plot.set_title('Sleep Score vs Sleep Duration')
plot.set_xlabel('Sleep Duration (hours)')
plot.set_ylabel('Sleep Score')

plt.show()

# %%

cleaned_no_naps = cleaned.loc[cleaned['is_nap'] == False]
sleep_duration_hours = cleaned_no_naps['sleep_duration'] / 60  # Convert minutes to hours

plot = sns.histplot(data=cleaned_no_naps, x=sleep_duration_hours, binwidth=1, kde=True)

plot.set_title('Distribution of Sleep Duration (Excluding Naps)')
plot.set_xlabel('Sleep Duration (hours)')
plot.set_ylabel('Count')

plt.show()
