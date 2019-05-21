import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import mannwhitneyu, levene, rankdata, tiecorrect


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
print("Stat normal test azure: {}".format(k2))

print("Azure network delay mean: {}".format(df_azure_stats['network_delay'].mean()))
print("Azure network delay std: {}".format(df_azure_stats['network_delay'].std()))
print("Azure network delay median: {}".format(df_azure_stats['network_delay'].median()))
print("Azure processing delay mean: {}".format(df_azure_stats['processing_delay'].mean()))
print("Azure processing delay std: {}".format(df_azure_stats['processing_delay'].std()))
print("Azure processing delay median: {}".format(df_azure_stats['processing_delay'].median()))

df_aws_stats['processing_delay'] = df_aws_stats.apply(calc_processing_delay, axis=1)
df_aws_stats['network_delay'] = df_aws_stats.apply(calc_network_delay_aws, axis=1)
df_aws_stats['overall_delay'] = df_aws_stats.apply(calc_overall_delay, axis=1)

k2_2, p_2 = stats.normaltest(df_aws_stats['overall_delay'])
print("AWS overall delay normaltest p_2: {}".format(p_2))
if p_2 < alpha:
    print("The null hypothesis can be rejected for aws, normal distribution")
else:
    print("The null hypothesis cannot be rejected for aws, not normal distribution")

print("Stat normal test aws: {}".format(k2_2))

print("AWS overall delay mean: {}".format(df_aws_stats['overall_delay'].mean()))
print("AWS overall delay std: {}".format(df_aws_stats['overall_delay'].std()))
print("AWS overall delay median: {}".format(df_aws_stats['overall_delay'].median()))
print("AWS network delay mean: {}".format(df_aws_stats['network_delay'].mean()))
print("AWS network delay std: {}".format(df_aws_stats['network_delay'].std()))
print("AWS network delay median: {}".format(df_aws_stats['network_delay'].median()))
print("AWS processing delay mean: {}".format(df_aws_stats['processing_delay'].mean()))
print("AWS processing delay std: {}".format(df_aws_stats['processing_delay'].std()))
print("AWS processing delay median: {}".format(df_aws_stats['processing_delay'].median()))

alpha_mw = 0.05
stat_mw, p_mw = mannwhitneyu(df_azure_stats['overall_delay'], df_aws_stats['overall_delay'], alternative='two-sided')
print("P_mw: {}".format(p_mw))
if p_mw > alpha_mw:
    print('Same distribution (fail to reject H0)')
else:
    print('Different distribution (reject H0)')

print("Stat Mann-whitney: {}".format(stat_mw))

len_overall_delay_azure = len(df_azure_stats['overall_delay'])
len_overall_delay_aws = len(df_aws_stats['overall_delay'])

m_u = len_overall_delay_azure * len_overall_delay_aws / 2
sigma_u = np.sqrt(len_overall_delay_azure * len_overall_delay_aws * (len_overall_delay_azure + len_overall_delay_aws + 1) / 12)

z = (stat_mw - m_u) / sigma_u

print("z Mann-whitney: {}".format(z))

r = z / np.sqrt(len_overall_delay_azure + len_overall_delay_aws)

print("r Mann-whitney: {}".format(r))

x = np.asarray(df_azure_stats['overall_delay'])
y = np.asarray(df_aws_stats['overall_delay'])
n1 = len(x)
n2 = len(y)
ranked = rankdata(np.concatenate((x, y)))
rankx = ranked[0:n1]  # get the x-ranks
ranky = ranked[n1:]

meanrank = n1*n2/2.0 + 0.5
rankx_mean = np.mean(rankx)
ranky_mean = np.mean(ranky)

print("Mann-whitney rankx mean: {}".format(rankx_mean))
print("Mann-whitney ranky mean: {}".format(ranky_mean))


stats_levene, p_levene = levene(df_azure_stats['overall_delay'], df_aws_stats['overall_delay'])

alpha_levene = 0.05
print("P_levene: {}".format(p_levene))
if p_levene > alpha_levene:
    print('Accept H0, same variance')
else:
    print('Reject H0, different variance')

print("Stat Levene: {}".format(stats_levene))

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

df_azure_stats.to_csv('./azure_formatted_stats.csv', header=True)
df_aws_stats.to_csv('./aws_formatted_stats.csv', header=True)

plt.figure(1)
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

x = np.arange(0, 500, 1)
df_lambda_stats = pd.read_csv('stats_lambda_1024mb.csv', delimiter=',')
lambda_overall_delay = pd.DataFrame({
    'overall_delay': np.concatenate((df_aws_stats['overall_delay'].values, df_lambda_stats['overall_delay'].values)),
    'platform': np.concatenate((['AWS Greengrass'] * 500, ['Azure Lambda'] * 500))
})

lambda_processing_delay = pd.DataFrame({
    'processing_delay': np.concatenate((df_aws_stats['processing_delay'].values, df_lambda_stats['processing_delay'].values)),
    'platform': np.concatenate((['AWS Greengrass'] * 500, ['Azure Lambda'] * 500))
})

lambda_network_delay = pd.DataFrame({
    'network_delay': np.concatenate((df_aws_stats['network_delay'].values, df_lambda_stats['network_delay'].values)),
    'platform': np.concatenate((['AWS Greengrass'] * 500, ['Azure Lambda'] * 500))
})

plt.figure(2)
fig, ax = plt.subplots(ncols=3, figsize=(30, 10))

fig.tight_layout()
subplot0 = plt.subplot(131)
subplot0.set_ylim(0.0, 1.5)
subplot0.set_yticks(np.arange(0.0, 1.5, 0.1))
fig.tight_layout()

plt.plot(x, df_lambda_stats['overall_delay'], 'r', label='AWS Lambda (Cloud)')
plt.plot(x, df_aws_stats['overall_delay'], 'b', label="AWS Greengrass (Edge)")
plt.title('Overall delay')
plt.legend()

subplot1 = plt.subplot(132)
subplot1.set_ylim(0.0, 1.5)
subplot1.set_yticks(np.arange(0.0, 1.5, 0.1))
plt.plot(x, df_lambda_stats['network_delay'], 'r', label='AWS Lambda (Cloud)')
plt.plot(x, df_aws_stats['network_delay'], 'b', label="AWS Greengrass (Edge)")
plt.title('Network delay')
plt.legend()

subplot2 = plt.subplot(133)
subplot2.set_ylim(0.0, 1.5)
subplot2.set_yticks(np.arange(0.0, 1.5, 0.1))
plt.plot(x, df_lambda_stats['processing_delay'], 'r', label='AWS Lambda (Cloud)')
plt.plot(x, df_aws_stats['processing_delay'], 'b', label="AWS Greengrass (Edge)")
plt.title('Processing delay')
plt.legend()

plt.show()