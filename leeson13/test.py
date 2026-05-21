import pandas as pd
from arrey_manipulation import total_sum

product = ["apple","bananas","oranges","grapes","pineaple"]

sales = [150,200,180,90,60]

sales_series = pd.Series(sales,index=product)

print(sales_series)

print(sales_series ['grapes'])

total_sum


