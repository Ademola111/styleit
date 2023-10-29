import re, os, math, random, json, requests
from datetime import datetime, date, timedelta
from sqlalchemy import desc, func, extract
from flask import render_template, request, redirect, flash, session, url_for, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_share import Share
from flask_socketio import emit, disconnect

from styleitapp import app, db
from styleitapp.models import Designer, Customer, Posting, Image, Comment, Like, Share, Bookappointment, Subscription, Payment, Notification, Admin, Superadmin, Report, Transaction_payment, Bank, Bankcodes, Transfer, Login, Activitylog
from styleitapp import Message, mail
from styleitapp.forms import AdminLoginForm, AdminSignupForm


rows_per_page = 12
rows_page = 3

"""homepage"""
@app.route('/adminhome/')
def admin_home():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    
    if admin:
        return redirect('/admin/dashboard/')
    elif spadmin:
        return redirect('/spadmin/dashboard/')
    else:     
        return render_template('admin/index.html', spa=spa, adm=adm)


"""login"""
@app.route('/admin/login/', methods=['GET', 'POST'])
def admin_login():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    logini=AdminLoginForm()
    adsignup=AdminSignupForm()
    # rendering login template
    if request.method == 'GET':
        admi=Admin.query.all()
        return render_template('admin/adminlogin.html', logini=logini, admin=admin, spadmin=spadmin, spa=spa, adm=adm, adsignup=adsignup, admi=admi)
    
    if request.method == "POST":
        email=request.form.get('email')
        pwd = request.form.get('pwd')
        # validating form data field
        if email=="" or pwd=="":
            flash('one or more field is empty', 'danger')
            return redirect('/admin/login/')
        
        if email !="" or pwd !="":
            # quering Customer by filtering with email
            adm=db.session.query(Admin).filter(Admin.admin_email==email).first()
            spa=db.session.query(Superadmin).filter(Superadmin.spadmin_email==email).first()           
            if adm and adm.admin_status=='active':
                # checking password hash
                if check_password_hash(adm.admin_pass,pwd):
                    session['admin']=adm.admin_id
                    lo=Login(login_email=adm.admin_email, login_adminid=adm.admin_id)
                    db.session.add(lo)
                    db.session.commit()
                    return redirect('/admin/dashboard/')
                
            elif spa and spa.spadmin_status=='active':
                if check_password_hash(spa.spadmin_pass, pwd):
                    session['superadmin']=spa.spadmin_id
                    lo=Login(login_email=spa.spadmin_email, login_spadminid=spa.spadmin_id)
                    db.session.add(lo)
                    db.session.commit()
                    return redirect('/admin/dashboard/')
            else:
                if adm and adm.admin_status=='deactive':
                    flash('You have been logged out of the portal. kindly contact the necessary authority', 'warning')
                    return redirect('/admin/login/')
                elif spa and spa.spadmin_status=='deactive':
                    flash('You have been logged out of the portal. kindly contact the necessary authority', 'warning')
                    return redirect('/admin/login/')
                flash('kindly supply a valid email address and password', 'warning')
                return render_template('admin/adminlogin.html', logini=logini, adm=adm, spa=spa)
        else:
            flash('Invalid Credentials', 'warning')
            return render_template('admin/adminlogin.html', logini=logini, adm=adm, spa=spa)


"""Admin Forgotten Password"""
@app.route('/admin/forgottenpassword/', methods=['POST', 'GET'])
def adminforgottenpass():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    if admin or spadmin:
        return redirect('/admin/dashboard/')
    
    if request.method == "GET":
        return render_template('admin/adminforgottenpassword.html')
    
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        pwd=request.form.get('pwd')
        cpwd=request.form.get('cpwd')
       
        #validating fileds
        if username =="" or email =="" or pwd =="" or cpwd =="":
            flash('One or more field is empty', 'warning')
            return render_template('admin/adminforgottenpassword.html')
        elif pwd != cpwd:
            flash('invalid credential supplied', 'danger')
            return redirect('/admin/forgottenpassword/')
        else:
            formated = generate_password_hash(pwd)
            cust=Admin.query.filter(Admin.admin_email==email).first()
            spa=Superadmin.query.filter(Superadmin.spadmin_email==email).first()
            if cust:                
                if cust and cust.admin_status=='deactive':
                    flash('Record cannot be found', 'warning')
                    return redirect('/admin/forgottenpassword/')
                elif check_password_hash(cust.admin_pass,pwd):
                    flash('This password have been used earlier','danger')
                    return redirect('/admin/forgottenpassword/')
                else:
                    if cust.admin_secretword == username:
                        cust.admin_pass=formated
                        db.session.commit()
                        flash('password updated successfully', 'success')
                        return redirect('/admin/login/')
            elif spa:                
                if spa and spa.spadmin_status=='deactive':
                    flash('Record cannot be found', 'warning')
                    return redirect('/admin/forgottenpassword/')
                elif check_password_hash(spa.spadmin_pass,pwd):
                    flash('This password have been used earlier','danger')
                    return redirect('/admin/forgottenpassword/')
                else:
                    if spa.spadmin_secretword == username:
                        spa.spadmin_pass=formated
                        db.session.commit()
                        flash('password updated successfully', 'success')
                        return redirect('/admin/login/')
            else:                 
                flash('invalid email address', 'danger')
                return redirect('/admin/forgottenpassword/')


