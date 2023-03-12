import re, os, math, random, json, requests
from datetime import datetime, date, timedelta
from sqlalchemy import desc, func, extract
from flask import render_template, request, redirect, flash, session, url_for, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_share import Share
from flask_socketio import emit, disconnect

from styleitapp import app, db
from styleitapp.models import Designer, Customer, Posting, Image, Comment, Like, Share, Bookappointment, Subscription, Payment, Notification, Admin, Superadmin, Report
from styleitapp.forms import AdminLoginForm, AdminSignupForm


rows_per_page = 12
rows_page = 20

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
            flash('Invalid Credentials', 'danger')
            return redirect('/admin/login/')
        
        if email !="" or pwd !="":
            # quering Customer by filtering with email
            adm=db.session.query(Admin).filter(Admin.admin_email==email).first()
            spa=db.session.query(Superadmin).filter(Superadmin.spadmin_email==email).first()
            if adm:
                formated_pwd=adm.admin_pass
                # checking password hash
                if formated_pwd==pwd:
                    session['admin']=adm.admin_id
                    return redirect('/admin/dashboard/')
            elif spa:
                formated_pwd=spa.spadmin_pass
                if formated_pwd==pwd:
                    session['superadmin']=spa.spadmin_id
                    return redirect('/admin/dashboard/')
            else:
                flash('kindly supply a valid email address and password', 'warning')
                return render_template('admin/adminlogin.html', logini=logini, adm=adm, spa=spa)
       


"""Admin Forgotten Password"""
@app.route('/admin/forgottenpassword/', methods=['POST', 'GET'])
def adminforgottenpass():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    if admin or spadmin:
        return redirect('/admin/dashboard/')
    
    if request.method == "GET":
        return render_template('admin/forgottenpassword.html')
    
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        pwd=request.form.get('pwd')
        cpwd=request.form.get('cpwd')
       
        #validating fileds
        if username =="" or email =="" or pwd =="" or cpwd =="":
            flash('One or more field is empty', 'warning')
            return render_template('admin/forgottenpassword.html')
        elif pwd != cpwd:
            flash('invalid credential supplied', 'danger')
            return redirect('/admin/forgottenpassword/')
        else:
            formated = generate_password_hash(pwd)
            cust=Admin.query.filter(Admin.admin_email==email).first()
            if cust.admin_secretword == username:
                cust.admin_pass=formated
                db.session.commit()
                flash('password updated successfully', 'success')
                return redirect('/admin/dashboard/')
            else:
                flash('invalid busiess name or email address', 'danger')
                return redirect('/admin/forgottenpassword/')


