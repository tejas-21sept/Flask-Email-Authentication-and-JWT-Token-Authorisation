# flask imports
import MySQLdb,random, string
from flask import Flask, request, jsonify
from numpy import identity
from app import app
from db import *
from flask_jwt_extended import JWTManager,create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash
from flask_bcrypt import Bcrypt
#from flask_mail import Mail, Message



class NameFieldError(Exception):           # Exception for interger used in name field
    def __init__(self,temp_var):
        self.msg = temp_var
        
class PhoneNumberError(Exception):         # Exception for phone number less/more than 10 digits.
    def __init__(self,temp_var):
        self.msg = temp_var

@app.route('/signup', methods = ['POST','GET'])
def register():
    try:
        cursor = mysql.connection.cursor() 
        name = request.form['name']
        if len([int(s) for s in name if s.isdigit()]) >0:
            raise NameFieldError("Number is not allowed in name field.") 
        
        password = request.form['password']
        
        phone = request.form['phone']
        if len(str(phone))<10 :
            raise PhoneNumberError("Phone Number is only of 10 digits.")
        
        mail=request.form['mail']

        try:
            cursor.execute(''' INSERT INTO log_data VALUES(%s,%s,%s,%s)''',(name,password,phone,mail))
            pw_bcrypt = bcrypt.generate_password_hash(password)
            cursor.execute(''' UPDATE log_data SET password = %s WHERE name = %s''',(pw_bcrypt,name))   
        except (MySQLdb.IntegrityError) as e:
            message = {'status':409,'message':'Username is already exist.'}
            resp = jsonify(message)
            resp.status_code = 409
            cursor.close()
            return resp
        
        mysql.connection.commit()
        message = {'status':200,'message':'User registered successfully.'}
        resp = jsonify(message)
        cursor.close()
        return resp
    except NameFieldError as e:
        message = {'status':406,'message':'Number is not allowed in name field.'}
        resp = jsonify(message)
        resp.status_code = 406
        return resp
                    
@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status':404,
        'message':'Not found: '+request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    
    return resp

JWTManager(app)
bcrypt = Bcrypt(app)
@app.route('/login', methods=['POST']) 
def login_user():
    cursor = mysql.connection.cursor()
    email = request.json.get('mail')
    password = request.json.get('password')
    print(f"\n{email} and {password}\n")
    cursor.execute( "SELECT password,name FROM log_data WHERE mail LIKE %s ", [email] )
    data = cursor.fetchone()
    mysql.connection.commit()
    if len(data) == 2  :
        hash= data[0]
        name= data[1]
        hash_password = bcrypt.check_password_hash(hash, password)
    
        if hash_password == True:
                refresh = create_refresh_token(identity=email)
                access = create_access_token(identity=email)
                
                resp = jsonify({'user': { 'refresh': refresh,'access': access,'username': name,'email': email}})
                resp.status_code = 200
                return resp
    
    resp = jsonify({'error': 'Wrong credentials. Check Username and Password.'})
    resp.status_code = 401
    return resp

#send_mail = Mail(app)
@app.route('/forget/', methods = ['POST'])
def forget():
    cursor = mysql.connection.cursor()
    email = request.json.get('mail')
    
    cursor.execute( "SELECT * FROM log_data WHERE mail LIKE %s ", [email] )
    data = cursor.fetchone()
    mysql.connection.commit()
     
    if data == None:
        mysql.connection.commit()
        return jsonify({'mail':email,'message':f'{email} is not registered.'})
    
    random_pass = ''.join(random.choices(string.digits+string.ascii_letters, k=8))
    new_pass = bcrypt.generate_password_hash(random_pass)
    cursor.execute( "UPDATE log_data SET password = %s WHERE mail LIKE %s ", [new_pass,email] )
    mysql.connection.commit()
    # msg = Message(
    #     f'Password Reset',
    #     sender ='djangoprotesting@gmail.com',
    #     recipients = [str(email)]
    #     )
    # msg.body = f'Hello {email}, \n\tYour new updated password is {random_pass}.'
    # send_mail.send(msg)
    return jsonify({'mail':email,'password':random_pass})

if __name__ =='__main__':
    app.run(debug=True) 