import os
import pandas as pd
import pm4py
from pm4py.algo.discovery.correlation_mining import algorithm as correlation_miner
from pm4py.visualization.dfg import visualizer as dfg_visualizer
import config
result_format = "jpg"


def apply(df, account_name, dir_path):
    df.rename(columns={'COMMAND': 'concept:name', 'CURRENT_TIMESTAMP': 'time:timestamp'}, inplace=True)
    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"], utc=True)
    frequency_dfg, performance_dfg = correlation_miner.apply(df, parameters={correlation_miner.Variants.CLASSIC.value.Parameters.ACTIVITY_KEY: "concept:name",
                                    correlation_miner.Variants.CLASSIC.value.Parameters.TIMESTAMP_KEY: "time:timestamp"})

    activities_freq = dict(df["concept:name"].value_counts())

    gviz_freq = dfg_visualizer.apply(frequency_dfg, variant=dfg_visualizer.Variants.FREQUENCY, activities_count=activities_freq, parameters={"format": result_format})
    gviz_perf = dfg_visualizer.apply(performance_dfg, variant=dfg_visualizer.Variants.PERFORMANCE, activities_count=activities_freq, parameters={"format": result_format})

    # freq_file = dir_path + "/" + account_name +'_freq.' + result_format
    freq_file = os.path.join(config.general.models_dir, account_name +'_freq.' + result_format)
    # perf_file = dir_path + "/" + account_name +'_pref.' + result_format
    perf_file = os.path.join(config.general.models_dir, account_name +'_pref.' + result_format)
    
    dfg_visualizer.save(gviz_freq,  freq_file)
    dfg_visualizer.save(gviz_perf, perf_file)
    
    models = {"frequency" : freq_file, 'performance': perf_file}
    return models