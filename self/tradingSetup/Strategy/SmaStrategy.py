from datetime import datetime
import backtrader as bt

class SmaSignal(bt.Signal):
    params = (('period', 20),)

    def __init__(self):
        self.lines.signal = self.data - bt.ind.SMA(period=self.p.period)


