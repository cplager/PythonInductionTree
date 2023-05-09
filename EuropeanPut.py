import math
import InductionTrees as it

########################################################################
## Define node class that has updateLocal and backInduct as appropriate ##
########################################################################
class EuropeanPutNode(it.BaseTreeNode):
    def updateLocal(self, info):
        self.price = info.initialPrice * info.stepVol ** self.stateInt
        if not self.isFinalNode:
            # All done.
            return
        # If I'm here, then this is a final node. Do whatever needs to be done
        self.value = max(self.price - info.strike, 0)

    def backInduct(self, info):
        if self.isFinalNode:
            # Nothing to do
            return
        self.value = (info.qUp   * self.nextUpper.value + 
                      info.qDown * self.nextLower.value) / \
                      math.exp(info.periodRate)

#################################################################
## Create a factory that can setup and print this type of tree ##
#################################################################
europeanPutFactory = it.TreeFactory(EuropeanPutNode)
europeanPutFactory.addForm('value', '%6.2f')
europeanPutFactory.addForm('price', '%6.2f')

#################################################################################
## Create an info object that grabs the right values and calculates any needed ##
## derived quantities.                                                         ##
#################################################################################
class EuropeanPutInfo(it.InfoObject):

    defaults = {'initialPrice' : 100     ,
                'strike'       : 100     ,
                'numYears'     :   0.25  ,
                'volatility'   :   0.234 ,
                'periods'      :  10     ,
                'rate'         :   0.1194,
                'divRate'      :   0     ,}

    def __init__(self, **kwargs):
        # All this initialization does is call the base initialization with
        # the class specific defaults dictionary
        super(EuropeanPutInfo, self).__init__(EuropeanPutInfo.defaults, kwargs)

    def calc(self):
        """We do any calculations inside this function so that if a user 
        modifies anything, we can make sure that any derived data gets 
        recalculated before it gets used by the tree. """
        self.periodRate   = self.rate * self.numYears / self.periods
        self.stepVol      = math.exp(self.volatility * 
                                     math.sqrt(self.numYears / self.periods))
        self.flipVol      = 1. / self.stepVol
        self.qUp          = (math.exp((self.rate - self.divRate) * 
                                       self.numYears / self.periods) 
                             - self.flipVol) / \
                            (self.stepVol - self.flipVol)
        self.qDown        = 1 - self.qUp