"""Admin and Superadmin Dashboard"""
@app.route('/admin/dashboard/', methods=['GET', 'POST'])
def dashboard():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if admin==None and spadmin==None:
        return redirect('/adminhome/')

    if request.method == 'GET':
        """the main query for the production"""
        subq_likes = db.session.query(Like.like_postid, func.count(Like.like_id).label('like_count')).group_by(Like.like_postid).subquery()
        subq_comments = db.session.query(Comment.com_postid, func.count(Comment.com_id).label('com_count')).group_by(Comment.com_postid).subquery()
        subq_shares = db.session.query(Share.share_postid, func.count(Share.share_id).label('share_count')).group_by(Share.share_postid).subquery()
        
        """query post without daily rank"""           
        pstn = db.session.query(Posting).outerjoin(subq_likes, Posting.post_id==subq_likes.c.like_postid).outerjoin(subq_comments, Posting.post_id==subq_comments.c.com_postid).outerjoin(subq_shares, Posting.post_id==subq_shares.c.share_postid).filter(Posting.post_id==Image.image_postid).order_by(desc(subq_likes.c.like_count), desc(subq_comments.c.com_count), desc(subq_shares.c.share_count), desc(Posting.post_date)).all()
        appt=Bookappointment.query.order_by(desc(Bookappointment.ba_id)).all()
        pymt=Payment.query.order_by(desc(Payment.payment_id)).all()
        sublist = Subscription.query.order_by(desc(Subscription.sub_date)).all()
        srepo = Report.query.order_by(desc(Report.report_id)).all()
        lk=Like.query.filter(Like.like_postid==Posting.post_id).all()
        des=Designer.query.all()
        cus=Customer.query.all()
        
        # Query data for the current day
        current_date = datetime.now()
        end_date = current_date + timedelta(days=1)  # You can change this for weeks, months, and years
        # Query data for the current week
        week_start = current_date - timedelta(days=current_date.weekday())
        week_end = week_start + timedelta(weeks=1)
        # Query data for the current month
        month_start = datetime(current_date.year, current_date.month, 1)
        month_end = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
        # Query data for the current year
        year_start = datetime(current_date.year, 1, 1)
        year_end = datetime(current_date.year + 1, 1, 1)
        if admin:
            prof=Admin.query.filter(Admin.admin_id==adm.admin_id).first()
            # daily achtivity
            day_data = db.session.query(Activitylog).filter(extract('day', Activitylog.date) >= extract('day', current_date), (extract('day', Activitylog.date) < extract('day', end_date)), Activitylog.adminid==adm.admin_id).all()
            # Weekly activity
            week_data = db.session.query(Activitylog).filter(Activitylog.date >= week_start, Activitylog.date < week_end, Activitylog.adminid==adm.admin_id).all()
            # Monthly Activity
            month_data = db.session.query(Activitylog).filter(Activitylog.date >= month_start, Activitylog.date < month_end, Activitylog.adminid==adm.admin_id).all()
            # Yearly activities
            year_data = db.session.query(Activitylog).filter(Activitylog.date >= year_start, Activitylog.date < year_end, Activitylog.adminid==adm.admin_id).all()
            return render_template('admin/admindashboard.html', admin=admin, spadmin=spadmin, srepo=srepo, spa=spa, adm=adm, prof=prof, lk=lk, appt=appt, pymt=pymt, sublist=sublist, pstn=pstn, des=des, cus=cus, day_data=day_data, week_data=week_data, month_data=month_data, year_data=year_data)
        
        elif spadmin:
            prof=Superadmin.query.filter(Superadmin.spadmin_id==spa.spadmin_id).first()
            # dailt actitity
            day_data = db.session.query(Activitylog).filter(extract('day', Activitylog.date) >= extract('day', current_date), (extract('day', Activitylog.date) < extract('day', end_date)), Activitylog.spadminid==spa.spadmin_id).all()
            # Weekly activity
            week_data = db.session.query(Activitylog).filter(Activitylog.date >= week_start, Activitylog.date < week_end, Activitylog.spadminid==spa.spadmin_id).all()
            # Monthly Activity
            month_data = db.session.query(Activitylog).filter(Activitylog.date >= month_start, Activitylog.date < month_end, Activitylog.spadminid==spa.spadmin_id).all()
            # Yearly activities
            year_data = db.session.query(Activitylog).filter(Activitylog.date >= year_start, Activitylog.date < year_end, Activitylog.spadminid==spa.spadmin_id).all()
            return render_template('admin/admindashboard.html', admin=admin, spadmin=spadmin, srepo=srepo, spa=spa, adm=adm, lk=lk, appt=appt, pymt=pymt, sublist=sublist, prof=prof, pstn=pstn, des=des, cus=cus, day_data=day_data, week_data=week_data,  month_data=month_data, year_data=year_data)
    

"""previous day activity"""
@app.route('/activity/prev/', methods=['POST'])
def previous_day():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if admin==None and spadmin==None:
        return redirect('/adminhome/')
    
    if request.method == 'POST':
        # Query data for the current day
        current_date = datetime.now()
        # Define previous and next periods
        previous_day = current_date - timedelta(days=1)
        if admin:
            previous_day_data = db.session.query(Activitylog).filter(extract('day', Activitylog.date) >= extract('day', previous_day), extract('day', Activitylog.date) < extract('day', current_date), Activitylog.adminid==adm.admin_id).all()
            message=json.dumps(len(previous_day_data))
            return message
        elif spadmin:
            previous_day_data = db.session.query(Activitylog).filter(extract('day', Activitylog.date) >= extract('day', previous_day), extract('day', Activitylog.date) < extract('day', current_date), Activitylog.spadminid==spa.spadmin_id).all()
            message=json.dumps(len(previous_day_data))
            return message
            

"""next day activity"""
@app.route('/activity/next/', methods=['POST'])
def next_day():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if admin==None and spadmin==None:
        return redirect('/adminhome/')
    
    if request.method == 'POST':
        # Query data for the current day
        current_date = datetime.now()
        # Define previous and next periods
        next_day = current_date + timedelta(days=1)
        if admin:
            next_day_data = db.session.query(Activitylog).filter(extract('day', Activitylog.date) >= extract('day', current_date), extract('day', Activitylog.date) < extract('day', next_day), Activitylog.adminid==adm.admin_id).all()
            message=json.dumps(len(next_day_data))
            return message
        elif spadmin:
            next_day_data = db.session.query(Activitylog).filter(extract('day', Activitylog.date) >= extract('day', current_date), extract('day', Activitylog.date) < extract('day', next_day), Activitylog.spadminid==spa.spadmin_id).all()
            message=json.dumps(len(next_day_data))
            return message


"""previous week activity"""
@app.route('/activity/prevweek/', methods=['POST'])
def previous_week():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if admin==None and spadmin==None:
        return redirect('/adminhome/')
    
    if request.method == 'POST':
         # Query data for the current date
        current_date = datetime.now()
        # Define previous periods
        previous_week = current_date - timedelta(weeks=1)
        endweek= previous_week + timedelta(days=6)
        if admin:
            previous_week_data = db.session.query(Activitylog).filter(Activitylog.date >= previous_week, Activitylog.date < endweek, Activitylog.adminid==adm.admin_id).all()
            message=json.dumps(len(previous_week_data))
            return message
        elif spadmin:
            previous_week_data =db.session.query(Activitylog).filter(Activitylog.date >= previous_week, Activitylog.date <  endweek, Activitylog.spadminid==spa.spadmin_id).all()
            message=json.dumps(len(previous_week_data))
            return message
        
                
"""next week activity"""
@app.route('/activity/nextweek/', methods=['POST'])
def next_week():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if admin==None and spadmin==None:
        return redirect('/adminhome/')
    
    if request.method == 'POST':
         # Query data for the current date
        current_date = datetime.now()
        # Define previous periods
        next_week = current_date + timedelta(weeks=1)
        if admin:
            previous_week_data = db.session.query(Activitylog).filter(Activitylog.date >= next_week, Activitylog.date < current_date, Activitylog.adminid==adm.admin_id).all()
            message=json.dumps(len(previous_week_data))
            return message
        elif spadmin:
            previous_week_data =db.session.query(Activitylog).filter(Activitylog.date >= next_week, Activitylog.date <  current_date, Activitylog.spadminid==spa.spadmin_id).all()
            message=json.dumps(len(previous_week_data))
            return message

"""previous month activity"""
@app.route('/activity/prevmonth/', methods=['POST'])
def previous_month():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if admin==None and spadmin==None:
        return redirect('/adminhome/')
    
    if request.method == 'POST':
         # Query data for the current date
        current_date = datetime.now()
        # Define previous periods
        month_start = datetime(current_date.year, current_date.month, 1)
        previous_month = month_start - timedelta(days=1)
        if admin:
            previous_month_data = db.session.query(Activitylog).filter(Activitylog.date >= previous_month, Activitylog.date < month_start, Activitylog.adminid==adm.admin_id).all()
            message=json.dumps(len(previous_month_data))
            return message
        elif spadmin:
            previous_month_data =db.session.query(Activitylog).filter(Activitylog.date >= previous_month, Activitylog.date < month_start, Activitylog.spadminid==spa.spadmin_id).all()
            message=json.dumps(len(previous_month_data))
            return message
        
                
