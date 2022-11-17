import re, os, math, random, json, requests
from datetime import datetime, date, timedelta
from sqlalchemy import desc
from flask import render_template, request, redirect, flash, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_share import Share

from styleitapp import app, db
from styleitapp.models import Designer, State, Customer, Posting, Image, Comment, Like, Share, Bookappointment, Subscription, Payment
from styleitapp.forms import CustomerLoginForm, DesignerLoginForm
from styleitapp import Message, mail
from styleitapp.token import generate_confirmation_token, confirm_token
from styleitapp.email import send_email

rows_per_page = 12
rows_page = 20

"""homepage"""
@app.route('/')
def home():
    desiloggedin = session.get('designer')
    loggedin = session.get('customer')
    des=Designer.query.get(desiloggedin)
    cus=Customer.query.get(loggedin)
    
    if desiloggedin:
        return redirect('/designer/profile/')
    elif loggedin:
        return redirect('/customer/profile/')
    else:
        return render_template('user/index.html', cus=cus, des=des)

"""login"""
@app.route('/login/')
def login():
    loggedin = session.get('customer')
    desiloggedin = session.get('designer')
    des=Designer.query.get(desiloggedin)
    cus=Customer.query.get(loggedin)
    return render_template('user/login.html', cus=cus, des=des)

""" loading local govt area using ajax"""
@app.route('/load/lga/', methods=['POST'])
def lgacheck():
    state=request.form.get('stateid')
    # querying lga table
    lg=db.session.execute(f"SELECT * FROM lga WHERE lga_stateid={state}")
    results = lg.fetchmany(20)
    # building html tags for lga
    select_html = "<select>"
    for x,y,z in results:
        select_html = select_html + f"<option value='{x}'>{y}</option>"
    select_html = select_html + "</select>"
    return select_html

"""Trending section"""
@app.route('/trending/', methods=['GET', 'POST'])
def trending():
    desiloggedin = session.get('designer')
    loggedin = session.get('customer')
    if desiloggedin==None and loggedin== None:
        return redirect('/')

    if request.method == "GET":
        cus=Customer.query.get(loggedin)
        des=Designer.query.get(desiloggedin)        
        pstn=db.session.query(Posting).filter(Posting.post_id==Image.image_postid).order_by(desc(Posting.post_date)).limit(1000).all()
        lk=Like.query.filter(Like.like_postid==Posting.post_id).all()
        return render_template('user/trending.html', pstn=pstn, loggedin=loggedin, desiloggedin=desiloggedin, des=des, cus=cus, lk=lk)


""" post detail session """
@app.route('/post/<id>/')
def post(id):
    desiloggedin = session.get('designer')
    loggedin = session.get('customer')
    if desiloggedin==None and loggedin== None:
        return redirect('/')

    if request.method == 'GET':
        des=Designer.query.get(desiloggedin)
        cus = Customer.query.get(loggedin)
        pstn=db.session.query(Posting).filter(Posting.post_id==Image.image_postid, Posting.post_id==id).first()
        compost = Posting.query.filter_by(post_id=id).first_or_404()
        comnt=db.session.query(Comment).filter(Comment.com_postid==compost.post_id).order_by(Comment.path.asc()).all()
        share = db.session.query(Share).filter(Share.share_postid==compost.post_id).all()
        lk=Like.query.filter(Like.like_postid==Posting.post_id).all()
        for i in lk:
            print(i)
        return render_template('user/post.html', loggedin=loggedin, desiloggedin=desiloggedin, des=des,cus=cus,comnt=comnt, pstn=pstn, share=share, i=i)


"""All Designers """
@app.route('/alldesigners/', methods=['GET', 'POST'])
def designers():
    desiloggedin = session.get('designer')
    loggedin = session.get('customer')
    if desiloggedin==None and loggedin== None:
        return redirect('/')
        
    if request.method == 'GET':   
        des=Designer.query.get(desiloggedin)
        cus=Customer.query.get(loggedin)
        page = request.args.get('page', 1, type=int)
        design=Designer.query.paginate(page=page, per_page=rows_page)
        design=Subscription.query.filter(Subscription.sub_status=='active').paginate(page=page, per_page=rows_page)        
        return render_template('designer/alldesigners.html', design=design, des=des, cus=cus)

"""Designers Details """
@app.route('/designer/<id>/', methods=['GET', 'POST'])
def desi_detail(id):
    desiloggedin = session.get('designer')
    loggedin = session.get('customer')
    if desiloggedin==None and loggedin== None:
        return redirect('/')
        
    if request.method == 'GET':   
        des=Designer.query.get(desiloggedin)
        cus=Customer.query.get(loggedin)
        design=Designer.query.filter(Designer.desi_id==id).first()
        return render_template('designer/designerdetail.html', design=design, des=des, cus=cus)

