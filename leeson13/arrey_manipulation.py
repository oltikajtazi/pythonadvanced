from traceback import print_tb

import numpy as np
from numpy.ma.core import reshape

array_2d =np.array([[1,2,3,4,5],[6,7,8,9,10]])

print(array_2d)

element = array_2d[1,2]
element2 = array_2d[1,4]

print(element)

print(element2)

dimension = array_2d.ndim
print(dimension)

madhsia = array_2d.size
print(madhsia)


sub_array = array_2d[:2,:2]
print(sub_array)


sub_array2 = array_2d[-4:-4:]
print(sub_array2)

total_sum = np.sum(array_2d)
print(total_sum)

sum_coluns = np.sum(array_2d,axis=0)

print(sum_coluns)

reshape_array = array_2d.reshape(
    (5,2))

print(reshape_array)