"""next week activity"""
@app.route('/activity/nextmonth/', methods=['POST'])
def next_month():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if admin==None and spadmin==None:
        return redirect('/adminhome/')
    
    if request.method == 'POST':
         # Query data for the current date
        current_date = datetime.now()
        # Define previous periods
        month_start = datetime(current_date.year, current_date.month, 1)
        month_end = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
        next_month = month_start + timedelta(days=1)
        if admin:
            previous_week_data = db.session.query(Activitylog).filter(Activitylog.date >= month_start, Activitylog.date < next_month, Activitylog.adminid==adm.admin_id).all()
            message=json.dumps(len(previous_week_data))
            return message
        elif spadmin:
            previous_week_data =db.session.query(Activitylog).filter(Activitylog.date >= month_start, Activitylog.date <  next_month, Activitylog.spadminid==spa.spadmin_id).all()
            message=json.dumps(len(previous_week_data))
            return message
        
"""previous year activity"""
@app.route('/activity/prevyear/', methods=['POST'])
def previous_year():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if admin==None and spadmin==None:
        return redirect('/adminhome/')
    
    if request.method == 'POST':
         # Query data for the current date
        current_date = datetime.now()
        # Define previous periods
        current_year=current_date.year
        previous_year = current_date.replace(year=current_date.year - 1)
        if admin:
            previous_year_data = db.session.query(Activitylog).filter(Activitylog.date >= previous_year, Activitylog.date < current_year, Activitylog.adminid==adm.admin_id).all()
            message=json.dumps(len(previous_year_data))
            return message
        elif spadmin:
            previous_year_data =db.session.query(Activitylog).filter(Activitylog.date >= previous_year, Activitylog.date < current_year, Activitylog.spadminid==spa.spadmin_id).all()
            message=json.dumps(len(previous_year_data))
            return message
        
                
"""next year activity"""
@app.route('/activity/nextyear/', methods=['POST'])
def next_year():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if admin==None and spadmin==None:
        return redirect('/adminhome/')
    
    if request.method == 'POST':
         # Query data for the current date
        current_date = datetime.now()
        # Define previous periods
        current_year=current_date.year
        next_year = current_date.replace(year=current_date.year + 1)
        # year_end = datetime(current_date.year + 1, 1, 1)
        if admin:
            previous_year_data = db.session.query(Activitylog).filter(Activitylog.date >= next_year, Activitylog.date < current_year, Activitylog.adminid==adm.admin_id).all()
            message=json.dumps(len(previous_year_data))
            return message
        elif spadmin:
            previous_year_data =db.session.query(Activitylog).filter(Activitylog.date >= current_year, Activitylog.date < current_year, Activitylog.spadminid==spa.spadmin_id).all()
            message=json.dumps(len(previous_year_data))
            return message
        
        
                       
"""Trending section"""
@app.route('/admintrending/', methods=['GET', 'POST'])
def admin_trending():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    
    if admin==None and spadmin== None:
        return redirect('/')

    if request.method == "GET":
        today = date.today()
        adm=Admin.query.get(admin)
        spa=Superadmin.query.get(spadmin)
        
        if admin:
            """the main query for the production"""
            subq_likes = db.session.query(Like.like_postid, func.count(Like.like_id).label('like_count')).group_by(Like.like_postid).subquery()
            subq_comments = db.session.query(Comment.com_postid, func.count(Comment.com_id).label('com_count')).group_by(Comment.com_postid).subquery()
            subq_shares = db.session.query(Share.share_postid, func.count(Share.share_id).label('share_count')).group_by(Share.share_postid).subquery()
            
            
            """query post with daily rank this is for production"""
            pstn2 = db.session.query(Posting).outerjoin(subq_likes, Posting.post_id==subq_likes.c.like_postid).outerjoin(subq_comments, Posting.post_id==subq_comments.c.com_postid).outerjoin(subq_shares, Posting.post_id==subq_shares.c.share_postid).filter(extract('day', Posting.post_date) == extract('day', today), extract('month', Posting.post_date) == extract('month', today), extract('year', Posting.post_date) == extract('year', today)).order_by(desc(subq_likes.c.like_count), desc(subq_comments.c.com_count), desc(subq_shares.c.share_count), desc(Posting.post_date)).limit(1000).all()
            lk=Like.query.filter(Like.like_postid==Posting.post_id).all()
            return render_template('admin/admintrending.html', pstn2=pstn2, admin=admin, spadmin=spadmin, spa=spa, adm=adm, lk=lk)
            
        elif spadmin:
            """the main query for the production"""
            subq_likes = db.session.query(Like.like_postid, func.count(Like.like_id).label('like_count')).group_by(Like.like_postid).subquery()
            subq_comments = db.session.query(Comment.com_postid, func.count(Comment.com_id).label('com_count')).group_by(Comment.com_postid).subquery()
            subq_shares = db.session.query(Share.share_postid, func.count(Share.share_id).label('share_count')).group_by(Share.share_postid).subquery()
            
            """query post with daily rank this is for production"""
            pstn2 = db.session.query(Posting).outerjoin(subq_likes, Posting.post_id==subq_likes.c.like_postid).outerjoin(subq_comments, Posting.post_id==subq_comments.c.com_postid).outerjoin(subq_shares, Posting.post_id==subq_shares.c.share_postid).filter(extract('day', Posting.post_date) == extract('day', today), extract('month', Posting.post_date) == extract('month', today), extract('year', Posting.post_date) == extract('year', today)).order_by(desc(subq_likes.c.like_count), desc(subq_comments.c.com_count), desc(subq_shares.c.share_count), desc(Posting.post_date)).limit(1000).all()
            lk=Like.query.filter(Like.like_postid==Posting.post_id).all()
            return render_template('admin/admintrending.html', pstn2=pstn2, admin=admin, spadmin=spadmin, spa=spa, adm=adm, lk=lk)
        
            
""" post detail session """
@app.route('/adminpost/<id>/')
def admin_post(id):
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if admin==None and spadmin== None:
        return redirect('/')

    if request.method == 'GET':
        pstn=db.session.query(Posting).filter(Posting.post_id==Image.image_postid, Posting.post_id==id).first()
        compost = Posting.query.filter_by(post_id=id).first_or_404()
        comnt=db.session.query(Comment).filter(Comment.com_postid==compost.post_id).order_by(Comment.path.asc()).all()
        share = db.session.query(Share).filter(Share.share_postid==compost.post_id).all()
        lk=Like.query.filter(Like.like_postid==Posting.post_id).all()
        for i in lk:
            print(i)
        return render_template('admin/adminpost.html', spadmin=spadmin, admin=admin, adm=adm,spa=spa,comnt=comnt, pstn=pstn, share=share, i=i)