"""Comment session"""
@app.route('/comment/<int:postid>/', methods=['GET', 'POST'])
def comment(postid):
    desiloggedin = session.get('designer')
    loggedin = session.get('customer')
    if desiloggedin==None and loggedin== None:
        return redirect('/')
    
    if request.method == 'GET':
        return redirect('/trending/')

    if request.method == 'POST':
        if desiloggedin:
            des=Designer.query.get(desiloggedin)
            com=request.form.get('comment')
            m=Comment(com_body=com, com_postid=postid, com_desiid=des.desi_id)
            m.save()
            return redirect(f'/post/{postid}/')
        elif loggedin:
            cus = Customer.query.get(loggedin)
            com=request.form.get('comment')
            k=Comment(com_body=com, com_postid=postid, com_custid=cus.cust_id)
            k.save()
            return redirect(f'/post/{postid}/')

"""Reply Session """
@app.route('/reply/<int:postid>/<int:commentid>/', methods=['POST', 'GET'])
def reply(postid, commentid):
    desiloggedin = session.get('designer')
    loggedin = session.get('customer')
    if desiloggedin==None and loggedin== None:
        return redirect('/')
    
    if request.method == 'GET':
        return redirect('/trending/')

    if request.method == 'POST':
        if desiloggedin:
            des=Designer.query.get(desiloggedin)
            repl=request.form.get('comrep')
            m=Comment(com_body=repl, com_postid=postid, com_desiid=des.desi_id, parent_id=commentid)
            m.save()
            return redirect(f'/post/{postid}/')

        elif loggedin:
            cus = Customer.query.get(loggedin)
            repl=request.form.get('comrep')
            k=Comment(com_body=repl, com_postid=postid, com_custid=cus.cust_id, parent_id=commentid)
            k.save()
            return redirect(f'/post/{postid}/')

@app.route('/like/<int:post_id>/', methods=['GET'])
def like(post_id):
    desiloggedin = session.get('designer')
    loggedin = session.get('customer')
    post = Posting.query.filter_by(post_id=post_id).first()
    if desiloggedin:
        liking = Like.query.filter_by(like_desiid=desiloggedin, like_postid=post_id).first()
        if not post:
            flash('Post does not exit', category='error')
        elif liking:
            db.session.delete(liking)
            db.session.commit()
        else:
            liking=Like(like_desiid=desiloggedin, like_postid=post_id)
            db.session.add(liking)
            db.session.commit()
        return redirect(f'/post/{post_id}/')
        
    elif loggedin:
        liking = Like.query.filter_by(like_custid=loggedin, like_postid=post_id).first()
        if not post:
            flash('Post does not exit', category='error')
        elif liking:
            db.session.delete(liking)
            db.session.commit()
        else:
            liking=Like(like_custid=loggedin, like_postid=post_id)
            db.session.add(liking)
            db.session.commit()
        return redirect(f'/post/{post_id}/')

"""Share buttons"""
@app.route('/share/', methods=['GET','POST'])
def share():
    desiloggedin = session.get('designer')
    loggedin = session.get('customer')
    if desiloggedin:
        name = request.form.get('name')
        postid = request.form.get('sharepost')
        user = request.form.get('user')
        if name !="" and postid !="" and user !="":
            sh=Share(share_webname=name, share_postid=postid, share_desiid=user)
            db.session.add(sh)
            db.session.commit()
            # return redirect(f'/post/{postid}')
            return ('', 204)
    elif loggedin:
        name = request.form.get('name')
        postid = request.form.get('sharepost')
        user = request.form.get('user')
        if name !="" and postid !="" and user !="":
            sh=Share(share_webname=name, share_postid=postid, share_custid=user)
            db.session.add(sh)
            db.session.commit()
            # return redirect(f'/post/{postid}')
            return ('', 204)

