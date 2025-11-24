
from AlgorithmImports import *

# region imports
from AlgorithmImports import *
import numpy as np
# endregion

class OptionSeller(QCAlgorithm):
    USE_ATR_DISTANCES          = False
    DO_CONTINGENT_BUYBACK      = True
    DO_PROTECTIVE_LONG_PUT     = True

    PCT_SHORT_OTM              = 0.045
    PCT_PROTECTIVE_GAP         = 0.010
    ATR_SHORT_MULTIPLIER       = 2.0
    ATR_PROTECTIVE_MULTIPLIER  = 0.5
    TRIGGER_UNDER_DROP_ATR     = 0.50
    REL_LIMIT_MARKUP           = 0.15

    STARTING_CASH              = 250_000
    TICKERS                    = ["MSFT","NVDA"]

    def Initialize(self):
        # Backtest window
        self.set_start_date(2024,1, 7)
        self.set_end_date(2024, 6, 28)
        self.set_cash(self.STARTING_CASH)
        
        # Brokerage model (or omit entirely)
        self.set_brokerage_model(BrokerageName.INTERACTIVE_BROKERS_BROKERAGE, AccountType.MARGIN)

        self.symbols = {}
        self.optSymbols = {}
        self.atrs = {}
        self.dailyCloses = {}
        self.lastTradeDate = {t: None for t in self.TICKERS}

        # Register assets
        for t in self.TICKERS:
            equity = self.add_equity(t,Resolution.MINUTE)

            equity.set_data_normalization_mode(DataNormalizationMode.RAW)
            self.symbols[t] = equity.Symbol
            opt = self.add_option(t, Resolution.MINUTE)
            opt.SetFilter(self.UniverseFilter)
            self.optSymbols[t] = opt.Symbol

            # Daily ATR on underlying 
            self.atrs[t] = self.atr(equity.symbol, 14, MovingAverageType.SIMPLE)


        # Warm up indicators so ATR logic can run early
        self.set_warm_up(30, Resolution.DAILY)
 

        # Schedule the daily entry at 10:00 NY time
        self.schedule.on(
                self.date_rules.every_day('SPY'),
                self.time_rules.at(10, 0, TimeZones.NEW_YORK),
                self.DailyEntry
            )

        self.contingents = []

        self.debug(f"Initialized. ATR mode={self.USE_ATR_DISTANCES}, "
                   f"Contingent={self.DO_CONTINGENT_BUYBACK}, Protective={self.DO_PROTECTIVE_LONG_PUT}")

    def UniverseFilter(self, universe: OptionFilterUniverse) -> OptionFilterUniverse:
        return universe.strikes(-40, +40).expiration(0, 7)

    def DailyEntry(self):
        if self.is_warming_up:
            self.debug("Skipping entry while warming up.")
            return

        slice = self.current_slice
        for t in self.TICKERS:
            if self.lastTradeDate[t] == self.time.date():
                continue

            chain = slice.option_chains.get(self.optSymbols[t], None)
            if not chain:
                self.debug(f"{t} no option chain at {self.time}.")
                continue

            under = self.symbols[t]
            spot = self.securities[under].Price
            today = self.time.date()

            puts_today = [c for c in chain if c.Right == OptionRight.PUT and c.Expiry.date() == today]
            if not puts_today:
                minExpiry = min([c.Expiry for c in chain if c.Right == OptionRight.PUT], default=None)
                puts_today = [c for c in chain if c.Right == OptionRight.PUT and c.Expiry == minExpiry]
                if not puts_today:
                    self.debug(f"{t} no puts found for selection on {self.time}.")
                    continue

            if self.USE_ATR_DISTANCES and self.atrs[t].IsReady:
                dist = self.ATRDollars(t, self.ATR_SHORT_MULTIPLIER)
            else:
                dist = self.PCT_SHORT_OTM * spot

            target_price = spot - dist
            candidates = [c for c in puts_today if c.Strike <= spot] or puts_today
            short_put = min(candidates, key=lambda c: abs(c.Strike - target_price))

            qty = 1
            self.market_order(short_put.Symbol, -qty)
            self.lastTradeDate[t] = today
            self.log(f"{t} STEP1: Short PUT {short_put.Symbol.ID}  expiry {short_put.Expiry.date()}  "
                     f"strike {short_put.Strike:.2f}  spot {spot:.2f}  target {target_price:.2f}")

            if self.DO_PROTECTIVE_LONG_PUT:
                prot_strike = self.ChooseProtectiveStrike(t, chain, short_put, spot)
                if prot_strike:
                    self.market_order(prot_strike.Symbol, +qty)
                    self.log(f"{t} STEP3: Protective LONG PUT {prot_strike.Symbol.ID}  "
                             f"expiry {prot_strike.Expiry.date()}  strike {prot_strike.Strike:.2f}")

            if self.DO_CONTINGENT_BUYBACK:
                trigger = spot - self.ATRDollars(t, self.TRIGGER_UNDER_DROP_ATR)
                mid = self.MidPrice(short_put)
                if mid is None:
                    mid = max(short_put.BidPrice, short_put.AskPrice)
                limit_px = mid * (1.0 + self.REL_LIMIT_MARKUP)
                self.contingents.append({
                    'ticker': t,
                    'under': under,
                    'opt': short_put.Symbol,
                    'expiry': short_put.Expiry.date(),
                    'trigger': trigger,
                    'limit': round(limit_px, 2),
                    'qty': qty,
                    'active': True
                })
                self.log(f"{t} STEP2: staged contingent BUY-to-CLOSE if {t} spot <= {trigger:.2f} at LMT {limit_px:.2f}")

    def OnData(self, slice: Slice):
        if not self.contingents:
            return
        to_submit = []
        for c in self.contingents:
            if not c['active']:
                continue
            if self.time.date() > c['expiry']:
                c['active'] = False
                continue
            spot = self.securities[c['under']].Price
            if spot <= c['trigger']:
                to_submit.append(c)

        for c in to_submit:
            self.limit_order(c['opt'], +c['qty'], c['limit'])
            c['active'] = False
            self.log(f"{c['ticker']} STEP2: contingent triggered: BUY-to-CLOSE {c['opt']} at LMT {c['limit']} "
                     f"(spot {self.securities[c['under']].Price:.2f} <= {c['trigger']:.2f})")

    def ChooseProtectiveStrike(self, ticker: str, chain: OptionChain, short_put: OptionContract, spot: float):
        same_exp_puts = [c for c in chain if c.right == OptionRight.PUT and c.expiry == short_put.expiry]
        if self.USE_ATR_DISTANCES and self.atrs[ticker].IsReady:
            gap = self.ATRDollars(ticker, self.ATR_PROTECTIVE_MULTIPLIER)
        else:
            gap = self.PCT_PROTECTIVE_GAP * spot
        target = max(0.01, short_put.strike - gap)
        candidates = [c for c in same_exp_puts if c.strike <= short_put.strike]
        if not candidates:
            return None
        return min(candidates, key=lambda c: abs(c.strike - target))

    def ATRDollars(self, ticker: str, multiple: float) -> float:
        if not self.atrs[ticker].IsReady:
            price = self.securities[self.symbols[ticker]].Price
            return multiple * 0.02 * price
        return multiple * float(self.atrs[ticker].Current.Value)

    def MidPrice(self, contract: OptionContract):
        bid = float(contract.bid_price) if contract.bid_price is not None else None
        ask = float(contract.ask_price) if contract.ask_price is not None else None
        if bid and ask and bid > 0 and ask > 0:
            return 0.5 * (bid + ask)
        last = float(contract.last_price) if contract.last_price is not None else None
        return last

    def FindBargainPuts(self, chain: OptionChain, under_symbol: Symbol, lookback_days: int = 20, max_delta: float = 0.25):
        hist = self.history[TradeBar](under_symbol, lookback_days, Resolution.DAILY)
        if hist is None:
            return []
        closes = [float(x.close) for x in hist]
        rets = []
        for i in range(1, len(closes)):
            if closes[i-1] > 0:
                rets.append((closes[i]/closes[i-1]) - 1.0)
        if not rets:
            return []
        hv = np.std(rets) * np.sqrt(252.0)
        today_puts = [c for c in chain if c.right == OptionRight.PUT]
        scored = []
        for c in today_puts:
            iv = float(c.implied_volatility) if c.implied_volatility is not None else None
            if not iv or iv <= 0:
                continue
            if c.greeks is not None and c.greeks.delta is not None:
                if abs(float(c.greeks.delta)) > max_delta:
                    continue
            edge = iv - hv
            scored.append((edge, c))
        scored.sort(key=lambda x: x[0])
        return [c for _, c in scored]
