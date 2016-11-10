import csv
import numpy as np
from numba import jit
import sys
from collections import defaultdict

#read file
#input: filename as string
#output: returns 2d list, with transactions in the rows, 1s and 0s are Integers
def read_file(filename):
    with open(filename,'rb') as csvfile:
        temp = csv.reader(csvfile, delimiter=',')
        D = list(temp)
    #cast string to int
    for i in range(0,len(D)):
        D[i] = map(int, D[i])
    return D

#input: 2d list
#output: returns transposed list
# from one row: one transaction to one row: one item
def transpose(D):
    return [list(i) for i in zip(*D)]

@jit("uint64(uint64, uint64)")
def diff(x, y):
    return x-y if y<x else y-x

pow2=2**np.arange(64, dtype=np.uint64)

#http://stackoverflow.com/questions/35113081/efficiently-build-an-integer-from-bits-of-a-boolean-numpy-array
@jit("uint64(uint64[:])")
def pack(arr):
    x = np.lib.pad(arr, (0, 64-(len(arr)%64)), 'constant').reshape(-1, 64)
    ret = np.empty(len(x), dtype=np.uint64)
    for index, elem in enumerate(x):
        y = np.uint64(0)
        for i in range(elem.size):
            y += pow2[i] * elem[i]
        ret[index] = y
    return ret

@jit("uint64(uint64)")
def popcount(n):
    n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
    n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
    n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
    n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
    n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
    n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32) # This last & isn't strictly necessary.
    return n

@jit("uint64(uint64[:])")
def arr_popcount(arr):
    count = 0
    for a in arr:
        count += popcount(a)
    return count

positive_border = defaultdict(list)
_positive_border = defaultdict(list)
negative_border = set()

def generate_frequent_subsets(subsets, min_support, level):
    new_subsets = defaultdict(list)
    for k1, v1 in subsets[level-2].iteritems():
        for k2, v2 in subsets[level-2].iteritems():
            key_union = set(k1).union(set(k2))
            if len(key_union) == level and not tuple(key_union) in new_subsets:
                val_union = []
                for x, y in zip(v1, v2):
                    val_union.append(x & y)
                val_union = np.array(val_union, dtype=np.uint64)
                if arr_popcount(val_union) >= min_support:
                    new_subsets[tuple(key_union)] = val_union
                else:
                    negative_border.add(tuple(key_union))
                    _positive_border[tuple(k1)] = v1
                    _positive_border[tuple(k2)] = v2
    if not new_subsets:
        return False
    subsets.append(new_subsets)
    return True

###############################################################################

min_support = float(sys.argv[2])
filename = str(sys.argv[1])

# read file
data = np.array(read_file(filename), dtype=np.uint64)
data_transposed = transpose(data)
frequent_subsets = [] #defaultdict(list)
for i, elem in enumerate(data_transposed):
    elem = pack(elem)
    if arr_popcount(elem) >= int(min_support*len(data)):
        frequent_subsets.append(defaultdict(list))
        frequent_subsets[0][(i,)] = elem

if not frequent_subsets:
    sys.exit(0)
#print frequent_subsets[0]
lvl = 2
while(True):
    if not generate_frequent_subsets(frequent_subsets, int(min_support*len(data)), lvl):
        break
    lvl += 1
max_support = 0
for k, v in _positive_border.iteritems():
    max_support = max(max_support, arr_popcount(v))
for k, v in _positive_border.iteritems():
    if arr_popcount(v) >= max_support:
        positive_border[k] = v

print negative_border
print positive_border



# print results
with open(str(sys.argv[3]), 'w') as f:
    #print "subsets::frequency"
    f.write("subsets::frequency\n")
    for s in frequent_subsets:
        for k, v in s.iteritems():
        #print k, "::", arr_popcount(v)
            f.write(str(k)+"::"+str(arr_popcount(v))+"\n")