"""token confirmation"""
@app.route('/confirm/<token>/')
def confirm_email(token):
    loggedin = session.get('customer')
    desiloggedin = session.get('designer')
    
    if loggedin:
        try:
            email= confirm_token(token)
        except:
            flash('the confirmation link is invalid or has expired', 'danger')
        cus = Customer.query.filter_by(cust_email=email).first_or_404()
        if cus.cust_status=='actived':
            flash('Account already confirmed. Please login.', 'success')
        else:
            cus.cust_status = 'actived'
            cus.cust_activationdate = datetime.now()
            db.session.commit()
            flash('You have confirmed your account', 'success')
            return redirect('/user/customer/login/')
    
    elif desiloggedin:
        try:
            email= confirm_token(token)
        except:
            flash('the confirmation link is invalid or has expired', 'danger')
        des = Designer.query.filter_by(desi_email=email).first_or_404()
        if des.desi_status=='actived':
            flash('Account already confirmed. Please login.', 'success')
        else:
            des.desi_status = 'actived'
            des.desi_activationdate = datetime.now()
            db.session.commit()
            flash('You have confirmed your account', 'success')
            return redirect('/user/designer/login/')
    return redirect('main.home')


""" unconfirmed token"""
@app.route('/unconfirmed')
def unconfirmed():
    loggedin = session.get('customer')
    desiloggedin = session.get('designer')
    des=Designer.query.get(desiloggedin)
    cus=Customer.query.get(loggedin)
    if loggedin:
        cusi = Customer.query.filter_by(cust_id=loggedin).first_or_404()
        if cusi.cust_status=='actived':
            return redirect('/customer/profile/')
    elif desiloggedin:
        desi = Designer.query.filter_by(desi_id=desiloggedin).first_or_404()
        if desi.desi_status=='actived':
            return redirect('/designer/profile/')
    flash('Confirm your account !', 'warning')
    return render_template('user/unconfirmed.html', desiloggedin=desiloggedin, loggedin=loggedin, des=des, cus=cus)   


