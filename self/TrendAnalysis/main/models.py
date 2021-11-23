class models():

    def __init__(self):
        print ("initialize")

    def AR(self, data, p):
        return sm.tsa.ARMA(data, (p, 0)).fit(disp=-1)

    def MA(self, data, q):
        return sm.tsa.ARMA(data, (0, q)).fit(disp=-1)

    def ARMA(self, data, p, q):
        return sm.tsa.ARMA(data, (p, q)).fit(disp=-1)

