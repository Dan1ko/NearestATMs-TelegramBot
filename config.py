import pymysql

my_token='TOKEN'
connection = pymysql.connect(host='localhost',
                             user='username',
                             password='password',
                             database='locations',
                             cursorclass=pymysql.cursors.DictCursor)
