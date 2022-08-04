from app import app
from flask_mysqldb import MySQL
import os

mysql = MySQL()

# MySQL configurations

mysql.init_app(app)


app.config['MYSQL_HOST'] =      "localhost" 
app.config['MYSQL_USER'] =      "root"      
app.config['MYSQL_PASSWORD'] =  "MySQL"     
app.config['MYSQL_DB'] =        "appt_login" 

MAIL_DEBUG = True

app.config['JWT_SECRET_KEY'] =   os.urandom(12)
 
app.config['MAIL_SERVER']= 'smtp.gmail.com' 
app.config['MAIL_PORT'] =  465
app.config['MAIL_USERNAME'] =  'Your GMAIL id'     # gmail user id
app.config['MAIL_PASSWORD'] =  'Password'     # gmail user password
app.config['MAIL_USE_TLS'] =  False
app.config['MAIL_USE_SSL'] =  True