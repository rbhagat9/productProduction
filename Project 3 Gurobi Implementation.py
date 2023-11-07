# Rohan Bhagat
# ISYE 3133
# Project 3
# Studio Section MW1
# GTID: 903657424

from gurobipy import GRB,Model
import numpy as np

mod = Model('Project 3')
mod.setParam('OutputFlag', False)

# PART ONE
# read data

# resources required
with open('resource.csv') as f:
    rows = f.read().split('\n')
resourcesRequired = [] 
"""
list of P tuples where the ith tuple contains M ints corresponding
to the amount of resource j required to produce product i 
"""
for row in rows[1:len(rows) - 1]:
    row = row.split(',')
    numberRow = []
    for element in row:
        numberRow.append(int(element))
    resourcesRequired.append(tuple(numberRow))
reqs = np.array([np.array(row) for row in resourcesRequired])[:,1:]

# product prices
with open('product_prices.csv') as f:
    rows = f.read().split('\n')
price = [] # list of P ints corresponding to price of each product
for row in rows[1:len(rows) - 1]:
    row = row.split(',')
    price.append(int(row[1]))
prices = np.array(price)

# materials available constraint
with open('materials_available.csv') as f:
    rows = f.read().split('\n')
available = [] # list of M ints corresponding to amount of each resource m available
for row in rows[1:len(rows) - 1]:
    row = row.split(',')
    available.append(int(row[1]))
availabilities = np.array(available)

P = len(price) # number of products
M = len(available) # number of materials


# decision variables
A = mod.addMVar((1,P), vtype=GRB.CONTINUOUS, name = 'Optimal Product Production')

mod.addConstr(A @ reqs <= availabilities, name='c1') 
"""
resources required for product i times amount of product i must be less than
or equal to availabilities of said resources for all products.
"""

mod.setObjective((A @ prices), GRB.MAXIMIZE)
#print(prices)
#print(availabilities)

mod.optimize()
print("\nFOR PART 1:\n")
if mod.status == GRB.OPTIMAL:
    print("The solution found is optimal.")
    print(f"The optimal objective value is {mod.objVal}")
    print("The optimal solution is")
    """
    for v in mod.getVars():
        if v.x != 0:
            print(f"{v.varName} = {v.x}")
    """
    ntp = []
    for i in range(len(mod.getVars())):
        if mod.getVars()[i].x != 0:
            ntp.append((i, mod.getVars()[i].x))
    for p in ntp:
        print(f"Production of Product {p[0]} = {p[1]}")
else:
    print("The solution found is not optimal.")

""" If, in addition to the products produced and sold in the optimal solution,
1 unit of product 1 (the second product, since our product numbering is 0-indexed) were sold,
the objective value would increase by 3, since the product price of product 1 is 3.
In reality, we would only be able to do this if we were able to relax our constraints by increasing material availability."""

# ADDITIONS FOR PART TWO

# calculate shadow cost vector (1 dimensional array with M entries)
mod.Params.QCPDual = 1
constrs = mod.getConstrs()
shadowPrices = []
for i in range(M):
    shadowPrices.append(constrs[i].Pi)

# new product
with open('new_product.csv') as f:
    rows = f.read().split('\n')
new = [] # list of M ints corresponding to amount of each resource available
for row in rows[1:len(rows) - 1]:
    row = row.split(',')
    new.append(int(row[1]))

# add new product to requirements (out of place for clarity)
reqs2 = np.vstack([reqs, new])

# calculate resource cost of new product
rcNew = 0
for j in range(M):
    rcNew += (shadowPrices[j] * reqs2[32][j])

"""
The resource cost of the new product is rcNew ~= $4.57. This means that if we were to produce 1 unit of this product,
it would 'cost' us rcNew ~= $4.57  in opportunity cost to produce. So, this can be thought of as the minimum price
our product must sell for in order for it to be worth producing a nonzero amount of.
"""

# price of new product is 1 less than resource cost
priceNew = rcNew - 1

# add price of new product to price array (out of place for clarity)
prices2 = np.append(prices, priceNew)

# Update old constraints and decision variable
mod.remove(mod.getVars())
A = mod.addMVar((1,P+1), vtype=GRB.CONTINUOUS, name = 'Optimal Product Production')

mod.remove(mod.getConstrs())
mod.addConstr(A @ reqs2 <= availabilities, name='c2') 

# recalculate objective (it should be unchanged since the resource cost of the new product is greater than its sale price)
mod.setObjective((A @ prices2), GRB.MAXIMIZE)

# print out new solution (should be unchanged following same logic)
mod.optimize()
print("\n\nFOR PART II:\n")
print(f"The Resource Cost of the New Product is {rcNew}.\n")
print("When Sale Price = Resource Cost - 1:")
if mod.status == 2:
    print("The solution found is optimal.")
    print(f"The optimal objective value is {mod.objVal}")
    print("The optimal solution is")
    """
    for v in mod.getVars():
        if v.x != 0:
            print(f"{v.varName} = {v.x}")
    """
    ntp = []
    for i in range(len(mod.getVars())):
        if mod.getVars()[i].x != 0:
            ntp.append((i, mod.getVars()[i].x))
    for p in ntp:
        print(f"Production of Product {p[0]} = {p[1]}")
else:
    print("The solution found is not optimal.")



# Adjust sale price of new product to be 1 more than the resource cost and update model accordingly

# add price of new product to price array (out of place for clarity)
prices2[32] = (rcNew + 1)

# recalculate objective using updated price array
mod.setObjective((A @ prices2), GRB.MAXIMIZE)

# print out new solution (should changed following same logic)
mod.optimize()
print("\nWhen Sale Price = Resource Cost + 1:")
if mod.status == 2:
    print("The solution found is optimal.")
    print(f"The optimal objective value is {mod.objVal}")
    print("The optimal solution is")
    """
    for v in mod.getVars():
        if v.x != 0:
            print(f"{v.varName} = {v.x}")
    """
    ntp = []
    for i in range(len(mod.getVars())):
        if mod.getVars()[i].x != 0:
            ntp.append((i, mod.getVars()[i].x))
    for p in ntp:
        print(f"Production of Product {p[0]} = {p[1]}")
else:
    print("The solution found is not optimal.")