"""ban section"""
@app.route('/ban/', methods=['GET', 'POST'])
def ban():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if admin==None and spadmin== None:
        return redirect('/')
    
    if request.method=='POST':
        url=request.url
        postid = request.form.get('postid')
        comid = request.form.get('comid')
        if postid =="":
            flash('file error', 'danger')
            return redirect(f'/adminpost/{postid}/')
        elif comid =="":
            flash('file error', 'danger')
            return redirect(f'/adminpost/{postid}/')
        else:
            if adm:
                if postid:
                    if postid !="":
                        posi = Posting.query.filter_by(post_id=postid).first()
                        posi.post_suspend='suspended'
                        posi.post_adminid=adm.admin_id
                        db.session.commit()
                        actlog = Activitylog(adminid=adm.admin_id, link=url)
                        db.session.add(actlog)
                        db.session.commit()
                        msg='success'
                        return jsonify(msg)
                elif comid:
                    if comid !="":
                        posi = Comment.query.filter_by(com_id=comid).first()
                        posi.com_suspend='suspended'
                        posi.com_adminid=adm.admin_id
                        db.session.commit()
                        actlog = Activitylog(adminid=adm.admin_id, link=url)
                        db.session.add(actlog)
                        db.session.commit()
                        msg='success'
                        return jsonify(msg)
            elif spa:
                if postid:
                    if postid !="":
                        posi = Posting.query.filter_by(post_id=postid).first()
                        posi.post_suspend='suspended'
                        posi.post_spadminid=spa.spadmin_id
                        db.session.commit() 
                        actlog = Activitylog(spadminid=spa.spadmin_id, link=url)
                        db.session.add(actlog)
                        db.session.commit()                       
                        msg='success'
                        return jsonify(msg)
                elif comid:
                    if comid !="":
                        posi = Comment.query.filter_by(com_id=comid).first()
                        posi.com_suspend='suspended'
                        posi.com_spadminid=spa.spadmin_id
                        db.session.commit()
                        actlog = Activitylog(spadminid=spa.spadmin_id, link=url)
                        db.session.add(actlog)
                        db.session.commit() 
                        msg='success'
                        return jsonify(msg)
            
        

"""delete section"""
@app.route('/trash/', methods=['GET', 'POST'])
def trash():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if admin==None and spadmin== None:
        return redirect('/')
    
    if request.method=='POST':
        url=request.url
        postid = request.form.get('postid')
        comid = request.form.get('comid')
        if postid =="":
            flash('file error', 'error')
            return redirect(f'/adminpost/{postid}/')
        elif comid =="":
            flash('file error', 'error')
            return redirect(f'/adminpost/{postid}/')
        else:
            if adm:
                if postid:
                    if postid !="":
                        posi = Posting.query.filter(Posting.post_id==postid).first()
                        posi.post_delete='deleted'
                        posi.post_adminid=adm.admin_id
                        db.session.commit()
                        actlog = Activitylog(adminid=adm.admin_id, link=url)
                        db.session.add(actlog)
                        db.session.commit()
                        msg='successfully deleted'
                        return jsonify(msg)
                elif comid:
                    if comid !="":
                        posi = Comment.query.filter(Comment.com_id==comid).first()
                        posi.com_delete='deleted'
                        posi.com_adminid=adm.admin_id
                        db.session.commit()
                        actlog = Activitylog(adminid=adm.admin_id, link=url)
                        db.session.add(actlog)
                        db.session.commit()
                        msg='successfully deleted'
                        return jsonify(msg)
            elif spa:
                if postid:
                    if postid !="":
                        posi = Posting.query.filter(Posting.post_id==postid).first()
                        posi.post_delete='deleted'
                        posi.post_spadminid=spa.spadmin_id
                        db.session.commit()
                        actlog = Activitylog(spadminid=spa.spadmin_id, link=url)
                        db.session.add(actlog)
                        db.session.commit()
                        msg='successfully deleted'
                        return jsonify(msg)   
                elif comid:
                    if comid !="":
                        posi = Comment.query.filter(Comment.com_id==comid).first()
                        posi.com_delete='deleted'
                        posi.com_spadminid=spa.spadmin_id
                        db.session.commit()
                        actlog = Activitylog(spadminid=spa.spadmin_id, link=url)
                        db.session.add(actlog)
                        db.session.commit()
                        msg='successfully deleted'
                        return jsonify(msg)
    

"""All Designers """
@app.route('/admin/designers/', methods=['GET', 'POST'])
def admin_designers():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    
    if admin==None and spadmin== None:
        return redirect('/')
        
    if request.method == 'GET':   
        adm=Admin.query.get(admin)
        spa=Superadmin.query.get(spadmin)
        page = request.args.get('page', 1, type=int)
        design=Designer.query.paginate(page=page, per_page=rows_page)
        if admin:
            return render_template('admin/admindesigners.html', design=design, spa=spa, adm=adm)
        elif spadmin:           
            return render_template('admin/admindesigners.html', design=design, spa=spa, adm=adm)


"""All Customers """
@app.route('/admin/allcustomers/', methods=['GET', 'POST'])
def admin_customers():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    
    if admin==None and spadmin== None:
        return redirect('/')
        
    if request.method == 'GET':   
        adm=Admin.query.get(admin)
        spa=Superadmin.query.get(spadmin)
        page = request.args.get('page', 1, type=int)
        design=Customer.query.paginate(page=page, per_page=rows_page)
        if admin:
            # design=Designer.query.paginate(page=page, per_page=rows_page)
            return render_template('admin/admin_allcustomers.html', design=design, spa=spa, adm=adm)
        elif spadmin:
            # design=Designer.query.paginate(page=page, per_page=rows_page)
            return render_template('admin/admin_allcustomers.html', design=design, spa=spa, adm=adm)
    

"""Designers Details """
@app.route('/designers/<id>/', methods=['GET'])
def admin_desi_detail(id):
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    
    if admin==None and spadmin== None:
        return redirect('/')
        
    if request.method == 'GET':   
        adm=Admin.query.get(admin)
        spa=Superadmin.query.get(spadmin)
        if admin:
            design=Designer.query.filter(Designer.desi_id==id).first()
            return render_template('admin/admindesignerdetail.html', design=design, spa=spa, adm=adm,)

        elif spadmin:
            design=Designer.query.filter(Designer.desi_id==id).first()
            return render_template('admin/admindesignerdetail.html', design=design, spa=spa, adm=adm,)

"""Customers Details """
@app.route('/customers/<id>/', methods=['GET'])
def admin_cust_detail(id):
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    
    if admin==None and spadmin== None:
        return redirect('/')
        
    if request.method == 'GET':   
        adm=Admin.query.get(admin)
        spa=Superadmin.query.get(spadmin)
        if admin:
            design=Customer.query.filter(Customer.cust_id==id).first()
            return render_template('admin/admin_customerdetail.html', design=design, spa=spa, adm=adm,)
        elif spadmin:
            design=Customer.query.filter(Customer.cust_id==id).first()
            return render_template('admin/admin_customerdetail.html', design=design, spa=spa, adm=adm,)


"""admin and superadmin logout session"""
@app.route('/admin/logout/')
def admin_logout():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    if admin==None and spadmin==None:
        return redirect('/')
        
    if request.method == 'GET':
        if admin:
            session.pop('admin', None)
            lo=Login.query.filter_by(login_adminid=admin, logout_date=None).first()
            lo.logout_date=datetime.utcnow()
            db.session.commit()            
            return redirect('/adminhome')
        elif spadmin:
            session.pop('superadmin', None)
            lo=Login.query.filter_by(login_spadminid=spadmin, logout_date=None).first()
            lo.logout_date=datetime.utcnow()
            db.session.commit()            
            return redirect('/adminhome')

 
"""Error 404 page"""
@app.errorhandler(404)
def page_not_found(error):
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    if admin==None and spadmin==None:
        return redirect('/admin/login/')
    else:
        adm=Admin.query.get(admin)
        spa=Superadmin.query.get(spadmin)
        return render_template('admin/error.html', adm=adm, spa=spa, error=error),404


