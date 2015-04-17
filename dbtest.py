import mysql.connector

# Connection
connection = mysql.connector.connect(user='rpeace', password='3Q5CmaE7',
                            host='99.254.1.29',
                            database='Stocks')
 
# Cursor
cursor = connection.cursor()
 
# Execute Query
cursor.execute("SELECT * FROM Region;")
 
# Close Connection
connection.close()