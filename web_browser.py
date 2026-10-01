import os
import sqlite3
from flask import Flask,render_template,request,redirect,url_for,session
from dotenv import load_dotenv
load_dotenv()


app=Flask(__name__)
app.secret_key=os.getenv('SECRET_KEY','default_fallback_secret_key_for_development')
db_path=os.getenv('DATABASE_PATH','morninghub.db')



def init_db():
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()
    cursor.execute('''
            DROP TABLE IF EXISTS orders
        ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Coffee_item TEXT,
            Coffee_quantity TEXT,
            Coffee_flavor TEXT,
            Coffee_toppings TEXT,
            Tiffne_item TEXT,
            Tiffne_quantity INTEGER
            )''')
    conn.commit()
    conn.close()



@app.route('/')
def home_page():

    return render_template('Webpage.html')

@app.route ('/order_managemanet',methods=['GET','POST'])
def order_page():
    error = None
    orders = None
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    orders = conn.execute('SELECT * FROM orders ORDER BY id DESC').fetchall()
    conn.close() 
    return render_template('order_manage.html',orders=orders,error=error)


@app.route('/employee', methods=['GET', 'POST'])
def employee_page():
    if request.method == 'POST':
        email = request.form.get('email',' ').strip()
        password=request.form.get('password','').strip()
        if not email.endswith('@employee.com') and password != '1234@employee':
                 error = 'incorrect mail or password'
        else:
            return redirect(url_for('order_page'))
    return render_template('employee.html')

@app.route('/admin',methods=['GET','POST'])
def admin_page():
    error = None
    orders=None
    if request.method== 'POST':
        email= request.form.get('email','').strip()
        password=request.form.get('password','').strip()
        if not email.endswith('@admin.com')  and password != 'password':
                error='incorect email or password'
        else:
            return redirect(url_for('order_page'))
    return render_template('admin.html',error=error,orders=orders)



@app.route('/manager',methods=['GET','POST'])
def work_page():
    if request.method=='POST':
        session['coffee_started']=True
        session['coffee_choice']=request.form.get('coffee')
        session['tiffne_choice']=request.form.get('tiffne')
        

    if not session.get('coffee_started'):
        return redirect(url_for('home_page'))
        
    if session.get('coffee_choice')=='coffee' and not session.get('coffee_visited'):
        session['coffee_visited']=True
        return redirect(url_for('coffee_page'))
        
    if session.get('tiffne_choice')=='tiffne' and not session.get('tiffne_visited'):
        session['tiffne_visited']=True
        return redirect(url_for('tiffne_page'))
    print("----NEW ORDER DETAILS----")

    if session.get('coffee_choice')=='coffee':
        print("Coffee Order:")
        print(f"  - Item: {session.get('coffee_items')}")
        print(f"  - Quantity: {session.get('coffee_quantity')}")
        print(f"  - Flavor: {session.get('coffee_flavor')}")
        print(f"  - Toppings: {session.get('coffee_toppings')}")

    if session.get('tiffne_choice')=='tiffne':
        print("Tiffne Order:")
        print(f"  - Item: {session.get('tiffne_items')}")
        print(f"  - Quantity: {session.get('tiffne_quantity')}")
        
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()
    cursor.execute('''
        INSERT INTO orders (Coffee_item, Coffee_quantity, Coffee_flavor, Coffee_toppings, Tiffne_item, Tiffne_quantity)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        session.get('coffee_items', None),
        session.get('coffee_quantity', None),
        session.get('coffee_flavor', None),
        session.get('coffee_toppings', None),
        session.get('tiffne_items', None),
        session.get('tiffne_quantity', 0)
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('end_page'))






@app.route('/coffee', methods=['GET', 'POST'])
def coffee_page():
    if request.method =='POST':
        items=request.form.get('items')
        quantity=request.form.get('quantity')
        if items == 'milkshake':
            flavor=request.form.get('flavor')
        else:
            flavor=None
        toppings=request.form.get('topping')

        session['coffee_items'] = items 
        session['coffee_quantity'] = quantity
        session['coffee_flavor'] = flavor 
        session['coffee_toppings'] = toppings 
        return redirect(url_for('work_page'))
    return render_template('coffee_page.html')






@app.route('/tiffne', methods=['GET', 'POST'])
def tiffne_page():
    if request.method =='POST':
        items=request.form.get('item')
        quantity=request.form.get('quantity')
        session['tiffne_items'] = items
        session['tiffne_quantity'] = quantity 
        return redirect(url_for('work_page'))
    return render_template('tiffne_page.html')

@app.route('/delete-oldest', methods=['POST'])
def delete_oldest():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Deletes the row with the smallest ID
    cursor.execute('DELETE FROM orders WHERE id = (SELECT MIN(id) FROM orders)')
    conn.commit()
    conn.close()
    return redirect(url_for('order_page'))




@app.route('/finally')
def end_page():
    c_visit=session.get('coffee_visited',None)
    t_visit=session.get('tiffne_visited',None)
    c_item=session.get('coffee_items',None)
    c_quantity=session.get('coffee_quantity',None)
    c_flavor=session.get('coffee_flavor',None)
    c_topping=session.get('coffee_toppings',None)
    t_item=session.get('tiffne_items',None)
    t_quantity=session.get('tiffne_quantity',None)
    session.clear()
    return render_template( 
        'ending.html',
        c_visit=c_visit,
        t_visit=t_visit,
        c_item=c_item,
        c_quantity=c_quantity,
        c_flavor=c_flavor,
        c_topping=c_topping,
        t_item=t_item,
        t_quantity=t_quantity
    )




if __name__=='__main__':
    init_db()
    app_port=int(os.getenv('PORT',10000))
    app.run(host='0.0.0.0',port=app_port,debug=False)