"""Search section"""
@app.route('/adminsearch/', methods=['POST'])
def admin_search():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if admin:
        word=request.form.get('search')
        page = request.args.get('page', 1, type=int)
        wordsearch=Posting.query.outerjoin(Designer, Posting.post_id==Designer.desi_id).filter(Posting.post_title.ilike(f'%{word}%') | Posting.post_body.ilike(f'%{word}%') | Designer.desi_businessName.ilike(f'%{word}%') | Designer.desi_fname.ilike(f'%{word}%') | Designer.desi_lname.ilike(f'%{word}%')).order_by(desc(Posting.post_id)).paginate(page=page, per_page=rows_per_page)
    elif spadmin:
        word=request.form.get('search')
        page = request.args.get('page', 1, type=int)
        wordsearch=Posting.query.outerjoin(Designer, Posting.post_id==Designer.desi_id).filter(Posting.post_title.ilike(f'%{word}%') | Posting.post_body.ilike(f'%{word}%') | Designer.desi_businessName.ilike(f'%{word}%') | Designer.desi_fname.ilike(f'%{word}%') | Designer.desi_lname.ilike(f'%{word}%')).order_by(desc(Posting.post_id)).paginate(page=page, per_page=rows_per_page)
    return render_template('user/search.html', wordsearch=wordsearch, word=word, adm=adm, spa=spa)

@app.route('/deactivat/', methods=['POST'])
def deactivat():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    
    if request.method == "POST":
        url=request.url
        desi=request.form.get('desi_id')
        cust=request.form.get('cust_id')
        if adm:
            if desi:
                if desi !="":
                    dess=Designer.query.filter_by(desi_id=desi).first()
                    dess.desi_access='deactived'
                    dess.desi_adminid=adm.admin_id
                    db.session.commit()
                    actlog = Activitylog(adminid=adm.admin_id, link=url)
                    db.session.add(actlog)
                    db.session.commit()
                    message='Deactivated'
                    return jsonify(message)
            elif cust:
                if cust !="":
                    cust=Customer.query.filter_by(cust_id=cust).first()
                    cust.cust_access='deactived'
                    cust.cust_adminid=adm.admin_id
                    db.session.commit()
                    actlog = Activitylog(adminid=adm.admin_id, link=url)
                    db.session.add(actlog)
                    db.session.commit()
                    message='Deactivated'
                    return jsonify(message)
        elif spa:
            if desi:
                if desi !="":
                    dess=Designer.query.filter_by(desi_id=desi).first()
                    dess.desi_access='deactived'
                    dess.desi_spadminid=spa.spadmin_id
                    db.session.commit()
                    actlog = Activitylog(spadminid=spa.spadmin_id, link=url)
                    db.session.add(actlog)
                    db.session.commit()
                    message='Deactivated'
                    return jsonify(message)
            elif cust:
                if cust !="":
                    cust=Customer.query.filter_by(cust_id=cust).first()
                    cust.cust_access='deactived'
                    cust.cust_spadminid=spa.spadmin_id
                    db.session.commit()
                    actlog = Activitylog(spadminid=spa.spadmin_id, link=url)
                    db.session.add(actlog)
                    db.session.commit()
                    message='Deactivated'
                    return jsonify(message)

@app.route('/activat/', methods=['POST'])
def activat():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if request.method == "POST":
        url=request.url
        desi=request.form.get('desi_id')
        cust=request.form.get('cust_id')
        if adm:
            if desi:
                if desi !="":
                    dess=Designer.query.filter_by(desi_id=desi).first()
                    dess.desi_access='actived'
                    dess.desi_adminid=adm.admin_id
                    db.session.commit()
                    actlog = Activitylog(adminid=adm.admin_id, link=url)
                    db.session.add(actlog)
                    db.session.commit()
                    message='Activated'
                    return jsonify(message)
            elif cust:
                if cust !="":
                    cust=Customer.query.filter_by(cust_id=cust).first()
                    cust.cust_access='actived'
                    cust.cust_adminid=adm.admin_id
                    db.session.commit()
                    actlog = Activitylog(adminid=adm.admin_id, link=url)
                    db.session.add(actlog)
                    db.session.commit()
                    message='Activated'
                    return jsonify(message)
        elif spa:
            if desi:
                if desi !="":
                    dess=Designer.query.filter_by(desi_id=desi).first()
                    dess.desi_access='actived'
                    dess.desi_spadminid=spa.spadmin_id
                    db.session.commit()
                    actlog = Activitylog(spadminid=spa.spadmin_id, link=url)
                    db.session.add(actlog)
                    db.session.commit()
                    message='Activated'
                    return jsonify(message)
            elif cust:
                if cust !="":
                    cust=Customer.query.filter_by(cust_id=cust).first()
                    cust.cust_access='actived'
                    cust.cust_spadminid=spa.spadmin_id
                    db.session.commit()
                    actlog = Activitylog(spadminid=spa.spadmin_id, link=url)
                    db.session.add(actlog)
                    db.session.commit()
                    message='Activated'
                    return jsonify(message)
            
"""admin signup"""
@app.route('/admin/signup/', methods=['GET', 'POST'])
def adminsignup():
    if request.method == 'GET':
        return redirect('/admin/login/')
       
    if request.method == 'POST':
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        secretword=request.form.get('secretword')
        email=request.form.get('email')
        phone=request.form.get('phone')
        pwd=request.form.get('pwd')
        cpwd=request.form.get('cpwd')
        address= request.form.get('address')
        gender=request.form.get('gender')
        pic=request.files.get('pic')
        original_name=pic.filename


        if fname=="" or lname=="" or secretword=="" or email=="" or phone=="" or pwd=="" or cpwd=="" or address=="" or gender=="":
            flash('One or more field is empty', 'danger')
            return redirect('/admin/signup/')
    
        # checking length of password
        elif len(pwd) < 8:
            flash('Password should be atleast 8 character long', 'warning')
            return redirect('/admin/signup/')
        # compairing password match
        elif pwd !=cpwd:
            flash('Password match error', 'danger')
            return redirect('/admin/signup/')
        else:
            # spliting to check email extension
            mail = email.split('@')
            if mail[1] not in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
                flash('kindly provide a valid email', 'warning')
                return redirect('/admin/signup/')
            else:
                eemail = mail[0] + '@' + mail[1]
                # hashing password
                formated = generate_password_hash(pwd)
                
                # checking image field if empty
                if original_name != "":
                    # spliting image path
                    extension = os.path.splitext(original_name)
                    if extension[1].lower() in ['.jpg', '.gif', '.png']:
                        fn=math.ceil(random.random()*10000000000)
                        saveas = str(fn) + extension[1]
                        pic.save(f'styleitapp/static/images/profile/admin/{saveas}')
                        # committing to Customer table
                        k=Admin(admin_fname=fname, admin_secretword=secretword, admin_lname=lname, admin_gender=gender, admin_phone=phone, admin_email=eemail, admin_pass=formated, admin_address=address, admin_pic=saveas)
                        db.session.add(k)
                        db.session.commit()
                        return redirect('/admin/signup/')
                    # return redirect('/admin/signup/')

