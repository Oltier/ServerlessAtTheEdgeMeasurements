import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.anova import AnovaRM
from statsmodels.stats.multicomp import MultiComparison
from statsmodels.formula.api import ols
import pyvttbl as pt
from collections import namedtuple


def calc_processing_delay(row):
    return row['processing_end_time'] - row['processing_start_time']


def calc_network_delay_aws(row):
    return row['message_arrived'] - row['message_sent'] - row['processing_delay']


def calc_network_delay_azure(row):
    return row['message_arrived'] - row['message_sent']


def calc_overall_delay(row):
    return row['processing_delay'] + row['network_delay']


df_greengrass_stats = pd.read_csv('AWS_stats.csv', delimiter=',')

alpha = 0.05

df_greengrass_stats['processing_delay'] = df_greengrass_stats.apply(calc_processing_delay, axis=1)
df_greengrass_stats['network_delay'] = df_greengrass_stats.apply(calc_network_delay_aws, axis=1)
df_greengrass_stats['overall_delay'] = df_greengrass_stats.apply(calc_overall_delay, axis=1)

print("AWS Greengrass overall delay mean: {}".format(df_greengrass_stats['overall_delay'].mean()))
print("AWS Greengrass overall delay std: {}".format(df_greengrass_stats['overall_delay'].std()))
print("AWS Greengrass overall delay median: {}".format(df_greengrass_stats['overall_delay'].median()))
print("AWS Greengrass network delay mean: {}".format(df_greengrass_stats['network_delay'].mean()))
print("AWS Greengrass network delay std: {}".format(df_greengrass_stats['network_delay'].std()))
print("AWS Greengrass network delay median: {}".format(df_greengrass_stats['network_delay'].median()))
print("AWS Greengrass processing delay mean: {}".format(df_greengrass_stats['processing_delay'].mean()))
print("AWS Greengrass processing delay std: {}".format(df_greengrass_stats['processing_delay'].std()))
print("AWS Greengrass processing delay median: {}".format(df_greengrass_stats['processing_delay'].median()))

x = np.arange(0, 500, 1)
df_lambda_stats = pd.read_csv('stats_lambda_1024mb.csv', delimiter=',')

print("AWS Lambda overall delay mean: {}".format(df_lambda_stats['overall_delay'].mean()))
print("AWS Lambda overall delay std: {}".format(df_lambda_stats['overall_delay'].std()))
print("AWS Lambda overall delay median: {}".format(df_lambda_stats['overall_delay'].median()))
print("AWS Lambda network delay mean: {}".format(df_lambda_stats['network_delay'].mean()))
print("AWS Lambda network delay std: {}".format(df_lambda_stats['network_delay'].std()))
print("AWS Lambda network delay median: {}".format(df_lambda_stats['network_delay'].median()))
print("AWS Lambda processing delay mean: {}".format(df_lambda_stats['processing_delay'].mean()))
print("AWS Lambda processing delay std: {}".format(df_lambda_stats['processing_delay'].std()))
print("AWS Lambda processing delay median: {}".format(df_lambda_stats['processing_delay'].median()))

print("AWS Greengrass overall delay skew: {}".format(stats.skew(df_greengrass_stats['overall_delay'])))
print("AWS Greengrass overall delay kurtosis: {}".format(stats.kurtosis(df_greengrass_stats['overall_delay'])))
print("AWS Lambda overall delay skew: {}".format(stats.skew(df_lambda_stats['overall_delay'])))
print("AWS Lambda overall delay kurtosis: {}".format(stats.kurtosis(df_lambda_stats['overall_delay'])))

k2_lambda_overall_delay, p_aws_lambda_overall_delay = stats.normaltest(df_lambda_stats['overall_delay'])

if p_aws_lambda_overall_delay < alpha:
    print("The null hypothesis can be rejected for AWS Lambda overall delay: not normal distribution")
else:
    print("The null hypothesis can be accepted for AWS Lambda overall delay: not normal distribution")
print("AWS Lambda overall delay normaltest p_2: {}".format(p_aws_lambda_overall_delay))
print("Stat normal test aws lambda overall delay: {}".format(k2_lambda_overall_delay))

k2_greengrass_overall_delay, p_aws_greengrass_overall_delay = stats.normaltest(df_greengrass_stats['overall_delay'])
if p_aws_greengrass_overall_delay < alpha:
    print("The null hypothesis can be rejected for AWS Lambda overall delay: not normal distribution")
else:
    print("The null hypothesis can be accepted for AWS Lambda overall delay: normal distribution")
