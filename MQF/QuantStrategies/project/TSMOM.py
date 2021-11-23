LOOKBACK_PERIOD_ANNUAL = 251
import numpy as np
import pandas as pd

def __compute_annualized_returns(self, sd_window):
    """
    Computes annualized return and rolling standard deviation for lookback period.
    :return: tuple of daily return, annual return and rolling standard deviation of all assets.
    """
    daily_ret = self.aggregated_assets.pct_change()
    annual_ret = self.aggregated_assets.pct_change(periods=LOOKBACK_PERIOD_ANNUAL)
    rolling_std = daily_ret.rolling(sd_window).std() * np.sqrt(LOOKBACK_PERIOD_ANNUAL)
    rolling_std[rolling_std < self.sigma_target / 10.0] = self.sigma_target / 10.0

    return daily_ret, annual_ret, rolling_std


def pre_strategy(self, sd_window):
    """
    Prepares & computes the necessary variables needed before computating the strategy.
    :return:
    """
    self.__aggregate_assets()
    daily_ret, annual_ret, rolling_std = self.__compute_annualized_returns(sd_window)

    return daily_ret, annual_ret, rolling_std


def test_corr_adjusted_tsmom_strategy(self):
    st_2 = portfolio_strategy.CorrAdjustedTSMOMStrategy(self.dbm, self.df, 0.4)
    res_2 = st_2.compute_strategy()

    self.assertIsNotNone(res_2)


class CorrAdjustedTSMOMStrategy():
    def __init__(self, data: pd.DataFrame, sigma_target):
        self.__init__(self,data, sigma_target)

    def compute_strategy(self, sd_window):
        daily_ret, annual_ret, rolling_std = super().pre_strategy(sd_window)

        annual_ret_signed = (annual_ret > 0)
        annual_ret_signed = (annual_ret_signed * 2) - 1

        cf_list = []

        for t in range(annual_ret.shape[0]):
            curr_date = annual_ret.index[t]
            annual_ret_upto_curr = annual_ret[annual_ret.index <= curr_date]

            assets_present = annual_ret.columns[annual_ret.iloc[t].notnull()]

            if t % 100 == 0:
                print('Progress: {0:.2f}%'.format(int(t * 100 / self.n_t.shape[0])))

            annual_ret_upto_curr_assets = annual_ret_upto_curr[assets_present]
            annual_ret_upto_curr_assets = annual_ret_upto_curr_assets.dropna(how='all')

            if annual_ret_upto_curr_assets.shape[0] < 2 or annual_ret_upto_curr_assets.shape[1] < 2:
                cf_list.append(1)
                continue

            annual_ret_upto_curr_assets_signed = annual_ret_upto_curr_assets > 0
            annual_ret_upto_curr_assets_signed *= 2
            annual_ret_upto_curr_assets_signed -= 1

            asset_corr = annual_ret_upto_curr_assets.corr().values

            co_sign = np.eye(*asset_corr.shape)

            for i in range(co_sign.shape[0]):
                for j in range(i + 1, co_sign.shape[1]):
                    temp = annual_ret_upto_curr_assets_signed.iloc[-1].values
                    co_sign[i, j] = temp[i] * temp[j]
                    co_sign[j, i] = temp[i] * temp[j]

            # N = self.n_t[t]
            N = asset_corr.shape[0]
            rho_bar = ((asset_corr * co_sign).sum() - asset_corr.shape[0]) / (N * (N - 1))
            temp = N / (1 + ((N - 1) * rho_bar))

            if temp < 0:
                print('Warning: negative value encountered for taking square root.')
                cf_list.append(1)
                continue

            cf_t = np.sqrt(temp)
            cf_list.append(cf_t)

        asset_weight = self.sigma_target * annual_ret_signed / rolling_std
        asset_weight = asset_weight.div(self.n_t, axis=0)
        asset_weight = asset_weight.mul(np.array(cf_list), axis=0)
        asset_weight = asset_weight.shift(1)

        portfolio_return = (asset_weight * daily_ret).sum(axis=1)
        # portfolio_return = portfolio_return.div(self.n_t * np.array(cf_list), axis=0)

        return portfolio_return, asset_weight, daily_ret
