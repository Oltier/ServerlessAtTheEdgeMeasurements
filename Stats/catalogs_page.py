import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def calc_overall_delay(row):
    return row['processing_delay'] + row['network_delay']


df_no_limit_stats = pd.read_csv('no_limit.csv', delimiter=',')
df_with_limit_stats = pd.read_csv('with_limit.csv', delimiter=',')

overall_delay = pd.DataFrame({
    'overall_delay': np.concatenate(
        (df_no_limit_stats['response_time'].values,
         df_with_limit_stats['response_time'].values)
    ),
    'platform': np.concatenate((['Catalogs list No limit (default limit=25)'] * 100, ['Catalogs list With Limit of 500'] * 100))
})

plt.figure(1)
fig, ax = plt.subplots(nrows=1, figsize=(20, 20))
fig.tight_layout()
overall_delay_fig = sns.boxplot('platform', 'overall_delay', data=overall_delay, ax=ax)
overall_delay_fig.set(
    title="Overall response_time by limit option (n=100)",
    xlabel='Platform',
    ylabel='Overall response_time (ms)'
)
plt.savefig('plots.png')
plt.show()
