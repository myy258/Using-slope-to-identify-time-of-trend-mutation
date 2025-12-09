## 方法概述
在基于时间序列数据的分析任务中，往往会因时间的推移出现数据漂移或波动。在不同的行业或领域都会出现，原因有很多，在这里不概述原因。旨在通过算法识别出出现变化的那个时间点，方便做出各种决策。
> “通常可用于识别产品缺陷发生的时间点，有助于快速定位问题出现的时间。当然不限于这种情况。”

主要工作原理：
1. 将时间格式数据转化为序列。
2. 建立滑动窗口，自定义每个窗口的数据量，一个窗口为一个batch，自定义setp。
3. 设置斜率阈值，计算每个batch的斜率，找出斜率最大且大于阈值的batch,标记该batch的第一个数据点为∧（increase）或∨（decrease）。
4. 当出现∧（increase）或∨（decrease）时，后面不会重复出现相同的标记直至不同的标记出现。
5. 必须根据散点拟合出趋势线，趋势线的平滑度通过参数调整。

![image]([https://github.com/myy258/1024-game/blob/main/image/Screenshot%202025-11-17%20153047.png](https://github.com/myy258/Using-slope-to-identify-time-of-trend-mutation/blob/main/img/Screenshot%202025-12-09%20161729.png))
   
## 使用环境

- **Python版本**: 3.9.7
- **Conda**: Anaconda

## 模块版本

- **pandas**: 1.5.3
- **numpy**: 1.26.4
- **matplotlib**: 3.8.3
- **statsmodels**: 0.14.4

## 传入参数使用

```bash
# 曲线平滑度
lambda_val=0.3

滑动窗口大小
window_size=20

斜率阈值
threshold=0.6

开始时间点
x=time_range_start

结束时间点
y=time_range_end
```

## 实例
```python
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
```
依据实际情况调整传入参数。
