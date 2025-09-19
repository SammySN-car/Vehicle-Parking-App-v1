import matplotlib
matplotlib.use('Agg')
from flask import Flask,render_template,redirect,request,session,url_for
import sqlite3
import matplotlib.pyplot as plt 
import os

app=Flask(__name__)
app.secret_key='This is my secret key'

def databaseconn():
    conn = sqlite3.connect("data/parking.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")
    return conn


@app.route("/")
def redirectlogin():
    return redirect('/login')

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=='POST':
        Email=request.form['email']
        Password=request.form['password']

        conn=databaseconn()
        cursor=conn.cursor()
        
        cursor.execute("""select * from USERS
                       where Email_id=? and Password=?
        """,(Email,Password))

        user=cursor.fetchone()
        conn.close()

        if user:
            session['user_id']=user['id']
            session['role']=user['role']
            if user['role']=='admin':
                return redirect("/admin/dashboard")
            else:
                return redirect("/user/dashboard")
        else:
            return 'Invalid Information'

    return render_template('login.html')

@app.route("/forgotpass",methods=['GET','POST'])
def forgotpass():
    if request.method=='POST':
        conn=databaseconn()
        cursor=conn.cursor()
        email_id=request.form['email_id']
        cursor.execute('select * from USERS where Email_id=?',(email_id,))
        info=cursor.fetchone()
        if not info:
            conn.close()
            return 'Wrong Email_id'
        else:
            conn.close()
            session['email_id']=info['Email_id']
            return redirect('/newpass')
    return render_template('forgotpass.html')
        
@app.route('/newpass',methods=['GET','POST'])
def newpass():
    email_id=session.get('email_id')
    if not email_id:
        return redirect('forgotpass')
    if request.method=='POST':
        newpassw=request.form['new_password']
        currentpass=request.form['password']
        if newpassw!=currentpass:
            return 'Please write same answer in both fields'
        conn=databaseconn()
        cursor=conn.cursor()
        cursor.execute('update USERS set password=? where Email_id=?',(newpassw,email_id))
        conn.commit()
        conn.close()
        session.pop('email_id',None)
        return redirect('/login')
    return render_template('newpass.html')
    

