
# Python Backward Induction Overview

This project was written as a (very hurried) introduction to python for those who
understand how to make induction trees in Excel.  Look at the [Notebook](blob/main/backInductTree1.ipynb) to see how it's run.

## Python Basics

- Anything that is imported is usually imported by a name and then accessed via name.
    - _E.g.,_
       import somePackage as sp
       sp.someFunction(3,2)
- Indentation is what determines grouping
    - This is true for loops, classes, functions, etc
- Python functions all start with keyword def _functionName_ followed by a list of parameters being
    passed in
       - E.g.,
```
          def addTwoNumbers(alpha, beta):
          newValue = alpha + beta
          return newValue
```
## Python Class Basics

- Python class definitions start with the keyword _class_ and then lists the methods that are being
    defined.
       - If a class derives from anther class, that base class functions are available to the upper
          class.
       - Sometimes we overwrite these classes
- Class method functions always have a reference to the object. This is always ‘self’
    - _E.g.,_
```    
       class SomeClass(object):
       def sayHello(self):
       print(“hello!”)
```

## Tree Induction Object Basics

In order to create a new type of tree, you need to do the following:

- Define a new tree node class
- Create a new tree node factory
- Define a new tree info class (which derives from it.InfoObject)

### Tree Node Class

The new tree node class has to derive from it.BaseTreeNode and needs two functions to be overwritten:

- def updateLocal(self, info):
    - Using the info passed in, updates any variables that depend on the nodes position in the
       tree. You can access
          - timestep
          - state (from 0 to timestep – 1)
          - stateInt – deviation from center ( 0 is center, 1 is one node up, -2 is two nodes
             down) = (-timeStep) + 2 * (state)


- def backInduct(self, info):
    0 Using the tree info and nextUpper node and nextLower node (if not isFinalNode),
       calculate anything needed using backward induction

### Tree Node Factory

To create a factory, one needs to

- Pass in new Tree node class
- Set any printing format of variables we want to print out

```
europeanPutFactory = it.TreeFactory(EuropeanPutNode)
europeanPutFactory.addForm('value', '%6.2f')
europeanPutFactory.addForm('price', '%6.2f')
```
### Tree Info Class

To create a tree info class, you need to:

- Create a set of default values. This is a dictionary.
- Copy the def __init__ function changing the names as appropriate
    - (This function is the constructor for this class. It’s ok if you don’t know what that means
       yet)
- Create a calc() function that calculates any derived values.

## Using the Induction Tree

To use the tree,

- Start your favorite python interpreter. I recommend using Jupyter notebooks.
- Import your new file
- Create a new info object from your new file
- Create a tree using factory from file and new info object
- Print out variables of interest


