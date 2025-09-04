# README IN CHINESE

# 项目内容

![示例图](spread_demo_2y/中华人民共和国财政部-2024S1-30年债券利差分析.png)

在第一创业公司实习时对四大行（财政部，中国农业发展银行，国家开发银行，中国进出口银行）发行的同期限债券进行债券间利差分析，主要集中在10年和30年。`利差分析四大行2年_final.csv`包含了24年至25年下旬债券时序的必要数据。基于此csv，
`spread_demo.py`生成利差与借贷额（做空程度）和成交笔数（活跃度）的分析图，见`spread_demo_2y`;
`spread_corr.py`生成最活跃券与次活跃券（1-2）和最活跃券与次次活跃券（1-3）利差与成交笔数比的回归分析，见`spread_demo_corr`;
`spread_boxplots.py`生成利差随时间分布的箱型图，见`spread_demo_boxplots`。

注意：
1.图片文件夹只包含了中华人民共和国财政部（国债）30年债券，更改python文件中的参数可以按自己喜好对其它发债主体，其它期限的债券进行分析。
2.由于活跃券大约3个月切换一次，我们观察了24到25年8月的整体概览，手动定位了活跃券的切换日期，将这1年半的数据按活跃券切换分为了6段，标记为2024S1等，确保了活跃券的稳定，使利差分析有意义。

# 讨论

通常认为同类债券间的利差主要受活跃度影响，即流动性溢价，也可能受到YTM本身波动，市场情绪，金融机构合规要求等次要因素的影响。本研究通过`spread_demo.py`调查了做空程度对利差的影响，发现市场上对同类债券的做空总量大致稳定，最活跃券与次活跃券的做空程度若倒挂会缩小利差。
`spread_corr.py`则发现利差与活跃度比的关系较为复杂，虽然大多数情况下都存在线性关系（皮尔逊相关系数和R方不为0），但该关系随时间周期演进会大幅变化，甚至由正/负相关转为负/正相关，无法给我们有实践意义的结论，这说明“流动性溢价”这一规律并不总是有效，由图也可看出最活跃券-次活跃券的利差常常为正。
然而，`spread_boxplots.py`的结果说明，大部分时间内，尽管最活跃券-次活跃券（1-2）的利差值较为随机，但1-2，1-3，1-4，1-5的利差逐级拉大的现象是明确的，说明流动性溢价在相对意义上是明显的。综上，此研究增进了我们对于债券市场利差现象的理解，在交易时能帮助我们更好地对债券进行定价和预期管理。


# README IN ENGLISH

# Bond Spread Analysis among Chinese Policy Banks and MOF

This project studies yield spreads between bonds of the **Ministry of Finance (MOF)**, **Agricultural Development Bank of China (ADBC)**, **China Development Bank (CDB)**, and the **Export-Import Bank of China (EXIM Bank)**, focusing on 10-year and 30-year maturities.  
The dataset comes from *spread_analysis_2y_final.csv*, which contains bond time-series data from 2024 to mid-2025.

---

## Scripts and Outputs

- **spread_demo.py**  
  Generates charts analyzing spreads against:
  - borrowing volume (short-selling intensity)  
  - transaction counts (liquidity/activeness)  
  → Output: *spread_demo_2y*

- **spread_corr.py**  
  Runs regression analysis of spreads vs. activeness ratios:  
  - most active vs. second-most active bond (1–2)  
  - most active vs. third-most active bond (1–3)  
  → Output: *spread_demo_corr*

- **spread_boxplots.py**  
  Produces boxplots of spread distributions over time.  
  → Output: *spread_demo_boxplots*

---

## Notes

1. Image folders only includes charts for **MOF 30Y bonds**.  
   You can change parameters in the Python files to analyze other issuers or maturities.  

2. Since the most active bond changes roughly every 3 months, we manually identified six stable periods between 2024 and Aug 2025 (labeled *2024S1*, etc.) to ensure meaningful spread analysis.  

---

## Discussion

- **Liquidity premium**:  
  Spreads between similar bonds are usually explained by liquidity. Other secondary drivers include YTM volatility, market sentiment, and regulatory constraints.  

- **Results from `spread_demo.py`**:  
  Short-selling volume is broadly stable. When the most active bond has lower shorting than the second-most active one, their spread tends to narrow.  

- **Results from `spread_corr.py`**:  
  The relationship between spreads and activeness ratios is unstable. While linear correlation (Pearson and R²) usually exists, the sign can flip over time. This suggests the “liquidity premium” effect is not always valid in practice. Many times, the spread between the most and second-most active bonds is positive.  

- **Results from `spread_boxplots.py`**:  
  Although the 1–2 spread is hard to predict, the pattern of **1–2 < 1–3 < 1–4 < 1–5** is clear, confirming liquidity premium exists in a relative sense.  

---

## Conclusion
This project improves our understanding of bond yield spreads in the Chinese market.  
The findings highlight when liquidity effects dominate and when they break down, providing useful insights for **bond pricing and expectation management** in trading practice.  



