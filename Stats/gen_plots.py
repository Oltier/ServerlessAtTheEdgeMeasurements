import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def calc_processing_delay(row):
    return row['processing_end_time'].astype(np.float) - row['processing_start_time'].astype(np.float)


def calc_network_delay_aws(row):
    return row['message_arrived'].astype(np.float) - row['message_sent'].astype(np.float) - row['processing_delay'].astype(np.float)


def calc_network_delay_azure(row):
    return row['message_arrived'].astype(np.float) - row['message_sent'].astype(np.float)


def calc_overall_delay(row):
    return row['processing_delay'].astype(np.float) + row['network_delay'].astype(np.float)


df_azure_stats = pd.read_csv('azure_stats.csv', delimiter=';')
df_aws_stats = pd.read_csv('AWS_stats.csv', delimiter=';')

df_azure_stats['processing_delay'] = df_azure_stats.apply(calc_processing_delay, axis=1)
df_azure_stats['network_delay'] = df_azure_stats.apply(calc_network_delay_azure, axis=1)
df_azure_stats['overall_delay'] = df_azure_stats.apply(calc_overall_delay, axis=1)

df_aws_stats['processing_delay'] = df_aws_stats.apply(calc_processing_delay, axis=1)
df_aws_stats['network_delay'] = df_aws_stats.apply(calc_network_delay_aws, axis=1)
df_aws_stats['overall_delay'] = df_aws_stats.apply(calc_overall_delay, axis=1)

# plt.figure(1)