"""searching for refno to approve payment"""
@app.route('/searchref/', methods=['POST'])
def searchref():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    url=request.url
    if admin and request.method=='POST':
        nomba=request.form.get('searchref')
        if nomba != "":
            pymt=Payment.query.filter_by(payment_transNo=nomba).first()
            typmt=Transaction_payment.query.filter_by(tpay_transNo=nomba).first()
            if pymt == None and typmt==None:
                message ={"message":f"This refno {nomba} is not available"}
                return message
            else:
                if pymt:
                    msg={"payment_id":pymt.payment_id, "payment_transNo":pymt.payment_transNo, "payment_transdate":str(pymt.payment_transdate), "payment_amount":pymt.payment_amount, "payment_status":pymt.payment_status, "payment_desiid":pymt.payment_desiid, "payment_subid":pymt.payment_subid, "desipaymentobj":pymt.desipaymentobj.desi_businessName}
                    message=json.dumps(msg)
                    actlog = Activitylog(adminid=admin, link=url)
                    db.session.add(actlog)
                    db.session.commit()
                    return message
                elif typmt:
                    msg={"tpay_id":typmt.tpay_id, "tpay_transNo":typmt.tpay_transNo, "tpay_transdate":str(typmt.tpay_transdate), "tpay_amount":typmt.tpay_amount, "tpay_status":typmt.tpay_status, "tpay_desiid":typmt.tpay_desiid, "tpay_custid":typmt.tpay_custid, "tpay_baid":typmt.tpay_baid, "desitpayobj":typmt.desitpayobj.desi_businessName, "custtpayobj":typmt.custtpayobj.cust_fname, "custtpayobj2":typmt.custtpayobj.cust_lname, "tpaybaobj":typmt.tpaybaobj.ba_paystatus, "tpaybaobj2":typmt.tpaybaobj.ba_custstatus, "tpay_currencyicon":typmt.tpay_currencyicon}
                    message=json.dumps(msg)
                    actlog = Activitylog(adminid=admin, link=url)
                    db.session.add(actlog)
                    db.session.commit()
                    return message
        else:
            message={"message":"your refno is incorrect"}
            return message
    elif spadmin and request.method=='POST':
        nomba=request.form.get('searchref')
        if nomba != "":
            pymt=Payment.query.filter_by(payment_transNo=nomba).first()
            typmt=Transaction_payment.query.filter_by(tpay_transNo=nomba).first()
            if pymt == None and typmt==None:
                message ={"message":f"This refno {nomba} is not available"}
                return message
            else:
                if pymt:
                    msg={"payment_id":pymt.payment_id, "payment_transNo":pymt.payment_transNo, "payment_transdate":str(pymt.payment_transdate), "payment_amount":pymt.payment_amount, "payment_status":pymt.payment_status, "payment_desiid":pymt.payment_desiid, "payment_subid":pymt.payment_subid, "desipaymentobj":pymt.desipaymentobj.desi_businessName}
                    message=json.dumps(msg)
                    actlog = Activitylog(spadminid=spadmin, link=url)
                    db.session.add(actlog)
                    db.session.commit()
                    return message
                elif typmt:
                    msg={"tpay_id":typmt.tpay_id, "tpay_transNo":typmt.tpay_transNo, "tpay_transdate":str(typmt.tpay_transdate), "tpay_amount":typmt.tpay_amount, "tpay_status":typmt.tpay_status, "tpay_desiid":typmt.tpay_desiid, "tpay_custid":typmt.tpay_custid, "tpay_baid":typmt.tpay_baid, "desitpayobj":typmt.desitpayobj.desi_businessName, "custtpayobj":typmt.custtpayobj.cust_fname, "custtpayobj2":typmt.custtpayobj.cust_lname, "tpaybaobj":typmt.tpaybaobj.ba_paystatus, "tpaybaobj2":typmt.tpaybaobj.ba_custstatus, "tpay_currencyicon":typmt.tpay_currencyicon}
                    message=json.dumps(msg)
                    print(message)
                    actlog = Activitylog(spadminid=spadmin, link=url)
                    db.session.add(actlog)
                    db.session.commit()
                    return message
        else:
            message={"message":"your refno is incorrect"}
            return message
    else:
        return redirect('/adminhome')
    
