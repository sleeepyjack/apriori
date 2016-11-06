import csv 
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

#input: 2d list
#output: prints the list   
def print_itemsets(D):
    for itemset in D:
        print itemset

#input: list of itemsets D (or C_i)
#ouput: array with frequencies for each item, e.g. [0,4,2] means first item occurs 0 times, 
#second item 4 times, third item 2 times
def get_support_count(D):
    count = []
    for itemset in D:
        count.append(itemset.count(1))
    return count

#input: 
#count: C_i, list with counts
#minimum_support_count
#output: returns list with indices of the itemsets that are frequent
def get_index_of_frequent_itemsets(count, minimum_support_count):
    return [i for i in range(0,len(frequency)) if (count[i]>minimum_support_count)]

#input: list of indices of the itemsets that should stay, i.e. that are frequent
#and list of itemsets L_i
#output: reduced itemsets
def get_reduced_list_of_itemsets(indices, itemsets):
    return [itemsets[i] for i in indices]

def get_tuples(itemset_number, itemset):
     return zip(itemset_number, itemset)


filename = 'dm1.csv'
minimum_support_count = 5

D = transpose(read_file(filename))
print_itemsets(D)

indices = get_index_of_frequent_itemsets(get_support_count(D), minimum_support_count)
frequent_itemsets = get_reduced_list_of_itemsets(indices, D)

#work with tuples, so we can keep track of WHICH itemset we're talking about
tuples = get_tuples(indices, frequent_itemsets)
for tuple in tuples:
    print tuple