@app.route("/register",methods=['GET','POST'])
def register():
    if request.method=='POST':
        Email=request.form['email']
        Password=request.form['password']
        Full_name=request.form['full_name']
        Address=request.form['address']
        Pincode=request.form['pincode']

        conn=databaseconn()
        cursor=conn.cursor()

        try:
            cursor.execute("""INSERT INTO USERS (Full_name,Email_id,Password,Address,Pincode) VALUES (?,?,?,?,?)""",(Full_name,Email,Password,Address,Pincode))
            conn.commit()
            conn.close()

            return redirect('/login')
        
        except sqlite3.IntegrityError:
            return 'User already exist'

    return render_template('Register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route("/admin/dashboard")
def admind():
    if session.get('role')!='admin':
        return 'Unauthorized user'
    conn=databaseconn()
    cursor=conn.cursor()
    cursor.execute("""select pl.*,
                   (select count(*) from Parking_spot ps where ps.lot_id=pl.id and ps.status='A') as Available,
                   (select count(*) from Parking_spot ps where ps.lot_id=pl.id and ps.status='O') as Occupied 
                   from Parking_lot pl""")
    lots=cursor.fetchall()
    full_lots=[]
    for lot in lots:
        cursor.execute("""select * from Parking_spot where lot_id=?""",(lot['id'],))
        spots=cursor.fetchall()
        full_lots.append({'lot':lot,'spots':spots})
    conn.close()
    return render_template('admin_dashboard.html',lots=full_lots)

@app.route('/admin/add_lot',methods=['GET','POST'])
def add_parking_lot():
    if session.get('role')!='admin':
        return 'Unauthorized user'
    
    if request.method=='POST':
        prime_location_name=request.form['prime_location_name']
        price=int(request.form['price'])
        max_spots=int(request.form['max_spots'])
        address=request.form['address']
        pincode=int(request.form['pincode'])

        conn=databaseconn()
        cursor=conn.cursor()

        cursor.execute("""INSERT INTO Parking_lot (prime_location_name,Price,Address,Pincode,maximum_number_of_spots) VALUES (?,?,?,?,?)""",(prime_location_name,price,address,pincode,max_spots))
        
        lot_id=cursor.lastrowid

        for _ in range(max_spots):
            cursor.execute("""INSERT INTO Parking_spot (lot_id) VALUES (?)""",(lot_id,))
        
        conn.commit()
        conn.close()
        
        return redirect('/admin/dashboard')
    
    return render_template('add_parking_lot.html')

@app.route('/admin/edit_lot/<int:lot_id>',methods=['GET','POST'])
def edit_parking_lot(lot_id):
    if session.get('role')!='admin':
        return 'Unauthorized user'
    
    conn=databaseconn()
    cursor=conn.cursor()

    if request.method=='POST':
        cursor.execute("""select maximum_number_of_spots from Parking_lot where id=?""",(lot_id,))
        lots=cursor.fetchone()[0]
        prime_location_name=request.form['prime_location_name']
        price=int(request.form['price'])
        max_spots=int(request.form['max_spots'])
        address=request.form['address']
        pincode=int(request.form['pincode'])

        cursor.execute("""update Parking_lot set prime_location_name=?,Price=?,Address=?,Pincode=?,maximum_number_of_spots=? where id=? """,(prime_location_name,price,address,pincode,max_spots,lot_id))
        if max_spots > lots:
            for _ in range(max_spots - lots):
                cursor.execute("""INSERT INTO Parking_spot (lot_id) VALUES (?)""", (lot_id,))
        elif max_spots<lots:
            cursor.execute("""select count(*) from Parking_spot where lot_id=? and status='A'""",(lot_id,))
            fot=cursor.fetchone()
            if fot!=None:
                fot=fot[0]
            else:
                fot=0
            star=lots-max_spots
            if star<=fot:
                cursor.execute("""DELETE FROM Parking_spot WHERE rowid IN (SELECT rowid FROM Parking_spot WHERE lot_id = ? AND status = 'A' LIMIT ?)""", (lot_id, star))

            else:
                conn.close()
                return 'Free up spot first to delete'             
        conn.commit()
        conn.close()
        return redirect('/admin/dashboard')
    
    cursor.execute('select * from Parking_lot where id=?',(lot_id,))
    lot=cursor.fetchone()
    conn.commit()
    conn.close()

    return render_template('edit_parking.html',lot=lot)

@app.route('/admin/delete_lot/<int:lot_id>')
def delete_lot(lot_id):
    if session.get('role')!='admin':
        return 'Unauthorized user'
    
    conn=databaseconn()
    cursor=conn.cursor()

    cursor.execute("""select count(*) from Parking_spot where lot_id=? and status='O'""",(lot_id,))
    count=cursor.fetchone()[0]
    if count>0:
        conn.close()
        return 'Cannot delete because all spots are not available'
    cursor.execute("""delete from Reserve_parking_spot where spot_id in(select id from Parking_spot where lot_id=?)""",(lot_id,))
    cursor.execute("""delete from Parking_spot where lot_id=?""",(lot_id,))
    cursor.execute("""delete from Parking_lot where id=?""",(lot_id,))
    conn.commit()
    conn.close()
    return redirect("/admin/dashboard")

@app.route('/admin/spot/<int:spot_id>',methods=['GET','POST'])
def view_delete_parking_spot(spot_id):
    if session.get('role')!='admin':
        return 'Unauthorized user'
    conn=databaseconn()
    cursor=conn.cursor()
    cursor.execute('select * from Parking_spot where id=?',(spot_id,))
    spot=cursor.fetchone()
    occupied=None
    if spot['status']=='O':
        cursor.execute("""select r.spot_id,r.user_id,r.vehicle_number,r.Parking_timestamp,r.Parking_cost from Reserve_parking_spot r where r.spot_id=?""",(spot_id,))
        occupied=cursor.fetchone()

    if request.method=='POST':
        if spot['status']=='A':
            cursor.execute("""delete from Reserve_parking_spot where spot_id=?""",(spot_id,))
            cursor.execute("""delete from Parking_spot where id=?""",(spot_id,))
            conn.commit()
            conn.close()
            return redirect('/admin/dashboard')
        else:
            conn.close()
            return 'cannot delete occupied parking slot'
    conn.close()
    return render_template('view_delete_spot.html',spot=spot,occupied=occupied)

@app.route('/admin/users')
def viewusers():
    if session.get('role')!='admin':
        return 'Unauthorized user'
    conn=databaseconn()
    cursor=conn.cursor()
    cursor.execute("""select id,Email_id,Full_name,Address,Pincode from USERS where role!='admin' """)
    users=cursor.fetchall()
    conn.close()
    return render_template('view_users.html',users=users)

@app.route('/admin/search',methods=['GET','POST'])
def admin_serach():
    if session.get('role')!='admin':
        return 'Unauthorized user'
    results=None
    search_type=None
    if request.method=='POST':
        search_type=request.form['search_by']
        search_term=request.form['search_term'] 

        conn=databaseconn()
        cursor=conn.cursor()
        if search_type == 'user_id':
            cursor.execute("""select * from USERS where id=?""",(search_term,))
            results=cursor.fetchall()
        
        elif search_type == 'location':
            cursor.execute("""select * from Parking_lot where prime_location_name like ?""",('%'+search_term+'%',))
            lots=cursor.fetchall()
            results=[]
            for lot in lots:
                cursor.execute("""select count(*) from Parking_spot where status='O' and lot_id=?""",(lot['id'],))
                occupied=cursor.fetchone()
                if occupied is not None:
                    occupied=occupied[0]
                else:
                    occupied=0
                cursor.execute("""select count(*) from Parking_spot where status='A' and lot_id=?""",(lot['id'],))
                available=cursor.fetchone()
                if available is not None:
                    available=available[0]
                else:
                    available=0
                results.append({'lot':lot,'occupied':occupied,'available':available})
        conn.close()
    return render_template('search_users.html',search_type=search_type,results=results)
    
@app.route('/admin/summary')
def admin_summary():
    if session.get('role')!='admin':
        return 'Unauthorized user'
    conn=databaseconn()
    cursor=conn.cursor()
    cursor.execute("""select * from Parking_lot""")
    parking_lots=cursor.fetchall()
    summary_data=[]
    total_occupied=0
    total_available=0
    total_revenue=0
    for lot in parking_lots:
        lot_id=lot['id']
        cursor.execute("""select count(*) from Parking_spot where status='O' and lot_id=?""",(lot_id,))
        occupied=cursor.fetchone()
        if occupied:
            occupied=occupied[0]
        else:
            occupied=0
        cursor.execute("""select count(*) from Parking_spot where status='A' and lot_id=?""",(lot_id,))
        available=cursor.fetchone()
        if available:
            available=available[0]
        else:
            available=0
        cursor.execute("""select SUM(r.Parking_cost) as price from Parking_spot ps,Reserve_parking_spot r where ps.lot_id=? and ps.id=r.spot_id and Leaving_timestamp is not NULL""",(lot_id,))
        result = cursor.fetchone()
        revenue = result['price'] if result and result['price'] is not None else 0
        total_available+=available
        total_occupied+=occupied
        total_revenue+=revenue
        summary_data.append({
            'lot':lot['id'],
            'available':available,
            'occupied':occupied,
            'revenue':revenue
        })
    if summary_data:
        loty=[]
        revenuety=[]
        occupiedty=[]
        availablety=[]
        for data in summary_data:
            loty.append(data['lot'])
            revenuety.append(data['revenue'])
            occupiedty.append(data['occupied'])
            availablety.append(data['available'])
        if any(revenuety):
            plt.clf()
            plt.pie(revenuety,labels=loty,autopct='%1.1f%%')
            plt.title('Revenue from each Parking lot')
            try:
                plt.tight_layout()
            except Exception as e:
                print("tight_layout error (pie):", e)
            plt.savefig('static/adminpie.png')
            plt.close()
        else:
            if os.path.exists('static/adminpie.png'):
                os.remove('static/adminpie.png')

        if any(availablety) or any(occupiedty):
            plt.clf()
            plt.figure(figsize=(8,5))
            x=list(range(len(loty)))
            width=0.4

            plt.bar([i - width/2 for i in x], availablety, width, label='Available')
            plt.bar([i + width/2 for i in x], occupiedty, width, label='Occupied')
            plt.title("Summary on available and occupied Parking_lots")
            plt.xticks(x,loty)
            plt.yticks(range(0, max(max(availablety),max(occupiedty))+1,1))
            plt.xlabel("Lot_id's with available and occupied")
            plt.ylabel('Count')
            plt.legend()
            plt.tight_layout()
            plt.savefig('static/adminbar.png')
            plt.close()
        else:
            if os.path.exists('static/adminbar.png'):
                os.remove('static/adminbar.png')
    else:
        for f in ['static/adminpie.png','static/adminbar.png']:
            if os.path.exists(f):
                os.remove(f)
    show_pie=os.path.exists('static/adminpie.png'),
    show_bar=os.path.exists('static/adminbar.png')
    
    conn.close()
    return render_template('admin_summary.html',show_bar=show_bar,show_pie=show_pie[0])

@app.route('/admin/edit_profile',methods=['GET','POST'])
@app.route('/user/edit_profile',methods=['GET','POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect('/login')
    user_id=session['user_id']
    conn=databaseconn()
    cursor=conn.cursor()
    if request.method=='POST':
        password=request.form['password']
        full_name=request.form['full_name']
        address=request.form['address']
        pincode=request.form['pincode']

        cursor.execute("""update USERS set Full_name=?,Address=?,Pincode=?,Password=? where id=?""",(full_name,address,pincode,password,user_id))
        conn.commit()
        conn.close()

        if session.get('role')!='user':
            return redirect('/admin/dashboard')
        else:
            return redirect('/user/dashboard')
    cursor.execute("""select * from USERS where id=?""",(user_id,))
    user=cursor.fetchone()
    conn.close()
    
    return render_template('edit_profile.html',user=user)

@app.route("/user/dashboard",methods=['GET','POST'])
def userd():
    if session.get('role')!='user':
        return 'unauthorized user'
    user_id=session['user_id']
    conn=databaseconn()
    cursor=conn.cursor()
    cursor.execute("""select r.id,pl.prime_location_name,r.vehicle_number,r.Leaving_timestamp from Reserve_parking_spot r,Parking_lot pl,Parking_spot ps where ps.lot_id=pl.id and r.spot_id=ps.id and r.user_id=? and r.Leaving_timestamp IS NOT NULL""",(user_id,))
    released=cursor.fetchall()
    cursor.execute("""select r.id,pl.prime_location_name,r.vehicle_number from Reserve_parking_spot r,Parking_lot pl,Parking_spot ps where ps.lot_id=pl.id and r.spot_id=ps.id and r.user_id=? and r.Leaving_timestamp IS NULL""",(user_id,))
    booked=cursor.fetchall()
    lots=[]
    search_term=''
    cursor.execute("""select * from Parking_lot""")
    details=cursor.fetchall()
    detail=[]
    for lot in details:
        cursor.execute("""select count(*) as Available from Parking_spot ps where ps.lot_id=? and ps.status='A'""",(lot['id'],))
        detai=cursor.fetchone()
        detail.append({**lot,'Available':detai['Available']})
    
    if request.method=='POST':
        search_term=request.form['search_term']
        cursor.execute("""select pl.id,pl.prime_location_name,count(*) as Available from Parking_lot pl,Parking_spot ps where ps.lot_id=pl.id and (pl.prime_location_name like ? or CAST(pl.Pincode as TEXT) like ?) and ps.status='A' group by pl.id,pl.prime_location_name""",('%'+search_term+'%','%'+search_term+'%'))
        lots=cursor.fetchall()
    conn.close()
    return render_template('user_dashboard.html',lots=lots,released=released,booked=booked,detail=detail)

@app.route("/user/book/<int:lot_id>",methods=['GET','POST'])
def user_book(lot_id):
    if session.get('role')!='user':
        return 'unauthorized user'
    user_id=session['user_id']
    conn=databaseconn()
    cursor=conn.cursor()
    cursor.execute("""select * from Parking_spot where lot_id=? and status='A'""",(lot_id,))
    spot=cursor.fetchone()
    if request.method=='POST':
        vehicle=request.form['vehicle_number']
        cursor.execute("""select * from Reserve_parking_spot where vehicle_number=? and Leaving_timestamp is null""",(vehicle,))
        check=cursor.fetchall()
        if check:
            return 'This vehicle is already parked'
        from datetime import datetime
        parking_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""insert into Reserve_parking_spot (spot_id,user_id,vehicle_number,Parking_timestamp) values (?,?,?,?)""",(spot['id'],user_id,vehicle,parking_time))
        cursor.execute("""update Parking_spot set status='O' where id=?""",(spot['id'],))
        conn.commit()
        conn.close()
        return redirect('/user/dashboard')
    conn.close()
    return render_template('user_book.html',spot=spot,user_id=user_id)

@app.route("/user/release/<int:reservation_id>",methods=['POST','GET'])
def user_release(reservation_id):
    if session.get('role')!='user':
        return 'unauthorized'
    conn=databaseconn()
    cursor=conn.cursor()
    cursor.execute("""select * from Reserve_parking_spot where id=?""",(reservation_id,))
    reservation=cursor.fetchone()
    from datetime import datetime
    now = datetime.now()
    leaving_time = now.strftime("%Y-%m-%d %H:%M:%S")
    start_time = datetime.strptime(reservation["Parking_timestamp"], "%Y-%m-%d %H:%M:%S")
    hours = max(1, int((now - start_time).total_seconds() // 3600))
    cursor.execute("""select * from Parking_spot where id=?""",(reservation['spot_id'],))
    spot=cursor.fetchone()
    cursor.execute("""select Price from Parking_lot where id=?""",(spot['lot_id'],))
    lot=cursor.fetchone()['Price']
    cost=hours*lot
    if request.method=='POST':
        cursor.execute("""update Reserve_parking_spot set Leaving_timestamp=?,Parking_cost=? where id=?""",(leaving_time,cost,reservation_id))
        cursor.execute("""update Parking_spot set status ='A' where id=?""",(reservation['spot_id'],))
        conn.commit()
        conn.close()
        return redirect("/user/dashboard")
    conn.close()
    return render_template('user_release.html',reservation=reservation,leaving_time=leaving_time,cost=cost)

@app.route('/user/summary')
def user_summary():
    if session.get('role')!='user':
        return 'unauthorized'
    user_id=session['user_id']
    conn=databaseconn()
    cursor=conn.cursor()
    cursor.execute("""select pl.id,count(*) as used from Parking_lot pl,Parking_spot ps,Reserve_parking_spot r where r.spot_id=ps.id and pl.id=ps.lot_id and r.user_id=? and r.Leaving_timestamp is not NULL group by pl.id""",(user_id,))
    summary=cursor.fetchall()
    to=[]
    fro=[]
    if summary:
        for info in summary:
            to.append(info['id'])
            fro.append(info['used'])
        plt.clf()
        plt.figure(figsize=(8,5))
        plt.bar(to,fro)
        plt.title("User Summary")
        plt.xticks(to)
        plt.yticks(range(0, max(fro)+1,1))
        plt.xlabel("Lot_id's")
        plt.ylabel('Times Booked')
        plt.tight_layout()
        plt.savefig('static/userbar.png')
        plt.close()
    else:
        if os.path.exists('static/userbar.png'):
            os.remove('static/userbar.png')
    show_bar=os.path.exists('static/adminbar.png')

    conn.close()
    return render_template('user_summary.html',show_bar=show_bar)

if __name__=='__main__':
    app.run(debug=True)