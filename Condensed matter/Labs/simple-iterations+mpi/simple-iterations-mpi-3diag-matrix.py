#!/Library/Frameworks/Python.framework/Versions/3.5/Resources/Python.app/Contents/MacOS/Python

#SIMPLE ITERATIONS + MPI4PY an exact 3 diagonal matrix

#run me from console with:
#mpirun -np [number-of-processes] [path-to-this-file]

import random
from mpi4py import MPI
from pprint import pprint
from copy import deepcopy as copy

comm = MPI.COMM_WORLD

sz = 10**2
rank = comm.rank
bunch = sz//comm.size


def _sync():
    global x, f
    if comm.rank == 0:
        for i in range(1, comm.size):
            comm.send(x, dest=i, tag=1)
            comm.send(f, dest=i, tag=2)
    else:
        x = comm.recv(source=0, tag=1)
        f = comm.recv(source=0, tag=2)
    comm.Barrier()

# core idea:
# A*x = b
# (A_new - E)*x = b
# x = -A_new*x + b

# this version uses an exact READY matrix I was asked to harcode

def makerow(sz, i): #this generates a row of a known [-A_new][b]
    rdict = {}
    if i == 0:
        return {i: 0, sz: 100} #if first row
    elif i == sz-1:
        return {i:0, sz:200} #if second row
    else:
        return {i-1: -0.5, i:0, i+1: -0.5, sz:0}  #if any other row

x = [1 for i in range(sz)]
nx = [0 for i in range(sz)]

f = True

if not comm.rank:
    print("start SI method")

iter_n = 1
while f: and iter_n < 1000:
    j = comm.rank
  
    for r in range(j*bunch, (j+1)*bunch):
        rd = makerow(sz, r)
        nx[r] = -sum([x[key] * value for key, value in rd.items() if key < sz]) + rd.get(sz)
    
    comm.Barrier()

    if comm.rank:
        comm.send(nx[j*bunch : (j+1)*bunch], dest=0)
    else:
        for j in range(1, comm.size):
            nx[j*bunch : (j+1)*bunch] = comm.recv(source=j)

    comm.Barrier()

    if not comm.rank:
        print("iteration {} finished".format(iter_n))
        f = max([abs(nx[i] - x[i]) for i in range(sz)]) > (0.1**5)
        x = copy(nx)
        

    comm.Barrier()
    _sync()
    iter_n += 1

if not comm.rank:
    print(x)














