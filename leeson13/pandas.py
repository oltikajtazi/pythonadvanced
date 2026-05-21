import pandas as prodct

import pandas as pd

product = ["apple","bananas","oranges","grapes","pineaple"]

sales = [150,200,180,90,60]

sales_series = pd.Series(sales,index=product)

print(sales_series)