"""approve payment"""
@app.route('/approve/<id>/', methods=['GET'])
def approve_payment(id):
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    linkurl=request.url
    
    if admin and request.method=='GET' or spadmin and request.method=='GET':        
        typm=Transaction_payment.query.filter_by(tpay_transNo=id).first()
        desi=typm.desitpayobj.desi_id
        sendname=typm.custtpayobj.cust_fname + " " + typm.custtpayobj.cust_lname
        bnk=Bank.query.filter_by(bnk_desiid=desi).first()
        bnkcode = Bankcodes.query.filter_by(name=bnk.bnk_bankname).first()
        ac= bnk.bnk_acno
        accd=bnkcode.code
        Tns=Transfer.query.filter_by(tf_tpayreference=typm.tpay_transNo).first()
        # confirm account number and bank code
        url = f"https://api.paystack.co/bank/resolve?account_number={ac}&bank_code={accd}"
        payload = {}
        headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_9ebd9bc239bcde7a0f43e2eab48b18ef1910356f"}
        response = requests.request("GET", url, headers=headers, data=payload)
        res=response.json()
        print(res)
        # generating transfer reciept
        # if res['data']['account_number']==bnk.bnk_acno and res['data']['account_name']==bnk.bnk_acname.upper():
        data = {"type": "nuban", "name": res['data']['account_name'], "account_number": res['data']['account_number'], "bank_code": accd, "currency": "NGN", "email":typm.desitpayobj.desi_email, "description":"payment for the just conculeded service"}
        url2 = "https://api.paystack.co/transferrecipient"
        headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_9ebd9bc239bcde7a0f43e2eab48b18ef1910356f"}
        response = requests.request("post", url2, headers=headers, data=json.dumps(data))
        res2=response.json()
        print(res2)
        if Tns==None:
            refno = int(random.random()*10000000) 
            session['refno'] = refno
            
            tf=Transfer(tf_createdAt=res2['data']['createdAt'], tf_updatedAt=res2['data']['updatedAt'], tf_reference=refno, tf_RecipientCode=res2['data']['recipient_code'], tf_receiverAcName=res2['data']['details']['account_name'], tf_receiverAcNo=res2['data']['details']['account_number'], tf_receiverbankName=res2['data']['details']['bank_name'], tf_receiverEmail=res2['data']['email'], tf_amountRemited=(typm.tpay_amount) - (typm.tpay_amount * 0.2), tf_integrationCode=res2['data']['integration'], tf_receiptId=res2['data']['id'], tf_message=res2['message'], tf_depositor=sendname, tf_tpayid=typm.tpay_id, tf_status='pending', tf_tpayreference=typm.tpay_transNo)
            db.session.add(tf)
            db.session.commit()
            actlog = Activitylog(adminid=adm.admin_id, link=linkurl)
            db.session.add(actlog)
            db.session.commit()
            return render_template('admin/approvepayment.html', admin=admin, spadmin=spadmin, adm=adm, spa=spa, desi=desi, typm=typm, bnk=bnk, data=res2, Tns=Tns)
        elif Tns.tf_reference==None:
            refno = int(random.random()*10000000) 
            session['refno'] = refno
            
            tf=Transfer(tf_createdAt=res2['data']['createdAt'], tf_updatedAt=res2['data']['updatedAt'], tf_reference=refno, tf_RecipientCode=res2['data']['recipient_code'], tf_receiverAcName=res2['data']['details']['account_name'], tf_receiverAcNo=res2['data']['details']['account_number'], tf_receiverbankName=res2['data']['details']['bank_name'], tf_receiverEmail=res2['data']['email'], tf_amountRemited=(typm.tpay_amount) - (typm.tpay_amount * 0.2), tf_integrationCode=res2['data']['integration'], tf_receiptId=res2['data']['id'], tf_message=res2['message'], tf_depositor=sendname, tf_tpayid=typm.tpay_id, tf_status='pending', tf_tpayreference=typm.tpay_transNo)
            db.session.add(tf)
            db.session.commit()
            actlog = Activitylog(adminid=adm.admin_id, link=linkurl)
            db.session.add(actlog)
            db.session.commit()
            return render_template('admin/approvepayment.html', admin=admin, spadmin=spadmin, adm=adm, spa=spa, desi=desi, typm=typm, bnk=bnk, data=res2, Tns=Tns)
        
        elif Tns.tf_reference !=None:
            return render_template('admin/approvepayment.html', admin=admin, spadmin=spadmin, adm=adm, spa=spa, desi=desi, typm=typm, bnk=bnk, data=res2, Tns=Tns)
        else:
            flash("Invalid Name and Account Number. Please check again", 'warning')
            return render_template('admin/approvepayment.html', admin=admin, spadmin=spadmin, adm=adm, spa=spa, desi=desi, typm=typm, bnk=bnk, data=res2, refno=refno, Tns=Tns)
    
    elif spadmin and request.method=='GET':        
        typm=Transaction_payment.query.filter_by(tpay_transNo=id).first()
        desi=typm.desitpayobj.desi_id
        sendname=typm.custtpayobj.cust_fname + " " + typm.custtpayobj.cust_lname
        bnk=Bank.query.filter_by(bnk_desiid=desi).first()
        bnkcode = Bankcodes.query.filter_by(name=bnk.bnk_bankname).first()
        ac= bnk.bnk_acno
        accd=bnkcode.code
        Tns=Transfer.query.filter_by(tf_tpayreference=typm.tpay_transNo).first()
        # confirm account number and bank code
        url = f"https://api.paystack.co/bank/resolve?account_number={ac}&bank_code={accd}"
        payload = {}
        headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_9ebd9bc239bcde7a0f43e2eab48b18ef1910356f"}
        response = requests.request("GET", url, headers=headers, data=payload)
        res=response.json()
        print(res)
        # generating transfer reciept
        # if res['data']['account_number']==bnk.bnk_acno and res['data']['account_name']==bnk.bnk_acname.upper():
        data = {"type": "nuban", "name": res['data']['account_name'], "account_number": res['data']['account_number'], "bank_code": accd, "currency": "NGN", "email":typm.desitpayobj.desi_email, "description":"payment for the just conculeded service"}
        url2 = "https://api.paystack.co/transferrecipient"
        headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_9ebd9bc239bcde7a0f43e2eab48b18ef1910356f"}
        response = requests.request("post", url2, headers=headers, data=json.dumps(data))
        res2=response.json()
        print(res2)
        if Tns==None:
            refno = int(random.random()*10000000) 
            session['refno'] = refno
            
            tf=Transfer(tf_createdAt=res2['data']['createdAt'], tf_updatedAt=res2['data']['updatedAt'], tf_reference=refno, tf_RecipientCode=res2['data']['recipient_code'], tf_receiverAcName=res2['data']['details']['account_name'], tf_receiverAcNo=res2['data']['details']['account_number'], tf_receiverbankName=res2['data']['details']['bank_name'], tf_receiverEmail=res2['data']['email'], tf_amountRemited=(typm.tpay_amount) - (typm.tpay_amount * 0.2), tf_integrationCode=res2['data']['integration'], tf_receiptId=res2['data']['id'], tf_message=res2['message'], tf_depositor=sendname, tf_tpayid=typm.tpay_id, tf_status='pending', tf_tpayreference=typm.tpay_transNo)
            db.session.add(tf)
            db.session.commit()
            actlog = Activitylog(spadminid=spa.spadmin_id, link=linkurl)
            db.session.add(actlog)
            db.session.commit()
            return render_template('admin/approvepayment.html', admin=admin, spadmin=spadmin, adm=adm, spa=spa, desi=desi, typm=typm, bnk=bnk, data=res2, Tns=Tns)
        elif Tns.tf_reference==None:
            refno = int(random.random()*10000000) 
            session['refno'] = refno
            
            tf=Transfer(tf_createdAt=res2['data']['createdAt'], tf_updatedAt=res2['data']['updatedAt'], tf_reference=refno, tf_RecipientCode=res2['data']['recipient_code'], tf_receiverAcName=res2['data']['details']['account_name'], tf_receiverAcNo=res2['data']['details']['account_number'], tf_receiverbankName=res2['data']['details']['bank_name'], tf_receiverEmail=res2['data']['email'], tf_amountRemited=(typm.tpay_amount) - (typm.tpay_amount * 0.2), tf_integrationCode=res2['data']['integration'], tf_receiptId=res2['data']['id'], tf_message=res2['message'], tf_depositor=sendname, tf_tpayid=typm.tpay_id, tf_status='pending', tf_tpayreference=typm.tpay_transNo)
            db.session.add(tf)
            db.session.commit()
            actlog = Activitylog(spadminid=spa.spadmin_id, link=linkurl)
            db.session.add(actlog)
            db.session.commit()
            return render_template('admin/approvepayment.html', admin=admin, spadmin=spadmin, adm=adm, spa=spa, desi=desi, typm=typm, bnk=bnk, data=res2, Tns=Tns)
        
        elif Tns.tf_reference !=None:
            return render_template('admin/approvepayment.html', admin=admin, spadmin=spadmin, adm=adm, spa=spa, desi=desi, typm=typm, bnk=bnk, data=res2, Tns=Tns)
        else:
            flash("Invalid Name and Account Number. Please check again", 'warning')
            return render_template('admin/approvepayment.html', admin=admin, spadmin=spadmin, adm=adm, spa=spa, desi=desi, typm=typm, bnk=bnk, data=res2, refno=refno, Tns=Tns)


"""initiating transfer of payment"""
@app.route('/sendfund/', methods=['GET', 'POST'])
def send_fund():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    linkurl=request.url
    if request.method=="GET":
        return redirect('/admin/logout/')
    
    if admin and request.method=='POST':
        refrno=request.form.get('refno')
        tf=Transfer.query.filter_by(tf_reference=refrno).first()
        data = {"amount":tf.tf_amountRemited, "reference":tf.tf_reference, "recipient":tf.tf_RecipientCode, "reason":tf.tf_message}
        url = "https://api.paystack.co/transfer"
        headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_9ebd9bc239bcde7a0f43e2eab48b18ef1910356f"}
        response = requests.request("post", url, headers=headers, data=json.dumps(data))
        print(response.text)
        actlog = Activitylog(adminid=adm.admin_id, link=linkurl)
        db.session.add(actlog)
        db.session.commit()
        rspjson = json.loads(response.text)
        print(rspjson)
        if rspjson.get('status') == True:
            authurl = rspjson['data']["transfer_code"]
            return redirect(authurl)
        else:
            return "Please try again"
        
    elif spadmin and request.method=='POST':
        refno=request.form.get('refno')
        tf=Transfer.query.filter_by(tf_reference=refno).first()
        data = {"amount":tf.tf_amountRemited, "reference":tf.tf_reference, "recipient":tf.tf_RecipientCode, "reason":tf.tf_message}
        url = "https://api.paystack.co/transfer"
        headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_9ebd9bc239bcde7a0f43e2eab48b18ef1910356f"}
        response = requests.request("post", url, headers=headers, data=json.dumps(data))
        print(response.text)
        actlog = Activitylog(spadminid=spa.spadmin_id, link=linkurl)
        db.session.add(actlog)
        db.session.commit()
        rspjson = json.loads(response.text) 
        print(rspjson)
        if rspjson.get('status') == True:
            authurl = rspjson['data']["transfer_code"]
            return redirect(authurl)
        else:
            return "Please try again"


