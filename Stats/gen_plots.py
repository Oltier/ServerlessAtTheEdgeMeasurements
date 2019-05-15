import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import mannwhitneyu, levene


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
alpha = 0.05

print("Azure overall delay mean: {}".format(df_azure_stats['overall_delay'].mean()))
print("Azure overall delay std: {}".format(df_azure_stats['overall_delay'].std()))
print("Azure overall delay median: {}".format(df_azure_stats['overall_delay'].median()))
print("Azure overall delay normaltest p: {}".format(p))
if p < alpha:
    print("The null hypothesis can be rejected for azure, normal distribution")
else:
    print("The null hypothesis cannot be rejected for azure, not normal distribution")


print("Azure network delay mean: {}".format(df_azure_stats['network_delay'].mean()))
print("Azure network delay std: {}".format(df_azure_stats['network_delay'].std()))
print("Azure processing delay mean: {}".format(df_azure_stats['processing_delay'].mean()))
print("Azure processing delay std: {}".format(df_azure_stats['processing_delay'].std()))

df_aws_stats['processing_delay'] = df_aws_stats.apply(calc_processing_delay, axis=1)
df_aws_stats['network_delay'] = df_aws_stats.apply(calc_network_delay_aws, axis=1)
df_aws_stats['overall_delay'] = df_aws_stats.apply(calc_overall_delay, axis=1)

k2_2, p_2 = stats.normaltest(df_aws_stats['overall_delay'])
print("AWS overall delay normaltest p_2: {}".format(p_2))
if p_2 < alpha:
    print("The null hypothesis can be rejected for aws, normal distribution")
else:
    print("The null hypothesis cannot be rejected for aws, not normal distribution")

print("AWS overall delay mean: {}".format(df_aws_stats['overall_delay'].mean()))
print("AWS overall delay std: {}".format(df_aws_stats['overall_delay'].std()))
print("AWS overall delay median: {}".format(df_aws_stats['overall_delay'].median()))
print("AWS network delay mean: {}".format(df_aws_stats['network_delay'].mean()))
print("AWS network delay std: {}".format(df_aws_stats['network_delay'].std()))
print("AWS processing delay mean: {}".format(df_aws_stats['processing_delay'].mean()))
print("AWS processing delay std: {}".format(df_aws_stats['processing_delay'].std()))

alpha_mw = 0.05
stat, p_mw = mannwhitneyu(df_azure_stats['overall_delay'], df_aws_stats['overall_delay'], alternative='two-sided')
print("P_mw: {}".format(p_mw))
if p_mw > alpha_mw:
    print('Same distribution (fail to reject H0)')
else:
    print('Different distribution (reject H0)')


stats_levene, p_levene = levene(df_azure_stats['overall_delay'], df_aws_stats['overall_delay'])

alpha_levene = 0.05
print("P_levene: {}".format(p_levene))
if p_levene > alpha_levene:
    print('Accept H0, same variance')
else:
    print('Reject H0, different variance')

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

fig, ax = plt.subplots(nrows=3, figsize=(10, 20))
fig.tight_layout()
overall_delay_fig = sns.boxplot('platform', 'overall_delay', data=overall_delay, ax=ax[0])
overall_delay_fig.set(title="Overall latency by platform", xlabel='Platform', ylabel='Overall latency (s)')
processing_delay_fig = sns.boxplot('platform', 'processing_delay', data=processing_delay, ax=ax[1])
processing_delay_fig.set(title="Processing latency by platform", xlabel='Platform', ylabel='Processing latency (s)')
network_delay_fig = sns.boxplot('platform', 'network_delay', data=network_delay, ax=ax[2])
network_delay_fig.set(title="Network latency by platform", xlabel='Platform', ylabel='Network latency (s)')
plt.savefig('plots.png')
plt.show()
