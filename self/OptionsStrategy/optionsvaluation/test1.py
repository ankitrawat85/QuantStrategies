import pandas as pd
desired_width = 320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns', 20)
df_date = pd.read_csv("final.csv",header=0)
print(df_date[df_date["Option Type"] == "PE"])

import matplotlib.pylab as plt
plt.figure(figsize = (12, 7))
plt.scatter(df_date['Strike Price'],df_date['impliedvolatility'], alpha = 0.8, c = 'g' ,marker = 's', label = 'Market')
plt.plot(df_date['Strike Price'], df_date['sabrsigma_new'], '--r', linewidth = 3, label = 'SABR model')
plt.ylabel('Implied Vol', fontsize = 20)
plt.xlabel('Strike', fontsize = 20)
plt.ylim(0.2, 0.4)
plt.legend(fontsize = 16);
plt.show()

