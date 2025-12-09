import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from enum import Enum, auto

def jmp_like_smoother(x, y, lambda_val=0.3):
    smoothed = sm.nonparametric.lowess(y, x, frac=lambda_val)
    return smoothed[:, 1]

class TrendState(Enum):
    NEUTRAL = auto()
    RISING = auto()
    FALLING = auto()

def find_trend_changes_v2(x, y, window_size, threshold):
    
    if len(x) != len(y):
        raise ValueError("x&y Should have the same length")
    
    state = TrendState.NEUTRAL
    slopes = []
    up_points = []
    down_points = []

    for i in range(len(y)-window_size+1):
        x_window = x[i:i+window_size]
        y_window = y[i:i+window_size]
        slope = np.polyfit(x_window, y_window*100, 1)[0]
        slopes.append(slope)

    mark_point = 0
    for i in range(len(slopes)):
        #current_idx = i + window_size
        
        if (state != TrendState.RISING or len(slopes[mark_point:i]) / len(slopes) > 1/3) and slopes[i] > threshold:
            up_points.append(i)
            mark_point = i
            state = TrendState.RISING
        elif (state != TrendState.FALLING or len(slopes[mark_point:i]) / len(slopes) > 1/3) and slopes[i] < -threshold:
            down_points.append(i)
            mark_point = i
            state = TrendState.FALLING
    
    return up_points, down_points


if __name__ == '__main__':

    df = pd.read_csv('data.csv') 
    df = df.sort_values(by='TIME', ascending=True)
    df['id index'] = np.arange(len(df))
    
    time_range_start = 0
    time_range_end = 291
    df_time_range = df.loc[(df['id index']>=time_range_start) & (df['id index']<=time_range_end)]
    df_time_range = df_time_range.reset_index(drop=True)

    dfScaler = df_time_range.copy()
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    dfScaler[['X1']] = scaler.fit_transform(dfScaler[['X1']])
    
    plt.subplots(figsize=(10, 8))  
    plt.plot(df_time_range['id index'], df_time_range['X1'], marker='o', markersize=4, linestyle='none', color='red')
    plt.grid(lw=2, ls=':')  
    
    y_min, y_max = min(df_time_range['X1']), max(df_time_range['X1'])
    margin = 0.2 * (y_max - y_min)
    
    smoothed_y = jmp_like_smoother(df_time_range['id index'], df_time_range['X1'], 0.3)
    plt.plot(df_time_range['id index'], smoothed_y, 'g--', label='trend') 
    smoothed_Scaler = jmp_like_smoother(df_time_range['id index'], dfScaler['X1'], 0.3)
    up_points, down_points = find_trend_changes_v2(df_time_range['id index'], smoothed_Scaler, 20, 0.6)
    
    
    plt.scatter([df_time_range['id index'][i] for i in up_points], [smoothed_y[i] for i in up_points], 
                c='b', marker='^', s=120, label='Up trend change', zorder=3)
    plt.scatter([df_time_range['id index'][i] for i in down_points], [smoothed_y[i] for i in down_points],
                c='b', marker='v', s=120, label='Down trend change', zorder=3)