"""Admin and Superadmin Dashboard"""
@app.route('/admin/dashboard/', methods=['GET', 'POST'])
def dashboard():
    admin = session.get('admin')
    spadmin= session.get('superadmin')
    adm=Admin.query.get(admin)
    spa=Superadmin.query.get(spadmin)
    if admin==None and spadmin==None:
        return redirect('/')

    if request.method == 'GET':
        if admin:
            prof=Admin.query.filter(Admin.admin_id==adm.admin_id).first()
            
            """the main query for the production"""
            subq_likes = db.session.query(Like.like_postid, func.count(Like.like_id).label('like_count')).group_by(Like.like_postid).subquery()
            subq_comments = db.session.query(Comment.com_postid, func.count(Comment.com_id).label('com_count')).group_by(Comment.com_postid).subquery()
            subq_shares = db.session.query(Share.share_postid, func.count(Share.share_id).label('share_count')).group_by(Share.share_postid).subquery()
            
            """query post without daily rank"""
            page = request.args.get('page', 1, type=int)
            pstn = db.session.query(Posting).outerjoin(subq_likes, Posting.post_id==subq_likes.c.like_postid).outerjoin(subq_comments, Posting.post_id==subq_comments.c.com_postid).outerjoin(subq_shares, Posting.post_id==subq_shares.c.share_postid).filter(Posting.post_id==Image.image_postid).order_by(desc(subq_likes.c.like_count), desc(subq_comments.c.com_count), desc(subq_shares.c.share_count), desc(Posting.post_date)).paginate(page=page, per_page=rows_page)
            lk=Like.query.filter(Like.like_postid==Posting.post_id).all()
            appt=Bookappointment.query.order_by(desc(Bookappointment.ba_id)).paginate(page=page, per_page=rows_page)
            pymt=Payment.query.order_by(desc(Payment.payment_id)).paginate(page=page, per_page=rows_page)
            sublist = Subscription.query.order_by(desc(Subscription.sub_date)).paginate(page=page, per_page=rows_per_page)
            srepo = Report.query.order_by(desc(Report.report_id)).paginate(page=page, per_page=rows_per_page)
            return render_template('admin/admindashboard.html', admin=admin, spadmin=spadmin, srepo=srepo, spa=spa, adm=adm, prof=prof, pstn=pstn, lk=lk, appt=appt, pymt=pymt, sublist=sublist)
        
        elif spadmin:
            prof=Superadmin.query.filter(Superadmin.spadmin_id==spa.spadmin_id).first()

            """the main query for the production"""
            subq_likes = db.session.query(Like.like_postid, func.count(Like.like_id).label('like_count')).group_by(Like.like_postid).subquery()
            subq_comments = db.session.query(Comment.com_postid, func.count(Comment.com_id).label('com_count')).group_by(Comment.com_postid).subquery()
            subq_shares = db.session.query(Share.share_postid, func.count(Share.share_id).label('share_count')).group_by(Share.share_postid).subquery()
            
            """query post without daily rank"""
            page = request.args.get('page', 1, type=int)            
            pstn = db.session.query(Posting).outerjoin(subq_likes, Posting.post_id==subq_likes.c.like_postid).outerjoin(subq_comments, Posting.post_id==subq_comments.c.com_postid).outerjoin(subq_shares, Posting.post_id==subq_shares.c.share_postid).filter(Posting.post_id==Image.image_postid).order_by(desc(subq_likes.c.like_count), desc(subq_comments.c.com_count), desc(subq_shares.c.share_count), desc(Posting.post_date)).paginate(page=page, per_page=rows_page)
            appt=Bookappointment.query.order_by(desc(Bookappointment.ba_id)).paginate(page=page, per_page=rows_page)
            pymt=Payment.query.order_by(desc(Payment.payment_id)).paginate(page=page, per_page=rows_page)
            lk=Like.query.filter(Like.like_postid==Posting.post_id).all()
            sublist = Subscription.query.order_by(desc(Subscription.sub_date)).paginate(page=page, per_page=rows_per_page)
            srepo = Report.query.order_by(desc(Report.report_id)).paginate(page=page, per_page=rows_per_page)
            return render_template('admin/admindashboard.html', admin=admin, spadmin=spadmin, srepo=srepo, spa=spa, adm=adm, pstn=pstn, lk=lk, appt=appt, pymt=pymt, sublist=sublist, prof=prof)
    
    if request.method == 'POST':
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        email=request.form.get('email')
        phone=request.form.get('phone')
        address= request.form.get('address')
        if fname != "" or lname != "" or email != "" or phone != "" or address != "":
            if admin:                
                upd=Admin.query.get(admin)
                upd.cust_fname=fname
                upd.cust_lname=lname
                upd.cust_phone=phone
                upd.cust_email=email
                upd.cust_address=address
                db.session.commit()
                flash('updated successfully', 'success')
                return redirect('/admin/dashboard/')
            elif spadmin:                
                upd=Admin.query.get(spadmin)
                upd.cust_fname=fname
                upd.cust_lname=lname
                upd.cust_phone=phone
                upd.cust_email=email
                upd.cust_address=address
                db.session.commit()
                flash('updated successfully', 'success')
                return redirect('/admin/dashboard/')
        else:
            flash('one or more filed is empty', 'warning')
            return redirect('/admin/dashboard/')
        
        

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
        postid = request.form.get('postid')
        comid = request.form.get('comid')
        if postid =="":
            flash('file error')
            return redirect(f'/adminpost/{postid}/')
        elif comid =="":
            flash('file error')
            return redirect(f'/adminpost/{postid}/')
        else:
            if postid:
                if postid !="":
                    posi = Posting.query.filter_by(post_id=postid).first()
                    posi.post_suspend='suspended'
                    db.session.commit()
                    msg='success'
                    return jsonify(msg)
            if comid:
                if comid !="":
                    posi = Comment.query.filter_by(com_id=comid).first()
                    posi.com_suspend='suspended'
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
        postid = request.form.get('postid')
        comid = request.form.get('comid')
        if postid =="":
            flash('file error')
            return redirect(f'/adminpost/{postid}/')
        elif comid =="":
            flash('file error')
            return redirect(f'/adminpost/{postid}/')
        else:
            if postid:
                if postid !="":
                    posi = Posting.query.filter(Posting.post_id==postid).first()
                    posi.post_delete='deleted'
                    db.session.commit()
                    msg='successfully deleted'
                    return jsonify(msg)
                
            if comid:
                if comid !="":
                    posi = Comment.query.filter(Comment.com_id==comid).first()
                    posi.com_delete='deleted'
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
        if admin:
            page = request.args.get('page', 1, type=int)
            design=Designer.query.paginate(page=page, per_page=rows_page)
            design=Subscription.query.filter(Subscription.sub_status=='active').paginate(page=page, per_page=rows_page)
            return render_template('admin/admindesigners.html', design=design, spa=spa, adm=adm)
        elif spadmin:
            page = request.args.get('page', 1, type=int)
            design=Designer.query.paginate(page=page, per_page=rows_page)
            design=Subscription.query.filter(Subscription.sub_status=='active').paginate(page=page, per_page=rows_page)
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
        if admin:
            page = request.args.get('page', 1, type=int)
            # design=Designer.query.paginate(page=page, per_page=rows_page)
            design=Customer.query.paginate(page=page, per_page=rows_page)
            return render_template('admin/admin_allcustomers.html', design=design, spa=spa, adm=adm)
        elif spadmin:
            page = request.args.get('page', 1, type=int)
            # design=Designer.query.paginate(page=page, per_page=rows_page)
            design=Customer.query.paginate(page=page, per_page=rows_page)
            return render_template('admin/admin_allcustomers.html', design=design, spa=spa, adm=adm)
    

