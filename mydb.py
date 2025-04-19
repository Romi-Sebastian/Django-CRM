import mysql.connector

dataBase = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='root'
)

# Prepare cursor object
cursorObject = dataBase.cursor()

# Create a database
cursorObject.execute("CREATE DATABASE razecrm")

print("Database created") 