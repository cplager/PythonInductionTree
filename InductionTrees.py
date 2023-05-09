import sys
import copy

class InfoObject(object):
    def __init__(self, defaults={}, values={}):
        if defaults is None:
            self.__dict__ = values.copy()
        else:
            for key, defVal in defaults.items():
                self.__dict__[key] = values.get(key, defVal)
            for key, val in sorted(values.items()):
                if key not in defaults:
                    print("Warning: variable '%s' now known" % key)
        self.calc()

    def __str__(self):
        # simple string representation
        return str(self.__dict__)

    def copy(self):
        return copy.copy(self)

    def calc(self):
        # Overwritten by derived class
        pass


class Tree(object):
    def __init__(self, nodeFactory, info=None):
        self._iteration   = 0  # keep track of when to calculate
        self._linear      = [] # information depends only on period
        self._tree        = {} # information depends on period and state
        self._periods     = 0  # number of periods
        self._nodeFactory = nodeFactory
        self._useLinear   = nodeFactory.useLinear
        if info is not None:
            self.update(info)

        
    def update(self, info):
        # before we do anything, make sure that info has been 'calc'ed
        info.calc()
        # Does this one have the same number of periods?
        # If not, we have to remake the tree
        if self._periods != info.periods:
            self._periods = info.periods
            self._createNewTree()
        # We use iteration so that the nodes can tell whether or not they've
        # already recalculated.
        self._iteration += 1
        info.iteration = self._iteration
        # Update
        if self._useLinear:
            self._linear[0].update(info)
        self._tree[0,0].update(info)

        
    def _createNewTree(self):
        """Creates a new tree, hooking up the next/previous nodes as appropriate"""
        self._linear    = [] 
        self._tree      = {}
        for timeStep in range(0, self._periods + 1):
            if self._useLinear:
                self._linear.append(self._nodeFactory.linearNode(timeStep))
            for state in range(0, timeStep + 1):
                self._tree[timeStep, state] = self._nodeFactory.treeNode(timeStep, state)
        # Now we loop again upto but not past penultamite timeStep to
        # setup the next nodes of the tree
        for timeStep in range(0, self._periods):
            if self._useLinear:
                self._linear[timeStep].setNextNode(self._linear[timeStep + 1])
            for state in range(0, timeStep + 1):
                self._tree[timeStep, state].setNextNodes(self._tree[timeStep+1, state  ],
                                                         self._tree[timeStep+1, state+1])
                if self._useLinear:
                    self._tree[timeStep, state].setLinearNode(self._linear[timeStep])


    def stringifyLinear(self, variables):
        """Stringify linear node inforation"""
        if isinstance(variables, str):
            variables = [variables]
        stringDict = {}
        maxPerTS   = {}
        for index, var in enumerate(variables):
            maxPerTS[-1] = max(len(var), maxPerTS.get(-1, 0))
            stringDict[-1, index] = var
            for timeStep in range(0, self._periods+1):
                node = self._linear[timeStep]
                value = self._nodeFactory.form(var) % node.get(var)
                maxPerTS[timeStep] = max(len(value), maxPerTS.get(node.timeStep, 0))
                stringDict[timeStep, index] = value
        retval = ''
        for height in range(-0, len(variables)):
            for timeStep in range(-1, self._periods+1):
                size    = maxPerTS[timeStep]
                form    = "%%%ds  " % size
                retval += form % stringDict.get((timeStep, height), '')
            retval += '\n'
        return retval


    def stringify(self, variable, rightTriangle=False):
        """Stringify tree node information.  Either prints things out to look
           like binomial tree or as a right triangle."""
        stringDict = {}
        maxPerTS   = {}
        # use recursive function
        self.addStringNode(variable, self._tree[0,0], stringDict, maxPerTS, rightTriangle)
        retval = '%s\n' % variable
        if rightTriangle:
            lower, upper = -1, self._periods
        else:
            lower, upper = -self._periods-1, self._periods
        for height in range (upper, lower, -1):
            for timeStep in range(0, self._periods+1):
                size    = maxPerTS[timeStep]
                form    = "%%%ds  " % size
                retval += form % stringDict.get((timeStep, height), '')
            retval += '\n'
        return retval


    def addStringNode(self, variable, node, stringDict, maxPerTS, rightTriangle):        
        """Recursive function for tree node stringify."""
        value = self._nodeFactory.form(variable) % node.get(variable)
        if rightTriangle:
            height = node.state
        else:
            height = node.stateInt
        stringDict[node.timeStep, height] = value
        maxPerTS[node.timeStep] = max(len(value), maxPerTS.get(node.timeStep, 0))
        if not node.isFinalNode:
            self.addStringNode(variable, node.nextUpper, stringDict, maxPerTS, rightTriangle)
            self.addStringNode(variable, node.nextLower, stringDict, maxPerTS, rightTriangle)