"""Resend activation"""
@app.route('/resend/activation')
def resent_confirmation():
    loggedin = session.get('customer')
    desiloggedin = session.get('designer')
    des=Designer.query.get(desiloggedin)
    cus=Customer.query.get(loggedin)
    if loggedin:
        cus = Customer.query.filter_by(cust_id=loggedin).first_or_404()
        token = generate_confirmation_token(cus.cust_email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('user/activate.html', confirm_url=confirm_url, cus=cus)
        subject = "Please confirm your email"
        send_email(cus.cust_email, subject, html)
        flash('A new confirmation mail has been sent.', 'success')
        return redirect(url_for('unconfirmed'))
    elif desiloggedin:
        des = Designer.query.filter_by(desi_id=desiloggedin).first_or_404()
        token = generate_confirmation_token(des.desi_email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('user/activate.html', confirm_url=confirm_url, des=des)
        subject = "Please confirm your email"
        send_email(des.desi_email, subject, html)
        flash('A new confirmation mail has been sent.', 'success')
        return redirect(url_for('unconfirmed')) 
    return redirect('/unconfirmed')



# Customers sections
"""Custormer Signup"""
@app.route('/user/customer/signup/', methods=['GET', 'POST'])
def customerSignup():
    loggedin = session.get('customer')
    cus=Customer.query.get(loggedin)
    state=State.query.all()
    if loggedin:
        return redirect('/customer/profile/')

    if request.method == 'GET':
        return render_template('user/customersignup.html', state=state, cus=cus)

    if request.method == 'POST':
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        username=request.form.get('username')
        email=request.form.get('email')
        phone=request.form.get('phone')
        pwd=request.form.get('pwd')
        cpwd=request.form.get('cpwd')
        address= request.form.get('address')
        state=request.form.get('state')
        lga=request.form.get('lga')
        gender=request.form.get('gender')
        pic=request.files.get('pic')
        original_name=pic.filename


        if fname=="" or lname=="" or username=="" or email=="" or phone=="" or pwd=="" or cpwd=="" or address=="" or state=="" or lga=="" or gender=="":
            flash('One or more field is empty', 'danger')
            return redirect('/user/customer/signup/')
    
        # checking length of password
        elif len(pwd) < 8:
            flash('Password should be atleast 8 character long', 'warning')
            return redirect('/user/customer/signup/')
        # compairing password match
        elif pwd !=cpwd:
            flash('Password match error', 'danger')
            return redirect('/user/customer/signup/')
        else:
            # spliting to check email extension
            mail = email.split('@')
            if mail[1] not in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
                flash('kindly provide a valid email', 'warning')
                return redirect('/user/customer/signup/')
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
                        pic.save(f'styleitapp/static/images/profile/customer/{saveas}')
                        # committing to Customer table
                        k=Customer(cust_fname=fname, cust_username=username, cust_lname=lname, cust_gender=gender, cust_phone=phone, cust_email=eemail, cust_pass=formated, cust_address=address, cust_pic=saveas,cust_stateid=state, cust_lgaid=lga)
                        db.session.add(k)
                        db.session.commit()

                        token = generate_confirmation_token(k.cust_email)
                        confirm_url = url_for('confirm_email', token=token, _external=True)
                        html = render_template('user/activate.html', confirm_url=confirm_url)
                        subject = "Please confirm your email"
                        send_email(k.cust_email, subject, html)
                        flash('Profile setup completed. A confirmation mail has been sent via email', 'success')
                        return redirect(url_for('customerLogin'))
                    return redirect('/user/customer/signup/')



"""Custormer Login"""
@app.route('/user/customer/login/', methods=['GET', 'POST'])
def customerLogin():
    loggedin = session.get('customer')       
    cus=Customer.query.get(loggedin)
    login = CustomerLoginForm()
    if loggedin:
        return redirect('/customer/profile/')
    # rendering login template
    if request.method == 'GET':
        return render_template('user/customerlogin.html', login=login, cus=cus)
        
    if request.method == 'POST':
        # getting form data
        email=request.form.get('email')
        pwd = request.form.get('pwd')
        # validating form data field
        if email=="" or pwd=="":
            flash('Invalid Credentials', 'danger')
            return redirect('/user/customer/login/')
        if email !="" or pwd !="":
            # quering Customer by filtering with email
            user=db.session.query(Customer).filter(Customer.cust_email==email).first()
            formated_pwd=user.cust_pass
            # checking password hash
            checking = check_password_hash(formated_pwd, pwd)
            if checking:
                session['customer']=user.cust_id
                return redirect('/customer/profile/')
            else:
                flash('kindly supply a valid email address and password', 'warning')
                return render_template('user/customerlogin.html', login=login, user=user)


"""Customer Forgotten Password"""
@app.route('/user/customer/forgottenpassword/', methods=['POST', 'GET'])
def customerforgottenpass():
    loggedin = session.get('customer')
    if loggedin:
        return redirect('/customer/profile/')
    if request.method == "GET":
        return render_template('user/forgottenpassword.html')
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        pwd=request.form.get('pwd')
        cpwd=request.form.get('cpwd')
       
        #validating fileds
        if username =="" or email =="" or pwd =="" or cpwd =="":
            flash('One or more field is empty', 'warning')
            return render_template('user/forgottenpassword.html')
        elif pwd != cpwd:
            flash('invalid credential supplied', 'danger')
            return redirect('/user/customer/forgottenpassword/')
        else:
            formated = generate_password_hash(pwd)
            cust=Customer.query.filter(Customer.cust_email==email).first()
            if cust.cust_username == username:
                cust.cust_pass=formated
                db.session.commit()
                flash('password updated successfully', 'success')
                return redirect('/user/customer/login/')
            else:
                flash('invalid busiess name or email address', 'danger')
                return redirect('/user/customer/forgottenpassword/')

                
"""Customer Profile"""
@app.route('/customer/profile/', methods=['GET', 'POST'])
def customerProfile():
    loggedin = session.get('customer')
    if loggedin==None:
        return redirect('/')

    if request.method == 'GET':
        state=State.query.all()
        cus=Customer.query.get(loggedin)
        if cus.cust_status == 'deactived':
            flash('Please confirm your account', 'warning')
            return redirect(url_for('unconfirmed'))
        else:
            page=request.args.get('page', 1, type=int)
            mylike = Like.query.filter(Like.like_custid==cus.cust_id).paginate(page=page, per_page=rows_per_page)
            getbk=Bookappointment.query.filter(Bookappointment.ba_custid==loggedin).order_by(desc(Bookappointment.ba_date)).paginate(page=page, per_page=rows_per_page)
            return render_template('user/customerprofile.html', loggedin=loggedin, cus=cus, state=state, mylike=mylike, getbk=getbk)
    
    if request.method == 'POST':
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        email=request.form.get('email')
        phone=request.form.get('phone')
        address= request.form.get('address')
        if fname != "" or lname != "" or email != "" or phone != "" or address != "":
            upd=Customer.query.get(loggedin)
            upd.cust_fname=fname
            upd.cust_lname=lname
            upd.cust_phone=phone
            upd.cust_email=email
            upd.cust_address=address
            db.session.commit()
            flash('updated successfully', 'success')
            return redirect('/customer/profile/')
        else:
            flash('one or more filed is empty', 'warning')
            return redirect('/customer/profile/')

"""customer logout session"""
@app.route('/customer/logout/')
def customerlogout():
    loggedin = session.get('customer')
    if loggedin==None:
        return redirect('/')
        
    if request.method == 'GET':
        session.pop('customer', None)
        return redirect('/')


"""book appointment"""
@app.route('/bookappointment/', methods=['GET', 'POST'])
def book_appointment():
    loggedin = session.get('customer')
    if loggedin==None:
        return redirect('/')

    if request.method == 'GET':
        cus=Customer.query.get(loggedin)
        apnt = Subscription.query.filter(Subscription.sub_status=='active').all()
        return render_template('user/bookappointment.html', apnt=apnt, cus=cus)

    if request.method == 'POST':
        getfor = request.form
        dsignername = getfor.get('dsignername')
        bdate = getfor.get('bdate')
        btime = getfor.get('btime')
        cdate = getfor.get('cdate')
        ctime = getfor.get('ctime')
        if dsignername =="" or bdate =="" or btime =="" or cdate =="" or ctime=="":
            flash('Kindly fill each fields')
            return redirect(request.url)
        else:
            bookapp=Bookappointment(ba_desiid=dsignername, ba_custid=loggedin, ba_bookingDate=bdate, ba_bookingTime=btime, ba_collectionDate=cdate, ba_collectionTime=ctime)
            db.session.add(bookapp)
            db.session.commit()
        return redirect('/customer/profile/')

# customer section ends

# designer section begins
"""Designer Signup"""
@app.route('/user/designer/signup/', methods=['GET', 'POST'])
def designerSignup():
    desiloggedin = session.get('designer')
    des=Designer.query.get(desiloggedin)
    state=State.query.all()
    if desiloggedin:
        return redirect('/designer/profile/')

    if request.method == 'GET':
        return render_template('designer/designersignup.html', state=state, des=des)
    
    if request.method == 'POST':
        fname=request.form.get('fname')
        busname=request.form.get('busname')
        lname=request.form.get('lname')
        email=request.form.get('email')
        phone=request.form.get('phone')
        pwd=request.form.get('pwd')
        cpwd=request.form.get('cpwd')
        address= request.form.get('address')
        state=request.form.get('state')
        lga=request.form.get('lga')
        gender=request.form.get('gender')
        pic=request.files.get('pic')
        original_name=pic.filename

        # validating form fields
        if fname=="" or lname=="" or busname=="" or email=="" or phone=="" or pwd=="" or cpwd=="" or address=="" or state=="" or lga=="" or gender=="":
            flash('One or more field is empty', 'warning')
            return redirect('/user/designer/signup/')
        # checking length of password
        elif len(pwd) < 8:
            flash('Password should be atleast 8 character long', 'warning')
            return redirect('/user/designer/signup/')
        # compairing password match
        elif pwd !=cpwd:
            flash('Password match error', 'danger')
            return redirect('/user/designer/signup/')
        else:
            # spliting to check email extension
            mail = email.split('@')
            if mail[1] not in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
                flash('kindly provide a valid email', 'warning')
                return redirect('/user/designer/signup/')
            else:
                eemail = mail[0] + '@' + mail[1]
                # print(eemail)
                # hashing password
                formated = generate_password_hash(pwd)
                # checking image field if empty
                if original_name != "":
                    # spliting image path
                    extension = os.path.splitext(original_name)
                    if extension[1].lower() in ['.jpg', '.gif', '.png']:
                        fn=math.ceil(random.random()*10000000000)
                        saveas = str(fn) + extension[1]
                        pic.save(f'styleitapp/static/images/profile/designer/{saveas}')
                        # committing to Customer table
                        dk=Designer(desi_fname=fname, desi_businessName=busname, desi_lname=lname, desi_gender=gender, desi_phone=phone, desi_email=eemail, desi_pass=formated, desi_address=address, desi_pic=saveas, desi_stateid=state, desi_lgaid=lga)
                        db.session.add(dk)
                        db.session.commit()

                        token = generate_confirmation_token(dk.desi_email)
                        confirm_url = url_for('confirm_email', token=token, _external=True)
                        html = render_template('user/activate.html', confirm_url=confirm_url)
                        subject = "Please confirm your email"
                        send_email(dk.desi_email, subject, html)
                        flash('Profile setup completed. A confirmation mail has been sent via email', 'success')
                        return redirect(url_for('unconfirmed'))
                    return redirect('/user/designer/signup/')



""" checking sub status for automatic deactivation """
@app.before_request
def before_request_func():
    desiloggedin = session.get('designer')
    des=Designer.query.get(desiloggedin)
    if desiloggedin:
        subt=db.session.query(Subscription).filter(Subscription.sub_desiid==des.desi_id).first()
        today = date.today()
        # print(subt)
        # print(today)
        today = '2022-12-01'
        if subt != None:
            if subt.sub_enddate < str(today):
                subt.sub_status='deactive'
                db.session.commit()
        else:
            pass


"""Designer Login"""
@app.route('/user/designer/login/', methods=['GET', 'POST'])
def designerLogin():
    logins = DesignerLoginForm()
    desiloggedin = session.get('designer')
    des=Designer.query.get(desiloggedin)
    if desiloggedin:
        return redirect('/designer/profile/')

    # rendering login template
    if request.method == 'GET':
        return render_template('designer/designerlogin.html', logins=logins, des=des)
    
    if request.method == 'POST':
        # getting form data
        email=request.form.get('email')
        pwd = request.form.get('pwd')
        # validating form data field
        if email=="" or pwd=="":
            flash('Invalid Credentials', 'danger')
            return redirect('/user/designer/login/')
        if email !="" or pwd !="":
            # quering Customer by filtering with email
            designer=db.session.query(Designer).filter(Designer.desi_email==email).first()
            formated_pwd=designer.desi_pass
            # checking password hash
            checking = check_password_hash(formated_pwd, pwd)
            if checking:
                session['designer']=designer.desi_id
                return redirect('/designer/profile/')
            else:
                flash('kindly supply a valid email address and password', 'warning')
                return render_template('designer/designerlogin.html', logins=logins, designer=designer)


"""Designer Profile"""
@app.route('/designer/profile/', methods=['GET', 'POST'])
def designerProfile():
    desiloggedin = session.get('designer')
    if desiloggedin==None:
        return redirect('/')

    if request.method == 'GET':
        des=Designer.query.get(desiloggedin)
        state=State.query.all()
        if des.desi_status == 'deactived':
            flash('Please confirm your account', 'warning')
            return redirect(url_for('unconfirmed'))
        else:
            page = request.args.get('page', 1, type=int)
            pos=Posting.query.filter(Posting.post_desiid==des.desi_id).paginate(page=page, per_page=rows_per_page)
            getbk=Bookappointment.query.filter(Bookappointment.ba_desiid==desiloggedin).order_by(desc(Bookappointment.ba_date)).paginate(page=page, per_page=rows_per_page)
            subt=Subscription.query.filter(Subscription.sub_desiid==desiloggedin, Subscription.sub_status=='active').first()
            return render_template('designer/designerprofile.html', desiloggedin=desiloggedin, des=des, state=state, pos=pos, getbk=getbk, subt=subt)

    if request.method == 'POST':
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        email=request.form.get('email')
        phone=request.form.get('phone')
        address=request.form.get('address')

        if fname=="" or lname=="" or email=="" or phone=="" or address=="":
            desi=Designer.query.get(desiloggedin)
            desi.desi_fname=fname
            desi.desi_lname=lname
            desi.desi_email=email
            desi.desi_phone=phone
            desi.desi_address=address
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect('/designer/profile/')
        else:
            flash('One of more field is empty', 'warning')
            return redirect('/designer/profile/')

"""Designer Forgotten Password"""
@app.route('/user/designer/forgottenpassword/', methods=['POST', 'GET'])
def designerforgottenpass():
    desiloggedin = session.get('designer')
    if desiloggedin:
        return redirect('/designer/profile/')

    if request.method == "GET":
        return render_template('designer/forgottenpassword.html')
    if request.method == "POST":
        busname=request.form.get('businessname')
        email=request.form.get('email')
        pwd=request.form.get('pwd')
        cpwd=request.form.get('cpwd')

        if busname =="" or email =="" or pwd =="" or cpwd =="":
            flash('One or more field is empty', 'warning')
            return render_template('designer/forgottenpassword.html')
        elif pwd != cpwd:
            flash('invalid credential supplied', 'danger')
            return redirect('/user/designer/forgottenpassword/')
        else:
            formated = generate_password_hash(pwd)
            desi=Designer.query.filter(Designer.desi_email==email).first()
            if desi.desi_businessName == busname:
                desi.desi_pass=formated
                db.session.commit()
                flash('password updated successfully', 'success')
                return redirect('/user/designer/login/')
            else:
                flash('invalid busiess name or email address', 'danger')
                return redirect('/user/designer/forgottenpassword/')

"""designer logout session"""
@app.route('/designer/logout/')
def designerlogout():
    desiloggedin = session.get('designer')
    if desiloggedin==None:
        return redirect('/')

    if request.method == 'GET':
        session.pop('designer', None)
        return redirect('/')

"""Posting section"""
@app.route('/posting/', methods=['GET', 'POST'])
def posting():
    desiloggedin = session.get('designer')
    if desiloggedin==None:
        return redirect('/')

    if request.method == 'GET':
        pst=Posting.query.filter(Posting.post_id==desiloggedin).all()
        des=Designer.query.get(desiloggedin)
        return render_template('designer/post.html', des=des, pst=pst)

    if request.method == 'POST':
        des=Designer.query.get(desiloggedin)
        head=request.form.get('title')
        body=request.form.get('body')

        if head=='' or body=='':
            flash('Complete all fields', 'warning')
            return render_template('designer/post.html', des=des)
        else:
            if head !="" or body !="":
                # committing to Customer table
                pos=Posting(post_title=head, post_body=body, post_desiid=des.desi_id)
                db.session.add(pos)
                db.session.commit()      
                flash('Post saved successfully, proceed to add image', 'success')
                posimg = Posting.query.filter(Posting.post_title==head, Posting.post_desiid==des.desi_id).first()
                posimg2={posimg.post_id:{"head":posimg.post_title, "body":posimg.post_body, "desiid":posimg.post_desiid}}            
                session['postId']=posimg2
                return redirect('/image/')
                

"""image upload"""
@app.route('/image/', methods=['GET','POST'])
def image():
    desiloggedin = session.get('designer')
    if desiloggedin==None:
        return redirect('/')

    if request.method == 'GET':
        des=Designer.query.get(desiloggedin)
        return render_template('designer/addimage.html', des=des)

    if request.method == 'POST':
        imgname=request.form.get('name')
        imgs=request.files.getlist('img')
       
        if imgname=="":
            flash('fill all required fields', 'warning')
            return redirect('/posting/')
        else:
            postId = session.get('postId')
            for x,y in postId.items():
                    pass
            for img in imgs:
                original_name=img.filename
                if original_name != "":
                    # spliting image path
                    extension = os.path.splitext(original_name)
                    if extension[1].lower() in ['.jpg', '.gif', '.png']:
                        fn=math.ceil(random.random()*10000000000)
                        saveas = str(fn) + extension[1]
                        img.save(f'styleitapp/static/images/postpic/{saveas}')     
                        # committing to Customer table
                        
                        pos=Image(image_name=imgname, image_url=saveas,image_postid=x, Image_desiid=desiloggedin)
                        db.session.add(pos)
            db.session.commit()
            session.pop('postId', None)
            flash("Posted successfuly", 'success')
            return redirect('/designer/profile/')

"""Accept/decline appointment"""
@app.route('/appointment/status/<id>/', methods=['GET', 'POST'])
def appointment_status(id):
    desiloggedin = session.get('designer')
    if desiloggedin==None:
        return redirect('/')
    
    if request.method == 'GET':
        return redirect('/designer/profile/')
    
    if request.method == 'POST':
        apt=request.form
        aptaction = apt.get('action')
        if aptaction !="":
            if aptaction =="accept":
                apptm = Bookappointment.query.get(id)
                apptm.ba_status=aptaction
                db.session.commit()
                return redirect('/designer/profile/')
            elif aptaction =="decline":
                apptm = Bookappointment.query.get(id)
                apptm.ba_status=aptaction
                db.session.commit()
                return redirect('/designer/profile/')


"""subscription plans"""
@app.route('/designer/subplan/', methods=['GET'])
def subplan():
    desiloggedin = session.get('designer')
    if desiloggedin==None:
        return redirect('/')
    
    if request.method =='GET':
        des=Designer.query.get(desiloggedin)
        page=request.args.get('page', 1, type=int)
        sublist = Subscription.query.filter_by(sub_desiid=desiloggedin).order_by(desc(Subscription.sub_date)).paginate(page=page, per_page=rows_per_page)
        return render_template('designer/subscribeplans.html', des=des, sublist=sublist)


"""subscription"""
@app.route('/designer/sub/', methods=['GET', 'POST'])
def subscribe():
    desiloggedin = session.get('designer')
    if desiloggedin==None:
        return redirect('/')
    
    if request.method =='GET':
        des=Designer.query.get(desiloggedin)
        return render_template('designer/subscribe.html', des=des)
    
    if request.method == 'POST':
        getform = request.form
        plan = getform.get('plan')
        if plan =="":
            return redirect('/designer/sub/')
        else:
            planb = plan
            refno = int(random.random()*10000000) 
            session['refno'] = refno
            sub = Subscription(sub_plan=planb, sub_ref=refno, sub_desiid=desiloggedin, sub_startdate=0, sub_enddate=0)
            db.session.add(sub)
            db.session.commit()
            pay = Payment(payment_transNo=refno, payment_amount=planb, payment_desiid=desiloggedin, payment_subid=sub.sub_id)
            db.session.add(pay)
            db.session.commit()
            return redirect('/payment/')


""" payment """
@app.route('/payment/', methods=['GET', 'POST'])
def payment():
    desiloggedin = session.get('designer')
    if desiloggedin==None:
        return redirect('/')

    des=Designer.query.get(desiloggedin)
    refno = session.get('refno')
    pymt=Payment.query.filter_by(payment_transNo=refno).first()
    if request.method =='GET':
        return render_template('designer/confirmpayment.html', des=des, pymt=pymt)
    else:
        data = {"email":des.desi_email,"amount":pymt.payment_amount*100, "reference":pymt.payment_transNo}

        headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_9ebd9bc239bcde7a0f43e2eab48b18ef1910356f"}

        response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))

        rspjson = json.loads(response.text) 
        if rspjson.get('status') == True:
            authurl = rspjson['data']['authorization_url']
            return redirect(authurl)
        else:
            return "Please try again"


