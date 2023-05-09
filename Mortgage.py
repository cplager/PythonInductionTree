import math
import InductionTrees as it

########################################################################
## Define node class that has updateLocal and backInduct as appropriate ##
########################################################################
class MortgageNode(it.BaseTreeNode):
    def updateLocal(self, info):
        self.interestRate = info.interestStart * info.upMult ** self.stateInt
        if not self.isFinalNode:
            # All done.
            return
        # If I'm here, then this is a final node. Do whatever needs to be done
        self.nonCallValue = 0
        self.callValue    = 0

    def backInduct(self, info):
        if self.isFinalNode:
            # Nothing to do
            return
        self.nonCallValue = (0.5 * (self.nextUpper.nonCallValue + info.periodPayment) + 
                             0.5 * (self.nextLower.nonCallValue + info.periodPayment)) \
                               / (1 + self.interestRate)
        upperCallValue    = (0.5 * (self.nextUpper.callValue + info.periodPayment) + 
                             0.5 * (self.nextLower.callValue + info.periodPayment)) \
                               / (1 + self.interestRate)
        self.callValue    = min(self.linearNode.remainPrincipal, upperCallValue)

## Linear node class
class MortgageLinearNode(it.BaseLinearNode):
    def updateLocal(self, info):
        if self.isFinalNode:
            self.remainPrincipal = 0

    # no back propagation needed
    def backInduct(self, info):
        if self.isFinalNode:
            return
        self.remainPrincipal = (self.nextNode.remainPrincipal + info.periodPayment) \
                                / (1 + info.mortRate)

#################################################################
## Create a factory that can setup and print this type of tree ##
#################################################################
mortgageFactory = it.TreeFactory(MortgageNode, MortgageLinearNode)
mortgageFactory.addForm('nonCallValue',    '%6.2f')
mortgageFactory.addForm('callValue',       '%6.2f')
mortgageFactory.addForm('remainPrincipal', '%6.2f')

#################################################################################
## Create an info object that grabs the right values and calculates any needed ##
## derived quantities.                                                         ##
#################################################################################
class MortgageInfo(it.InfoObject):
    defaults = {'startPrincipal' : 100   ,
                'mortRate'       :   0.07,
                'periods'        :  30   ,
                'interestStart'  :   0.03,
                'interestVol'    :   0.20,
                'interestDrift'  :   0.  ,
                'prepayCost'     :   0.  ,}


    def __init__(self, **kwargs):
        super(MortgageInfo, self).__init__(MortgageInfo.defaults, kwargs)


    def calc(self):
        """We do any calculations inside this function so that if a user modifies
        anything, we can make sure that any derived data gets recalculated before it
        gets used by the tree. """
        self.upMult        = math.exp(self.interestDrift + self.interestVol)
        self.downMult      = math.exp(self.interestDrift - self.interestVol)
        self.periodPayment = self.startPrincipal * self.mortRate / \
                             (1 - 1 / (1 + self.mortRate)**self.periods)