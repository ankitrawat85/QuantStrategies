import math
import numpy as np

class BlackScholes:
    def __init__ (self, S0, vol):
        self.vol, self.S0 = vol, S0
    def NumberOfFactors(self):
        return 1
    def GetTimeSteps(self, eventDates):
        # black scholes diffusion is exact, no need to add more dates
        return eventDates
    def Diffuse(self, dts, bs):
        xs = [math.log(self.S0)]
        for i in (1, dts.size()):
            a = (self.r - self.q - 0.5 * self.vol * self.vol) * dts[i]
            b = self.vol * bs[0, i] * math.sqrt(dts[i])
            xs.append(xs[i-1] + a + b)
        return (lambda t: np.interp(t, dts, xs))