@app.route("/user/payverify")
def paystack():
    reference = request.args.get('reference')
    refno = session.get('refno')
    #update our database 
    headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_9ebd9bc239bcde7a0f43e2eab48b18ef1910356f"}

    response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    rsp =response.json()#in json format
    if rsp['data']['status'] =='success':
        amt = rsp['data']['amount']
        ipaddress = rsp['data']['ip_address']
        p = Payment.query.filter(Payment.payment_transNo==refno).first()
        p.payment_status = 'paid'
        db.session.add(p)
        db.session.commit()
        return redirect('/activate/')  #update database and redirect them to the feedback page
    else:
        p = Payment.query.filter(Payment.payment_transNo==refno).first()
        p.payment_status = 'failed'
        db.session.add(p)
        db.session.commit()
        flash("Payment Failed", "danger")
        return redirect('/designer/profile/')

@app.route('/activate/', methods=['GET', 'POST'])
def activating():
    desiloggedin = session.get('designer')
    if desiloggedin==None:
        return redirect('/')

    if request.method == 'GET':
        des=Designer.query.get(desiloggedin)
        refno = session.get('refno')
        substat = Subscription.query.filter(Subscription.sub_ref==refno).first()
        # print(substat.sub_plan)
        if substat.sub_plan == '500':
            Dstart = date.today()
            Dend = Dstart + timedelta(days=29)
            # print(Dstart)
            # print(Dend)
            substat.sub_startdate=Dstart
            substat.sub_enddate=Dend
            substat.sub_status='active'
            substat.sub_paystatus='paid'
            db.session.commit()
            flash("Activation Successful", "success")
            return redirect('/designer/profile/')  #update database and redirect them to the feedback page
        elif substat.sub_plan == '1350':
            Dstart = date.today()
            Dend = Dstart + timedelta(days=89)
            # print(Dstart)
            # print(Dend)
            substat.sub_startdate=Dstart
            substat.sub_enddate=Dend
            substat.sub_status='active'
            substat.sub_paystatus='paid'
            db.session.commit()
            flash("Activation Successful", "success")
            return redirect('/designer/profile/')  #update database and redirect them to the feedback page
        elif substat.sub_plan == '2400':
            Dstart = date.today()
            Dend = Dstart + timedelta(days=179)
            # print(Dstart)
            # print(Dend)
            substat.sub_startdate=Dstart
            substat.sub_enddate=Dend
            substat.sub_status='active'
            substat.sub_paystatus='paid'
            db.session.commit()
            flash("Activation Successful", "success")
            return redirect('/designer/profile/')  #update database and redirect them to the feedback page
        elif substat.sub_plan == '4200':
            Dstart = date.today()
            Dend = Dstart + timedelta(days=364)
            # print(Dstart)
            # print(Dend)
            substat.sub_startdate=Dstart
            substat.sub_enddate=Dend
            substat.sub_status='active'
            substat.sub_paystatus='paid'
            db.session.commit()
            flash("Activation Successful", "success")
            return redirect('/designer/profile/')  #update database and redirect them to the feedback page
        else:
            flash("Activation Unsuccessful", "danger")
            return redirect('/trending')

"""Error 404 page"""
@app.errorhandler(404)
def page_not_found(error):
    desiloggedin = session.get('designer')
    loggedin = session.get('customer')
    if desiloggedin==None and loggedin== None:
        return redirect('/')
    else:
        des=Designer.query.get(desiloggedin)
        cus=Customer.query.get(loggedin)
        return render_template('user/error.html', des=des, cus=cus, error=error),404