print("AWS greengrass overall delay normaltest p_2: {}".format(p_aws_greengrass_overall_delay))
print("Stat normal test aws greengrass overall delay: {}".format(k2_greengrass_overall_delay))

k2_lambda_network_delay, p_lambda_network_delay = stats.normaltest(df_lambda_stats['network_delay'])

if p_lambda_network_delay < alpha:
    print("The null hypothesis can be rejected for AWS Lambda network delay: not normal distribution")
else:
    print("The null hypothesis can be accepted for AWS Lambda network delay: normal distribution")
print("AWS Greengrass network delay normaltest p_2: {}".format(p_lambda_network_delay))
print("Stat normal test aws greengrass network delay: {}".format(k2_lambda_network_delay))

k2_greengrass_network_delay, p_greengrass_network_delay = stats.normaltest(df_greengrass_stats['network_delay'])

if p_greengrass_network_delay < alpha:
    print("The null hypothesis can be rejected for AWS Greengrass network delay: not normal distribution")
else:
    print("The null hypothesis can be accepted for AWS Greengrass network delay: normal distribution")
print("AWS Greengrass network delay normaltest p_2: {}".format(p_greengrass_network_delay))
print("Stat normal test aws greengrass network delay: {}".format(k2_greengrass_network_delay))

k2_lambda_processing_delay, p_lambda_processing_delay = stats.normaltest(df_lambda_stats['processing_delay'])
if p_lambda_processing_delay < alpha:
    print("The null hypothesis can be rejected for AWS Lambda processing delay: not normal distribution")
else:
    print("The null hypothesis can be accepted for AWS Lambda processing delay: normal distribution")
print("AWS Greengrass processing delay normaltest p_2: {}".format(p_lambda_processing_delay))
print("Stat normal test AWS Greengrass processing delay: {}".format(k2_lambda_processing_delay))

k2_greengrass_processing_delay, p_greengrass_processing_delay = stats.normaltest(
    df_greengrass_stats['processing_delay'])
if p_greengrass_processing_delay < alpha:
    print("The null hypothesis can be rejected for AWS Greengrass processing delay: not normal distribution")
else:
    print("The null hypothesis can be accepted for AWS Greengrass processing delay: normal distribution")
print("AWS Greengrass processing delay normaltest p_2: {}".format(p_greengrass_processing_delay))
print("Stat normal test aws greengrass processing delay: {}".format(k2_greengrass_processing_delay))

# greengrass_vs_lambda_overall_delay = pd.DataFrame({
#     'overall_delay': np.concatenate(
#         (df_greengrass_stats['overall_delay'].values, df_lambda_stats['overall_delay'].values)),
#     'platform': np.concatenate((['AWS Greengrass'] * 500, ['Azure Lambda'] * 500))
# })
#
# greengrass_vs_lambda_processing_delay = pd.DataFrame({
#     'processing_delay': np.concatenate(
#         (df_greengrass_stats['processing_delay'].values, df_lambda_stats['processing_delay'].values)),
#     'platform': np.concatenate((['AWS Greengrass'] * 500, ['Azure Lambda'] * 500))
# })
#
# greengrass_vs_lambda_network_delay = pd.DataFrame({
#     'network_delay': np.concatenate(
#         (df_greengrass_stats['network_delay'].values, df_lambda_stats['network_delay'].values)),
#     'platform': np.concatenate((['AWS Greengrass'] * 500, ['Azure Lambda'] * 500))
# })

x = np.concatenate((np.arange(0, 500, 1), np.arange(0, 500, 1)))
df_spss = pd.DataFrame({
    'id': x,
    'platform': np.concatenate((np.repeat('aws_greengrass', 500), np.repeat('aws_lambda', 500))),
    'network_delay': np.concatenate((df_greengrass_stats['network_delay'].values, df_lambda_stats['network_delay'].values)),
    'processing_delay': np.concatenate((df_greengrass_stats['processing_delay'].values, df_lambda_stats['processing_delay'].values))
})

df_spss.to_csv('df_spss.csv', header=True, index=None)

sub_id = np.concatenate((np.arange(0, 500, 1), np.arange(0, 500, 1), np.arange(0, 500, 1), np.arange(0, 500, 1)))
rt = np.concatenate(
    (df_greengrass_stats['network_delay'].values, df_lambda_stats['network_delay'].values, df_greengrass_stats['processing_delay'].values, df_lambda_stats['processing_delay'].values))
