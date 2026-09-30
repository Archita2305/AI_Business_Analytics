import pandas as pd
from database import engine

query = query = """
SELECT region, SUM(sales) AS total_sales
FROM sales
GROUP BY region
ORDER BY total_sales DESC
"""

df = pd.read_sql(query, engine)

print(df)