#%%
import pyodbc as odbc
server = 'scprod.database.windows.net'
database = 'scprod'
username = input('enter user name')
password = input('enter password')
print(username)
print(password)
# Create a connection string
print('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

cnxn = odbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
username = ''
password = ''
print(cnxn)
# Create a cursor
cursor = cnxn.cursor()

# Execute a query
# cursor.execute('SELECT * FROM <table_name>')

#%%
from collections import defaultdict
empty = defaultdict(set)
print(empty)
edges = {(1,2),(2,4),(4,5),(1,3),(3,4)} 


for (i,j) in edges:
    empty[i].add(j)

empty