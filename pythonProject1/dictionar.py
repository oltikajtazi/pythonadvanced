numrat = {
    "KS": +383,
    "AL": +355,
    "IT": +39
}

numrat["KS"] = +377

print(numrat["KS"])

del  numrat["AL"]

print (numrat)

keys = numrat.keys()
vlerat = numrat.values()
print(keys)
print(vlerat)