class BaseLinearNode(object):

    """One dimensional nodes (one per timestep.)  Formula calculation (using
       timestep info), forward and back Induction implemented."""

    def __init__(self, timeStep, ignore=False):
        self._timeStep  = timeStep
        self._nextNode  = None
        self._prevNode  = None
        self._iteration = 0
        # Lots of trees don't have linear pieces.  If the overriding class
        # doesn't change ignore, then this class will be ignored
        self._ignore    = ignore

        
    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    
    def setNextNode(self, nextNode):
        # set next node
        self._nextNode = nextNode
        # and on next node, set previous node
        nextNode._prevNode = self

    
    def update(self, info):
        if self._ignore:
            return
        self.updateLocal(info)
        if self._nextNode:
            self._nextNode.update(info)
            # back propagage anything we need
            self.backInduct(info)


    def updateLocal(self, info):
        # to be overridden
        pass

    
    def backInduct(self, nextNode):
        # to be overridden
        pass

    ##########################################            
    ## Setup properties to make easy access ##
    ##########################################            
    @property
    def timeStep(self):      return self._timeStep

    @property
    def nextNode(self):       return self._nextNode
        
    @property
    def prevNode(self):       return self._prevNode
    
    @property
    def isFinalNode(self):    return self._nextNode is None
    
    @property
    def isStartingNode(self): return self._prevNode is None
    
            
class BaseTreeNode(object):

    """Two dimenional tree nodes.  Formula calculation (based on 
    timestep and state (and even deviation from center) and backward
    Induction implemented. Forward Induction not yet implemented."""

    def __init__(self, timeStep, state):
        self._timeStep   = timeStep
        self._state      = state
        # state half is number of half steps from center
        self._stateHalf  = (-timeStep) + 2 * (state)
        self._nextLower  = None
        self._nextUpper  = None
        self._prevUpper  = None
        self._prevLower  = None
        self._linearNode = None
        self._iteration  = 0


    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    
    def setNextNodes(self, nextLower, nextUpper):
        # hook up next nodes
        self._nextLower = nextLower
        self._nextUpper = nextUpper
        # and in the next nodes, tell them about previous nodes
        nextUpper._prevLower = self
        nextLower._prevUpper = self


    def setLinearNode(self, linear):
        self._linearNode = linear
    
    def update(self, info):
        # If we've already updated this node, then don't do it again
        if self._iteration == info.iteration:
            # Already done
            return
        self.updateLocal(info)
        if not self.isFinalNode:
            self._nextUpper.update(info)
            self._nextLower.update(info)
            # back propagage anything we need
            self.backInduct(info)
        self._iteration = info.iteration

    def updateLocal(self, info):
        # to be overridden
        pass
    
    def backInduct(self, nextNode):
        # to be overridden
        pass

    ##########################################            
    ## Setup properties to make easy access ##
    ##########################################            
    @property
    def timeStep(self):     return self._timeStep

    @property
    def state(self):        return self._state

    @property
    def statePos(self):     return self._stateHalf / 2.    
    
    @property
    def nextUpper(self):    return self._nextUpper

    @property
    def nextLower(self):    return self._nextLower

    @property
    def prevUpper(self):    return self._prevUpper
    
    @property
    def prevLower(self):    return self._prevLower
    
    @property
    def linearNode(self):   return self._linearNode
    
    @property
    def stateInt(self):     return self._stateHalf

    @property
    def isFinalNode(self):  return self._nextLower is None
    

class TreeFactory(object):
    """Bookkeeping class to tell tree which classes to use for which nodes."""
    def __init__(self, treeNoteClass, linearNodeClass=None):
        self.treeNode   = treeNoteClass
        self.linearNode = linearNodeClass
        self.useLinear  = linearNodeClass is not None
        self.formsDict  = {}

    def addForm(self, variable, form):
        self.formsDict[variable] = form

    def form(self, variable):
        return self.formsDict.get(variable, '%.2f')