import pandas as pd;
import numpy as np;
import statsmodels.api as sm;
import statsmodels.discrete.discrete_model as smdiscrete
pd.set_option('use_inf_as_na', True)

meta_df = pd.read_csv("stockmetadata.csv")
fdata_df = pd.read_csv("corpfund.csv")
fdata_df = fdata_df[fdata_df['dimension']=='ARQ']
fdata_df['datekey'] = pd.to_datetime(fdata_df['datekey'])
df_left = pd.merge(fdata_df, meta_df, on='ticker', how='left')
df_left = df_left.set_index('datekey')


industrydummies = pd.get_dummies(df_left['sicsector'])
industrydummies.sum()		#purely for exploring the data, has no other purpose
industrydummies.describe()      #purely for exploring the data, has no other purpose

data_w_dummies = pd.concat([df_left,industrydummies], axis=1)

data_w_dummies.drop(['Wholesale Trade'], inplace=True, axis=1)	#drop 1 dummy variable
data_w_dummies['epratio'] = data_w_dummies['eps']/data_w_dummies['price']	#generate dependent variable
data_w_dummies['operatingmargin'] = data_w_dummies['opinc'] / data_w_dummies['revenue']		#generate independent variable


#initial analysis
result = sm.OLS(data_w_dummies['epratio'], sm.add_constant(data_w_dummies[['operatingmargin']]), missing='drop').fit()
result.summary()
result = sm.OLS(data_w_dummies['epratio'], sm.add_constant(data_w_dummies[['operatingmargin', 'Agriculture Forestry And Fishing', 'Construction','Finance Insurance And Real Estate', 'Manufacturing', 'Mining','Retail Trade', 'Services','Transportation Communications Electric Gas And Sanitary Service']]), missing='drop').fit()
result.summary()
data_w_dummies['lnoperatingmargin'] = np.log(data_w_dummies['operatingmargin'])
result = sm.OLS(data_w_dummies['epratio'], sm.add_constant(data_w_dummies[['lnoperatingmargin']]), missing='drop').fit()
result.summary()
data_w_dummies['lnepratio'] = np.log(data_w_dummies['epratio'])
result = sm.OLS(data_w_dummies['lnepratio'], sm.add_constant(data_w_dummies[['lnoperatingmargin']]), missing='drop').fit()
result.summary()

#with dummy variables
result = sm.OLS(data_w_dummies['lnepratio'], sm.add_constant(data_w_dummies[['lnoperatingmargin', 'Agriculture Forestry And Fishing', 'Construction','Finance Insurance And Real Estate', 'Manufacturing', 'Mining','Retail Trade', 'Services','Transportation Communications Electric Gas And Sanitary Service']]), missing='drop').fit()
result.summary()

#clustering standard variables
data_w_dummies.dropna(subset = ['lnepratio', 'lnoperatingmargin'], inplace=True)	#because of a bug in python where fillna is not working perfectly
#note that we can cannot cluster by str variables in python, hence using siccode instead of sicsector
result = sm.OLS(data_w_dummies['lnepratio'], sm.add_constant(data_w_dummies[['lnoperatingmargin', 'Agriculture Forestry And Fishing', 'Construction','Finance Insurance And Real Estate', 'Manufacturing', 'Mining','Retail Trade', 'Services','Transportation Communications Electric Gas And Sanitary Service']]), missing='drop').fit(cov_type='cluster', cov_kwds={'groups': data_w_dummies['siccode']})
result.summary()

#generate categorical variable for probit/logit analysis
data_w_dummies['paydividend'] = data_w_dummies['dps']>0
data_w_dummies['paydividend']	#purely for describing data
data_w_dummies['paydividend'].mean()	#purely for describing data
data_w_dummies['paydividend'] = data_w_dummies['paydividend'].astype(int)	#formatting the data for estimation models

#try using OLS anyway
result = sm.OLS(data_w_dummies['paydividend'], sm.add_constant(data_w_dummies[['lnoperatingmargin', 'Agriculture Forestry And Fishing', 'Construction','Finance Insurance And Real Estate', 'Manufacturing', 'Mining','Retail Trade', 'Services','Transportation Communications Electric Gas And Sanitary Service']]), missing='drop').fit(cov_type='cluster', cov_kwds={'groups': data_w_dummies['siccode']})
result.summary()

#use logit instead
result = smdiscrete.Logit(data_w_dummies['paydividend'], sm.add_constant(data_w_dummies[['lnoperatingmargin', 'Agriculture Forestry And Fishing', 'Construction','Finance Insurance And Real Estate', 'Manufacturing', 'Mining','Retail Trade', 'Services','Transportation Communications Electric Gas And Sanitary Service']]), missing='drop').fit(cov_type='cluster', cov_kwds={'groups': data_w_dummies['siccode']})
result.summary()

