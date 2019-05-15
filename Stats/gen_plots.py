import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats


def calc_processing_delay(row):
    return row['processing_end_time'] - row['processing_start_time']


def calc_network_delay_aws(row):
    return row['message_arrived'] - row['message_sent'] - row['processing_delay']


def calc_network_delay_azure(row):
    return row['message_arrived'] - row['message_sent']


def calc_overall_delay(row):
    return row['processing_delay'] + row['network_delay']


df_azure_stats = pd.read_csv('azure_stats.csv', delimiter=',')
df_aws_stats = pd.read_csv('AWS_stats.csv', delimiter=',')

df_azure_stats['processing_delay'] = df_azure_stats.apply(calc_processing_delay, axis=1)
df_azure_stats['network_delay'] = df_azure_stats.apply(calc_network_delay_azure, axis=1)
df_azure_stats['overall_delay'] = df_azure_stats.apply(calc_overall_delay, axis=1)
k2, p = stats.normaltest(df_azure_stats['overall_delay'])
alpha = 1e-3

print("Azure overall delay mean: {}".format(df_azure_stats['overall_delay'].mean()))
print("Azure overall delay std: {}".format(df_azure_stats['overall_delay'].std()))
print("Azure overall delay normaltest p: {}".format(p))
if p < alpha:
    print("The null hypothesis can be rejected")
else:
    print("The null hypothesis cannot be rejected")
print("Azure network delay mean: {}".format(df_azure_stats['network_delay'].mean()))
print("Azure network delay std: {}".format(df_azure_stats['network_delay'].std()))
print("Azure processing delay mean: {}".format(df_azure_stats['processing_delay'].mean()))
print("Azure processing delay std: {}".format(df_azure_stats['processing_delay'].std()))

df_aws_stats['processing_delay'] = df_aws_stats.apply(calc_processing_delay, axis=1)
df_aws_stats['network_delay'] = df_aws_stats.apply(calc_network_delay_aws, axis=1)
df_aws_stats['overall_delay'] = df_aws_stats.apply(calc_overall_delay, axis=1)

print("AWS overall delay mean: {}".format(df_aws_stats['overall_delay'].mean()))
print("AWS overall delay std: {}".format(df_aws_stats['overall_delay'].std()))
print("AWS network delay mean: {}".format(df_aws_stats['network_delay'].mean()))
print("AWS network delay std: {}".format(df_aws_stats['network_delay'].std()))
print("AWS processing delay mean: {}".format(df_aws_stats['processing_delay'].mean()))
print("AWS processing delay std: {}".format(df_aws_stats['processing_delay'].std()))

overall_delay = pd.DataFrame({
    'overall_delay': np.concatenate((df_aws_stats['overall_delay'].values, df_azure_stats['overall_delay'].values)),
    'platform': np.concatenate((['AWS Greengrass'] * 500, ['Azure IoT Edge'] * 500))
})

processing_delay = pd.DataFrame({
    'processing_delay': np.concatenate((df_aws_stats['processing_delay'].values, df_azure_stats['processing_delay'].values)),
    'platform': np.concatenate((['AWS Greengrass'] * 500, ['Azure IoT Edge'] * 500))
})

network_delay = pd.DataFrame({
    'network_delay': np.concatenate((df_aws_stats['network_delay'].values, df_azure_stats['network_delay'].values)),
    'platform': np.concatenate((['AWS Greengrass'] * 500, ['Azure IoT Edge'] * 500))
})

fig, ax = plt.subplots(nrows=3, figsize=(10, 5))
fig.tight_layout()
overall_delay_fig = sns.boxplot('platform', 'overall_delay', data=overall_delay, ax=ax[0])
overall_delay_fig.set(title="Overall delay by platform", xlabel='Platform', ylabel='Overall delay (ms)')
processing_delay_fig = sns.boxplot('platform', 'processing_delay', data=processing_delay, ax=ax[1])
processing_delay_fig.set(title="Processing delay by platform", xlabel='Platform', ylabel='Processing delay (ms)')
network_delay_fig = sns.boxplot('platform', 'network_delay', data=network_delay, ax=ax[2])
network_delay_fig.set(title="Network delay by platform", xlabel='Platform', ylabel='Network delay (ms)')
plt.savefig('plots.png')
plt.show()
