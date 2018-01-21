#!/Library/Frameworks/Python.framework/Versions/3.5/Resources/Python.app/Contents/MacOS/Python

#SIMPLE ITERATIONS + MPI4PY

#run me from console with:
# mpirun -np [number-of-processes] [path-to-this-file]

#this version gets the matrix from a file "simple-iterations-input"
#feel free to add another you sure about
#with a radnom-generated matrix the method is rarely converge

import random
from mpi4py import MPI
from pprint import pprint
from copy import deepcopy as copy

comm = MPI.COMM_WORLD

sz = 4
rank = comm.rank

def _sync():
    global m, x, f
    if comm.rank == 0:
        for i in range(1, comm.size):
            comm.send(m, dest=i, tag=0)
            comm.send(x, dest=i, tag=1)
            comm.send(f, dest=i, tag=3)
    else:
        m = comm.recv(source=0, tag=0)
        x = comm.recv(source=0, tag=1)
        f = comm.recv(source=0, tag=3)
    comm.Barrier()


if comm.rank == 0:
    m = [random.sample(range(-10, 10), sz+1) for i in range(sz)]
    x = [0 for i in range(sz)]
    nx = [0 for i in range(sz)]

    fin = open('simple-iterations-input', 'r')
    for i, s in enumerate(fin.readlines()):
        t = list(map(float, s.split()))
        for j, n in enumerate(t):
            m[i][j] = n

    print("Matrix:")
    pprint(m)
else:
    m, x, nx = None, None, None

f = True

_sync()

md = {}

# core idea:
# A*x = b
# (A_new - E)*x = b
# x = -A_new*x + b
# so...

for i in range(sz):
    c = m[i][i]

    j = comm.rank
    while j < sz+1:
        md[(i,j)] = -m[i][j] / c #...this is correct
        if j == sz:
            md[(i,j)] *= -1 #...this you better check out

        j += comm.size

if comm.rank:
    comm.send(md, dest=0)
else:
    for i in range(1, comm.size):
        md.update(comm.recv(source=i))

comm.Barrier()

if not comm.rank:
    for i in range(sz):
        for j in range(sz+1):
            m[i][j] = md[(i,j)]
            if i == j:
                m[i][j] = 0

_sync()

if not comm.rank:
    print("start SI method")

iter_n = 1
while f and iter_n < 100:
    j = comm.rank
    nxd = {}

    while j < sz:
        nxd[j] = m[j][-1] + sum([x[i]*m[j][i] for i in range(sz)])
        j += comm.size

    if comm.rank:
        comm.send(nxd, dest=0)
    else:
        for i in range(1, comm.size):
            nxd.update(comm.recv(source=i))

    comm.Barrier()

    if not comm.rank:
        for i in range(sz):
            nx[i] = nxd[i]
        print("iteration {} finished".format(iter_n))
        f = max([abs(nx[i] - x[i]) for i in range(sz)]) > (0.1 ** 5)
        x = copy(nx)

    comm.Barrier()
    _sync()
    iter_n += 1

if not comm.rank:
    pprint(x)
    print()