"""Designers Details """
@app.route('/designers/<id>/', methods=['GET', 'POST'])
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
@app.route('/customers/<id>/', methods=['GET', 'POST'])
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
            return redirect('/adminhome')
        elif spadmin:
            session.pop('superadmin', None)
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

@app.route('/deactivat/', methods=['GET', 'POST'])
def deactivat():
    if request.method == "POST":
        desi=request.form.get('desi_id')
        cust=request.form.get('cust_id')
        if desi:
            if desi !="":
                dess=Designer.query.filter_by(desi_id=desi).first()
                dess.desi_access='deactived'
                db.session.commit()
                message='Deactivated'
                return jsonify(message)
        elif cust:
            if cust !="":
                cust=Customer.query.filter_by(cust_id=cust).first()
                cust.cust_access='deactived'
                db.session.commit()
                message='Deactivated'
                return jsonify(message)

@app.route('/activat/', methods=['GET', 'POST'])
def activat():
    if request.method == "POST":
        desi=request.form.get('desi_id')
        cust=request.form.get('cust_id')
        if desi:
            if desi !="":
                dess=Designer.query.filter_by(desi_id=desi).first()
                dess.desi_access='actived'
                db.session.commit()
                message='Activated'
                return jsonify(message)
        elif cust:
            if cust !="":
                cust=Customer.query.filter_by(cust_id=cust).first()
                cust.cust_access='actived'
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
