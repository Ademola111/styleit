import re, os, math, random, json
from sqlalchemy import desc
from flask import render_template, request, redirect, flash, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_share import Share

from styleitapp import app, db
from styleitapp.models import Designer, State, Customer, Posting, Image, Comment, Like, Share, Bookappointment
from styleitapp.forms import CustomerLoginForm, DesignerLoginForm


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
        pstn=db.session.query(Posting).filter(Posting.post_id==Image.image_postid).order_by(desc(Posting.post_date)).all()
        return render_template('user/trending.html', pstn=pstn, loggedin=loggedin, desiloggedin=desiloggedin, des=des, cus=cus)


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
        design=Designer.query.all()
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
        # compairing password match
        elif pwd !=cpwd:
            flash('Password match error', 'danger')
            return redirect('/user/customer/signup/')
        else:
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
                    k=Customer(cust_fname=fname, cust_username=username, cust_lname=lname, cust_gender=gender, cust_phone=phone, cust_email=email, cust_pass=formated, cust_address=address, cust_pic=saveas,cust_stateid=state, cust_lgaid=lga)
                    db.session.add(k)
                    db.session.commit()
                    flash('Profile setup completed', 'success')
                    return redirect('/user/customer/login/')


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
        mylike = Like.query.filter(Like.like_postid==Like.like_custid, Like.like_date==Like.like_custid).all()
        getbk=Bookappointment.query.filter(Bookappointment.ba_custid==loggedin).order_by(desc(Bookappointment.ba_date)).limit(10).all()
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
        session.pop('customer')
        return redirect('/')


"""book appointment"""
@app.route('/bookappointment/', methods=['GET', 'POST'])
def book_appointment():
    loggedin = session.get('customer')
    if loggedin==None:
        return redirect('/')

    if request.method == 'GET':
        cus=Customer.query.get(loggedin)
        apnt = Designer.query.all()
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
        # compairing password match
        elif pwd !=cpwd:
            flash('Password match error', 'danger')
            return redirect('/user/designer/signup/')
        else:
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
                    dk=Designer(desi_fname=fname, desi_businessName=busname, desi_lname=lname, desi_gender=gender, desi_phone=phone, desi_email=email, desi_pass=formated, desi_address=address, desi_pic=saveas, desi_stateid=state, desi_lgaid=lga)
                    db.session.add(dk)
                    db.session.commit()
                    flash('Profile setup completed', 'success')
                    return redirect('/user/designer/login/')


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
        pos=Posting.query.filter(Posting.post_desiid==des.desi_id).all()
        state=State.query.all()
        getbk=Bookappointment.query.filter(Bookappointment.ba_desiid==desiloggedin).order_by(desc(Bookappointment.ba_date)).limit(10).all()
        return render_template('designer/designerprofile.html', desiloggedin=desiloggedin, des=des, state=state, pos=pos, getbk=getbk)

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
        session.pop('designer')
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
@app.route('/designer/subplan', methods=['GET', 'POST'])
def subplan():
    desiloggedin = session.get('designer')
    if desiloggedin==None:
        return redirect('/')
    
    if request.method =='GET':
        des=Designer.query.get(desiloggedin)
        return render_template('designer/subscribeplans.html', des=des)


"""subscription"""
@app.route('/designer/sub', methods=['GET', 'POST'])
def subscribe():
    desiloggedin = session.get('designer')
    if desiloggedin==None:
        return redirect('/')
    
    if request.method =='GET':
        des=Designer.query.get(desiloggedin)
        return render_template('designer/subscribe.html', des=des)

""" payment """
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    desiloggedin = session.get('designer')
    if desiloggedin==None:
        return redirect('/')
    
    if request.method =='GET':
        des=Designer.query.get(desiloggedin)
        return f"You've made a payment {des}"