iv1 = np.concatenate((np.repeat('network_delay', 1000), np.repeat('processing_delay', 1000)))
iv2 = np.concatenate((np.repeat('aws_greengrass', 500), np.repeat('aws_lambda', 500), np.repeat('aws_greengrass', 500), np.repeat('aws_lambda', 500)))

# ********* pyvttbl version ************
# Sub = namedtuple('Sub', ['sub_id', 'rt', 'iv1', 'iv2'])
# df_pt = pt.DataFrame()
#
# for idx in range(len(sub_id)):
#     df_pt.insert(Sub(sub_id[idx], rt[idx], iv1[idx], iv2[idx])._asdict())
#
# print(type(df_pt['sub_id'][0]))
# aov = df_pt.anova('rt', sub='sub_id', wfactors=['iv1', 'iv2'])
#
# print(aov)


# ********* statsmodel version ************

df_pd = pd.DataFrame({
    'sub_id': sub_id,
    'delay': rt,
    'delay_type': iv1,
    'platform': iv2
})

#
# aovrm2way = AnovaRM(df_pd, 'delay', 'sub_id', within=['delay_type', 'platform'])
# res2way = aovrm2way.fit()
#
# print(res2way)


# ************Statsmodel with ols ***********

ols_model = ols('delay ~ C(delay_type)*C(platform)', df_pd).fit()

# print("Overall model F({ols_model.df_model: .0f},{ols_model.df_resid: .0f}) = {ols_model.fvalue: .3f}, p = {ols_model.f_pvalue: .4f}")
print("Overall model F({},{}) = {}, p = {}".format(ols_model.df_model, ols_model.df_resid, ols_model.fvalue, ols_model.f_pvalue))

print(ols_model.summary())

res2 = anova_lm(ols_model, typ=2)

# Calculating effect size
def anova_table(aov):
    aov['mean_sq'] = aov[:]['sum_sq']/aov[:]['df']

    aov['eta_sq'] = aov[:-1]['sum_sq']/sum(aov['sum_sq'])

    aov['omega_sq'] = (aov[:-1]['sum_sq']-(aov[:-1]['df']*aov['mean_sq'][-1]))/(sum(aov['sum_sq'])+aov['mean_sq'][-1])

    cols = ['sum_sq', 'mean_sq', 'df', 'F', 'PR(>F)', 'eta_sq', 'omega_sq']
    aov = aov[cols]
    return aov

anova_table(res2)

print(res2)


# ********** Post hoc testing ***************
mc = MultiComparison(df_pd['delay'], df_pd['delay_type'])
print(mc.tukeyhsd())


# greengrass_vs_lambda = pd.DataFrame({
#     'overall_delay': np.concatenate(
#         (df_greengrass_stats['overall_delay'].values, df_lambda_stats['overall_delay'].values)),
#     'network_delay': np.concatenate(
#         (df_greengrass_stats['network_delay'].values, df_lambda_stats['network_delay'].values)
#     ),
#     'processing_delay': np.concatenate((df_greengrass_stats['processing_delay'], df_lambda_stats['processing_delay'])),
#     'platform': np.concatenate((['aws_greengrass'] * 500, ['aws_lambda'] * 500))
# })

# plt.figure(2)
# fig, ax = plt.subplots(ncols=3, figsize=(30, 10))
#
# fig.tight_layout()
# subplot0 = plt.subplot(131)
# subplot0.set_ylim(0.0, 1.5)
# subplot0.set_yticks(np.arange(0.0, 1.5, 0.1))
# fig.tight_layout()
#
# plt.plot(x, df_lambda_stats['overall_delay'], 'r', label='AWS Lambda')
# plt.plot(x, df_greengrass_stats['overall_delay'], 'b', label="AWS Greengrass")
# plt.title('Overall delay')
# plt.legend()
#
# subplot1 = plt.subplot(132)
# subplot1.set_ylim(0.0, 1.5)
# subplot1.set_yticks(np.arange(0.0, 1.5, 0.1))
# plt.plot(x, df_lambda_stats['network_delay'], 'r', label='AWS Lambda')
# plt.plot(x, df_greengrass_stats['network_delay'], 'b', label="AWS Greengrass")
# plt.title('Network delay')
# plt.legend()
#
# subplot2 = plt.subplot(133)
# subplot2.set_ylim(0.0, 1.5)
# subplot2.set_yticks(np.arange(0.0, 1.5, 0.1))
# plt.plot(x, df_lambda_stats['processing_delay'], 'r', label='AWS Lambda')
# plt.plot(x, df_greengrass_stats['processing_delay'], 'b', label="AWS Greengrass")
# plt.title('Processing delay')
# plt.legend()
#
# plt.show()