@app.route('/verify_transfer', methods=['GET', 'POST'])
def verifytransfer():
    if request.method=='GET':
        return redirect('/adminhome')
    
    if request.method == 'POST':

        url = "https://api.paystack.co/transfer/{id_or_code}"

        payload = {}
        headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_9ebd9bc239bcde7a0f43e2eab48b18ef1910356f"}

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)


@app.route('/mail-notification', methods=['GET', 'POST'])
def admin_general_mail():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if request.method=='GET':
        return render_template('admin/maillinglist.html', admin=admin, spadmin=spadmin, adm=adm, spa=spa)

    if request.method=="POST":
        subj=request.form.get('subject')
        bodi = request.form.get('body')
        dsn=Designer.query.all()
        ctn = Customer.query.all()
        recipients = []
        for d in dsn:
            recipients.append(d.desi_email)
        for c in ctn:
            recipients.append(c.cust_email)
        if subj != None or bodi !=None:
            with app.app_context():
                for recipient in recipients:
                    subject = subj
                    body = bodi
                    msg = Message(subject=subject, recipients=[recipient])
                    # Attach a file (optional)
                    with app.open_resource('static/images/logo11.PNG') as attachment:
                        msg.attach('logo11.PNG', 'application/PNG', attachment.read())
                    msg.html = render_template('admin/email_template.html', subject=subject, body=body)
                    mail.send(msg)
                    flash('message sent', 'success')
            return redirect("/admin/dashboard/")
        else:
            flash('one or more filed is empty', 'danger')
            return render_template('admin/maillinglist.html', admin=admin, spadmin=spadmin, adm=adm, spa=spa)


"""All trending post admin"""
@app.route('/admin/alltrend', methods=['GET'])
def admin_alltrend():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    
    """the main query for the production"""
    subq_likes = db.session.query(Like.like_postid, func.count(Like.like_id).label('like_count')).group_by(Like.like_postid).subquery()
    subq_comments = db.session.query(Comment.com_postid, func.count(Comment.com_id).label('com_count')).group_by(Comment.com_postid).subquery()
    subq_shares = db.session.query(Share.share_postid, func.count(Share.share_id).label('share_count')).group_by(Share.share_postid).subquery()
    
    """query post without daily rank"""
    page = request.args.get('page', 1, type=int)            
    pstn = db.session.query(Posting).outerjoin(subq_likes, Posting.post_id==subq_likes.c.like_postid).outerjoin(subq_comments, Posting.post_id==subq_comments.c.com_postid).outerjoin(subq_shares, Posting.post_id==subq_shares.c.share_postid).filter(Posting.post_id==Image.image_postid).order_by(desc(subq_likes.c.like_count), desc(subq_comments.c.com_count), desc(subq_shares.c.share_count), desc(Posting.post_date)).paginate(page=page, per_page=rows_page)
    if admin:
        return render_template('admin/admin_alltrend.html', spa=spa, adm=adm, admin=admin, spadmin=spadmin, pstn=pstn)
    elif spadmin:
        return render_template('admin/admin_alltrend.html', spa=spa, adm=adm, admin=admin, spadmin=spadmin, pstn=pstn)
    

"""All appointment admin"""
@app.route('/admin/appointment', methods=['GET'])
def admin_appointment():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    page = request.args.get('page', 1, type=int)
    appt=Bookappointment.query.order_by(desc(Bookappointment.ba_id)).paginate(page=page, per_page=rows_page)
    if admin:
        return render_template('admin/admin_appointments.html', admin=admin, spadmin=spadmin, spa=spa, adm=adm, appt=appt)
    elif spadmin:
        return render_template('admin/admin_appointments.html', admin=admin, spadmin=spadmin, spa=spa, adm=adm, appt=appt)


"""All payment admin"""
@app.route('/admin/payment', methods=['GET'])
def admin_allpment():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    page = request.args.get('page', 1, type=int)
    pymt=Payment.query.order_by(desc(Payment.payment_id)).paginate(page=page, per_page=rows_page)
    if admin:
        return render_template('admin/admin_payment.html', admin=admin, spadmin=spadmin, spa=spa, adm=adm, pymt=pymt)
    elif spadmin:
        return render_template('admin/admin_payment.html', admin=admin, spadmin=spadmin, spa=spa, adm=adm, pymt=pymt)


"""All subscription admin"""
@app.route('/admin/subscription', methods=['GET'])
def admin_subscription():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    page = request.args.get('page', 1, type=int)
    sublist = Subscription.query.order_by(desc(Subscription.sub_date)).paginate(page=page, per_page=rows_per_page)
    if admin:
        return render_template('admin/admin_subscription.html', admin=admin, spadmin=spadmin, spa=spa, adm=adm, sublist=sublist)
    elif spadmin:
        return render_template('admin/admin_subscription.html', admin=admin, spadmin=spadmin, spa=spa, adm=adm, sublist=sublist)


"""All report admin"""
@app.route('/admin/report/', methods=['GET'])
def admin_report():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    page = request.args.get('page', 1, type=int)
    srepo = Report.query.order_by(desc(Report.report_id)).paginate(page=page, per_page=rows_per_page)
    if admin:
        return render_template('admin/admin_report.html', admin=admin, spadmin=spadmin, spa=spa, adm=adm, srepo=srepo)
    elif spadmin:
        return render_template('admin/admin_report.html', admin=admin, spadmin=spadmin, spa=spa, adm=adm, srepo=srepo)
    

"""deactivate admin"""
@app.route('/admin_deactivate/', methods=['POST', 'GET'])
def admin_deactivate():
    spadmin= session.get('superadmin')
    spa=Superadmin.query.get(spadmin)
    url=request.url
    if request.method == 'POST':
        jjj=request.form.get('admin_dact')
        print(jjj)
        adm=Admin.query.filter(Admin.admin_id==jjj).first()
        print(adm.admin_status)
        if adm.admin_status=='active':
            adm.admin_status='deactive'
            db.session.commit()
            actlog = Activitylog(spadminid=spa.spadmin_id, link=url)
            db.session.add(actlog)
            db.session.commit()
            return redirect('/admin/login/')
        elif adm.admin_status=='deactive':
            adm.admin_status='active'
            db.session.commit()
            actlog = Activitylog(spadminid=spa.spadmin_id, link=url)
            db.session.add(actlog)
            db.session.commit()
            return redirect('/admin/login/')
    else:
        return redirect('/admin/dashboard/')


@app.route('/staffactivity', methods=['GET'])
def staff_activity():
    spadmin= session.get('superadmin')
    spa=Superadmin.query.get(spadmin)
    
    if spadmin==None:
        return redirect('/')
    
    if request.method=='GET':
        current_date = datetime.now()
        target_month = current_date.month
        target_year = current_date.year
        result = db.session.query(Admin, func.sum(Activitylog.adminid).label('total_activities')).join(Activitylog).group_by(Admin.admin_id, extract('month', Activitylog.date)==target_month, func.extract('year', Activitylog.date) == target_year).order_by(func.sum(Activitylog.adminid).desc()).all()
        return render_template('admin/activity.html', spadmin=spadmin,result=result, spa=spa, month=target_month, year=target_year)