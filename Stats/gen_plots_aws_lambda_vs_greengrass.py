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

df_aws_stats = pd.read_csv('AWS_stats.csv', delimiter=',')

alpha = 0.05

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

print("AWS Greengrass overall delay mean: {}".format(df_aws_stats['overall_delay'].mean()))
print("AWS Greengrass overall delay std: {}".format(df_aws_stats['overall_delay'].std()))
print("AWS Greengrass overall delay median: {}".format(df_aws_stats['overall_delay'].median()))
print("AWS Greengrass network delay mean: {}".format(df_aws_stats['network_delay'].mean()))
print("AWS Greengrass network delay std: {}".format(df_aws_stats['network_delay'].std()))
print("AWS Greengrass network delay median: {}".format(df_aws_stats['network_delay'].median()))
print("AWS Greengrass processing delay mean: {}".format(df_aws_stats['processing_delay'].mean()))
print("AWS Greengrass processing delay std: {}".format(df_aws_stats['processing_delay'].std()))
print("AWS Greengrass processing delay median: {}".format(df_aws_stats['processing_delay'].median()))


x = np.arange(0, 500, 1)
df_lambda_stats = pd.read_csv('stats_lambda_1024mb.csv', delimiter=',')


print("AWS Greengrass overall delay skew: {}".format(stats.skew(df_aws_stats['overall_delay'])))
print("AWS Greengrass overall delay kurtosis: {}".format(stats.kurtosis(df_aws_stats['overall_delay'])))
print("AWS Lambda overall delay skew: {}".format(stats.skew(df_lambda_stats['overall_delay'])))
print("AWS Lambda overall delay kurtosis: {}".format(stats.kurtosis(df_lambda_stats['overall_delay'])))




greengrass_vs_lambda_overall_delay = pd.DataFrame({
    'overall_delay': np.concatenate((df_aws_stats['overall_delay'].values, df_lambda_stats['overall_delay'].values)),
    'platform': np.concatenate((['AWS Greengrass'] * 500, ['Azure Lambda'] * 500))
})

greengrass_vs_lambda_processing_delay = pd.DataFrame({
    'processing_delay': np.concatenate((df_aws_stats['processing_delay'].values, df_lambda_stats['processing_delay'].values)),
    'platform': np.concatenate((['AWS Greengrass'] * 500, ['Azure Lambda'] * 500))
})

greengrass_vs_lambda_network_delay = pd.DataFrame({
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

plt.plot(x, df_lambda_stats['overall_delay'], 'r', label='AWS Lambda')
plt.plot(x, df_aws_stats['overall_delay'], 'b', label="AWS Greengrass")
plt.title('Overall delay')
plt.legend()

subplot1 = plt.subplot(132)
subplot1.set_ylim(0.0, 1.5)
subplot1.set_yticks(np.arange(0.0, 1.5, 0.1))
plt.plot(x, df_lambda_stats['network_delay'], 'r', label='AWS Lambda')
plt.plot(x, df_aws_stats['network_delay'], 'b', label="AWS Greengrass")
plt.title('Network delay')
plt.legend()

subplot2 = plt.subplot(133)
subplot2.set_ylim(0.0, 1.5)
subplot2.set_yticks(np.arange(0.0, 1.5, 0.1))
plt.plot(x, df_lambda_stats['processing_delay'], 'r', label='AWS Lambda')
plt.plot(x, df_aws_stats['processing_delay'], 'b', label="AWS Greengrass")
plt.title('Processing delay')
plt.legend()

plt.show()