import datetime, humanize
from styleitapp import db

class Posting(db.Model):
    post_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    post_title = db.Column(db.String(255), nullable=False)
    post_body = db.Column(db.Text(), nullable=True)
    post_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    post_suspend = db.Column(db.Enum('suspended', 'unsuspended'), server_default='unsuspended')
    post_delete = db.Column(db.Enum('deleted', 'not deleted'), server_default='not deleted')
    #foreignkey
    post_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    #relationship
    imagepostobj = db.relationship("Image", back_populates='postimageobj')
    designerobj = db.relationship("Designer", back_populates='designerpostobj')
    postcomobj = db.relationship('Comment', back_populates='compostobj')
    # likes = db.relationship('Like', backref='posting', lazy='dynamic')
    likes = db.relationship('Like', back_populates='posts')
    sharepostobj = db.relationship('Share', back_populates='postshareobj')
    postnotifyobj = db.relationship('Notification', back_populates='notifypostobj')
    
    # @property
    # def rank(self):
    #     return _get_rank_for_post_count(self.ranks.count)

class Image(db.Model):
    image_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    image_name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    #foreignkey
    image_postid = db.Column(db.Integer(), db.ForeignKey('posting.post_id'))
    Image_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    #relationship
    imagedesignerobj = db.relationship("Designer", back_populates='designerimageobj')
    postimageobj= db.relationship("Posting", back_populates='imagepostobj')
    

class Comment(db.Model):
    _N = 6
    com_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    com_body = db.Column(db.Text(), nullable=True)
    com_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    path = db.Column(db.Text, index=True)
    com_suspend = db.Column(db.Enum('suspended', 'unsuspended'), server_default='unsuspended')
    com_delete = db.Column(db.Enum('deleted', 'not deleted'), server_default='not deleted')
    #foreignkey
    com_postid = db.Column(db.Integer(), db.ForeignKey('posting.post_id'))
    com_custid = db.Column(db.Integer(), db.ForeignKey('customer.cust_id'))
    com_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    parent_id = db.Column(db.Integer(), db.ForeignKey('comment.com_id'))
    #relationship
    compostobj = db.relationship('Posting', back_populates='postcomobj')
    comcustobj = db.relationship('Customer', back_populates='custcomobj')
    comdesiobj = db.relationship('Designer', back_populates='desicomobj')
    comnotifyobj = db.relationship('Notification', back_populates='notifycomobj')
    
    
    replies = db.relationship(
        'Comment', backref=db.backref('parent', remote_side=[com_id]),
        lazy='dynamic')
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        prefix = self.parent.path + '.' if self.parent else ''
        self.path = prefix + '{:0{}d}'.format(self.com_id, self._N)
        db.session.commit()

    def level(self):
        return len(self.path)//self._N - 1


class Customer(db.Model):
    cust_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    cust_regdate = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    cust_fname = db.Column(db.String(255), nullable=False)
    cust_lname = db.Column(db.String(255), nullable=False)
    cust_username = db.Column(db.String(255), nullable=False)
    cust_gender = db.Column(db.Enum('male','female'), nullable=False)
    cust_phone = db.Column(db.String(225), nullable=False)
    cust_email = db.Column(db.String(255), nullable=False)
    cust_pass = db.Column(db.String(255), nullable=False)
    cust_address = db.Column(db.Text(), nullable=True)
    cust_pic = db.Column(db.String(255), nullable=True)
    cust_activationdate = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    cust_status = db.Column(db.Enum('actived', 'deactived'), server_default='deactived')
    cust_access = db.Column(db.Enum('actived', 'deactived'), server_default='actived')

    #foreignkey
    cust_stateid = db.Column(db.Integer(), db.ForeignKey('state.state_id'))
    cust_lgaid = db.Column(db.Integer(), db.ForeignKey('lga.lga_id'))
    #relationship
    stateobj = db.relationship('State', back_populates='statecustomerobj')
    lgaobj = db.relationship('Lga', back_populates='lgacustomerobj')
    custcomobj = db.relationship('Comment', back_populates='comcustobj')
    likecustobj = db.relationship('Like', back_populates='custlikesobj')
    sharecustobj = db.relationship('Share', back_populates='custshareobj')
    bacustobj = db.relationship('Bookappointment', back_populates='custbaobj')
    custnotifyobj = db.relationship('Notification', back_populates='notifycustobj')
    reportcustobj = db.relationship('Report', back_populates='custreportobj')
    ratcustobj = db.relationship('Rating', back_populates='custratobj')
    custjbobj=db.relationship('Job', back_populates='jbcustobj')
    tpaycustobj=db.relationship('Transaction_payment', back_populates='custtpayobj')
    followcustobj = db.relationship('Follow', back_populates='custfollowobj')
    logincustobj = db.relationship('Login', back_populates='custloginobj')
    
    def __init__(self, cust_id, cust_regdate, cust_fname, cust_lname,
                    cust_username, cust_gender, cust_phone, cust_email, cust_pass, cust_address, cust_pic, cust_activationdate, cust_status, cust_access, cust_stateid, cust_lgaid):
            self.cust_id = cust_id
            self.sdesi_regdate = cust_regdate
            self.cust_fname = cust_fname
            self.cust_lname = cust_lname
            self.cust_businessName = cust_username
            self.cust_gender = cust_gender 
            self.cust_phone = cust_phone
            self.cust_email = cust_email
            self.cust_pass = cust_pass
            self.cust_address = cust_address
            self.cust_pic = cust_pic
            self.cust_activationdate = cust_activationdate
            self.cust_status = cust_status
            self.cust_access = cust_access
            self.cust_stateid = cust_stateid
            self.cust_lgaid = cust_lgaid

class State(db.Model): 
    state_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    state_name = db.Column(db.String(255), nullable=False)
    #set up the relationship
    statecustomerobj = db.relationship('Customer', back_populates ='stateobj')
    statedesignerobj = db.relationship('Designer', back_populates ='stateobj2')
    statelgaobj = db.relationship('Lga', back_populates='lgastateobj')

class Lga(db.Model): 
    lga_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    lga_name = db.Column(db.String(255), nullable=False)
    #foreignkey
    lga_stateid = db.Column(db.Integer(), db.ForeignKey('state.state_id'))
    #set up the relationship
    lgacustomerobj = db.relationship('Customer', back_populates ='lgaobj')
    lgadesignerobj = db.relationship('Designer', back_populates ='lgaobj2')
    lgastateobj = db.relationship('State', back_populates ='statelgaobj')

class Designer(db.Model):
    desi_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    desi_regdate = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    desi_fname = db.Column(db.String(255), nullable=False)
    desi_lname = db.Column(db.String(255), nullable=False)
    desi_businessName = db.Column(db.String(255), nullable=False)
    desi_gender = db.Column(db.Enum('male','female'), nullable=False)
    desi_phone = db.Column(db.String(225), nullable=False)
    desi_email = db.Column(db.String(255), nullable=False)
    desi_pass = db.Column(db.String(255), nullable=False)
    desi_address = db.Column(db.Text(), nullable=True)
    desi_pic = db.Column(db.String(255), nullable=True)
    desi_activationdate = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    desi_status = db.Column(db.Enum('actived', 'deactived'), server_default='deactived')
    desi_access = db.Column(db.Enum('actived', 'deactived'), server_default='actived')
    
    #foreignkey
    desi_stateid = db.Column(db.Integer(), db.ForeignKey('state.state_id'))
    desi_lgaid = db.Column(db.Integer(), db.ForeignKey('lga.lga_id'))
    #relationship
    stateobj2 = db.relationship('State', back_populates='statedesignerobj')
    lgaobj2 = db.relationship('Lga', back_populates='lgadesignerobj')
    designerpostobj = db.relationship("Posting", back_populates='designerobj')
    designerimageobj = db.relationship("Image", back_populates='imagedesignerobj')
    desicomobj = db.relationship('Comment', back_populates='comdesiobj')
    desisubobj = db.relationship('Subscription', back_populates='subdesiobj')
    likedesiobj = db.relationship('Like', back_populates='desilikesobj')
    sharedesiobj = db.relationship('Share', back_populates='desishareobj')
    badesiobj = db.relationship('Bookappointment', back_populates='desibaobj')
    paymentdesiobj=db.relationship('Payment', back_populates='desipaymentobj')
    desinotifyobj = db.relationship('Notification', back_populates='notifydesiobj')
    reportdesiobj = db.relationship('Report', back_populates='desireportobj')
    ratdesiobj = db.relationship('Rating', back_populates='desiratobj')
    desijbobj=db.relationship('Job', back_populates='jbdesiobj')
    tpaydesiobj=db.relationship('Transaction_payment', back_populates='desitpayobj')
    bnkdesiobj = db.relationship('Bank', back_populates='desibnkobj')
    followdesiobj = db.relationship('Follow', back_populates='desifollowobj')
    logindesiobj = db.relationship('Login', back_populates='desiloginobj')
    
    def __init__(self, desi_id, desi_regdate, desi_fname, desi_lname,
                    desi_businessName, desi_gender, desi_phone, desi_email, desi_pass, desi_address, desi_pic, desi_activationdate, desi_status, desi_access, desi_stateid, desi_lgaid):
            self.desi_id = desi_id
            self.sdesi_regdate = desi_regdate
            self.desi_fname = desi_fname
            self.desi_lname = desi_lname
            self.desi_businessName = desi_businessName
            self.desi_gender = desi_gender 
            self.desi_phone = desi_phone
            self.desi_email = desi_email
            self.desi_pass = desi_pass
            self.desi_address = desi_address
            self.desi_pic = desi_pic
            self.desi_activationdate = desi_activationdate
            self.desi_status = desi_status
            self.desi_access = desi_access
            self.desi_stateid = desi_stateid
            self.desi_lgaid = desi_lgaid
            

class Subscription(db.Model):
    sub_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    sub_plan = db.Column(db.Enum('500','1350', '2400','4200'), nullable=False)
    sub_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    sub_startdate = db.Column(db.String(255), nullable=True)
    sub_enddate = db.Column(db.String(255), nullable=True)
    sub_ref = db.Column(db.Integer(), nullable=True)
    sub_status = db.Column(db.Enum('active', 'deactive'), server_default='deactive')
    sub_paystatus = db.Column(db.Enum('pending', 'paid', 'failed'), server_default='pending')
    #foreignkey
    sub_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    #relationship
    subdesiobj = db.relationship('Designer', back_populates='desisubobj')
    paysubobj=db.relationship('Payment', back_populates='subpaymentobj')
    subnotifyobj = db.relationship('Notification', back_populates='notifysubobj')
    
    def __init__(self, sub_id, sub_plan, sub_date, sub_startdate,
                    sub_enddate, sub_ref , sub_status, sub_paystatus, sub_desiid, subdesiobj, paysubobj):
            self.sub_id = sub_id
            self.sub_plan = sub_plan
            self.sub_date = sub_date
            self.sub_startdate = sub_startdate
            self.sub_enddate = sub_enddate
            self.sub_ref = sub_ref 
            self.sub_status = sub_status
            self.sub_paystatus = sub_paystatus
            self.sub_desiid = sub_desiid
            self.subdesiobj = subdesiobj
            self.paysubobj = paysubobj

class Payment(db.Model):
    payment_id=db.Column(db.Integer(), primary_key=True,autoincrement=True)
    payment_transNo=db.Column(db.Integer(), nullable=True)
    payment_transdate=db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    payment_amount=db.Column(db.Float(), nullable=False)
    payment_status = db.Column(db.Enum('pending', 'paid', 'failed'), server_default='pending')
    #foreignkey
    payment_desiid = db.Column(db.Integer(), db.ForeignKey("designer.desi_id"))
    payment_subid = db.Column(db.Integer(), db.ForeignKey("subscription.sub_id"))
    #relationship
    desipaymentobj=db.relationship('Designer', back_populates='paymentdesiobj')
    subpaymentobj=db.relationship('Subscription', back_populates='paysubobj')
    paynotifyobj = db.relationship('Notification', back_populates='notifypayobj')

    def __init__(self, payment_id, payment_transNo, payment_transdate, payment_amount,
                    payment_status, payment_desiid, payment_subid, desipaymentobj, subpaymentobj):
            self.payment_id = payment_id
            self.payment_transNo = payment_transNo
            self.payment_transdate = payment_transdate
            self.payment_amount = payment_amount
            self.payment_status = payment_status
            self.payment_desiid = payment_desiid
            self.payment_subid = payment_subid
            self.desipaymentobj = desipaymentobj
            self.subpaymentobj = subpaymentobj
        

class Transaction_payment(db.Model):
    tpay_id=db.Column(db.Integer(), primary_key=True,autoincrement=True)
    tpay_transNo=db.Column(db.Integer(), nullable=True)
    tpay_transdate=db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    tpay_amount=db.Column(db.Float(), nullable=False)
    tpay_status = db.Column(db.Enum('pending', 'paid', 'failed'), server_default='pending')
    #foreignkey
    tpay_desiid = db.Column(db.Integer(), db.ForeignKey("designer.desi_id"))
    tpay_custid = db.Column(db.Integer(), db.ForeignKey("customer.cust_id"))
    tpay_baid = db.Column(db.Integer(), db.ForeignKey('bookappointment.ba_id'))
    
    #relationship
    desitpayobj=db.relationship('Designer', back_populates='tpaydesiobj')
    custtpayobj=db.relationship('Customer', back_populates='tpaycustobj')
    tpaynotifyobj = db.relationship('Notification', back_populates='notifytpayobj')
    tpaybaobj = db.relationship('Bookappointment', back_populates='batpayobj')
    tpaytfobj = db.relationship('Transfer', back_populates='tftpayobj')
    
    def __init__(self, tpay_id, tpay_transNo, tpay_transdate, tpay_amount,
                    tpay_status, tpay_desiid, tpay_custid, tpay_baid, desitpayobj, custtpayobj, tpaybaobj, tpaytfobj):
            self.tpay_id = tpay_id
            self.tpay_transNo = tpay_transNo
            self.tpay_transdate = tpay_transdate
            self.tpay_amount = tpay_amount
            self.tpay_status = tpay_status
            self.tpay_desiid = tpay_desiid
            self.tpay_custid = tpay_custid
            self.tpay_baid = tpay_baid
            self.desitpayobj = desitpayobj
            self.custtpayobj = custtpayobj
            self.tpaybaobj = tpaybaobj
            self.tpaytfobj = tpaytfobj
            

class Admin (db.Model):
    admin_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    admin_fname = db.Column(db.String(255), nullable=False)
    admin_lname = db.Column(db.String(255), nullable=False)
    admin_gender = db.Column(db.Enum('male','female'), nullable=False)
    admin_phone = db.Column(db.String(225), nullable=False)
    admin_email = db.Column(db.String(255), nullable=False)
    admin_pass = db.Column(db.String(255), nullable=False)
    admin_address = db.Column(db.Text(), nullable=True)
    admin_secretword = db.Column(db.String(255), nullable=False)
    admin_pic = db.Column(db.String(255), nullable=True)

class Like(db.Model):
    like_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    like_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)

    #foreignKey
    like_postid = db.Column(db.Integer(), db.ForeignKey('posting.post_id'))
    like_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    like_custid = db.Column(db.Integer(), db.ForeignKey('customer.cust_id'))
    
    
    #relationship
    desilikesobj = db.relationship('Designer', back_populates='likedesiobj')
    custlikesobj = db.relationship('Customer', back_populates='likecustobj')
    posts = db.relationship('Posting', back_populates='likes')
    likenotifyobj = db.relationship('Notification', back_populates='notifylikeobj')

class Superadmin (db.Model):
    spadmin_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    spadmin_fname = db.Column(db.String(255), nullable=False)
    spadmin_lname = db.Column(db.String(255), nullable=False)
    spadmin_gender = db.Column(db.Enum('male','female'), nullable=False)
    spadmin_phone = db.Column(db.String(225), nullable=False)
    spadmin_email = db.Column(db.String(255), nullable=False)
    spadmin_pass = db.Column(db.String(255), nullable=False)
    spadmin_address = db.Column(db.Text(), nullable=True)
    spadmin_secretword = db.Column(db.String(255), nullable=False)
    spadmin_pic = db.Column(db.String(255), nullable=True)    

class Share(db.Model):
    share_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    share_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    share_webname = db.Column(db.String(255), nullable=False)
    #foreignKey
    share_postid = db.Column(db.Integer(), db.ForeignKey('posting.post_id'))
    share_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    share_custid = db.Column(db.Integer(), db.ForeignKey('customer.cust_id'))
    #relationship
    desishareobj = db.relationship('Designer', back_populates='sharedesiobj')
    custshareobj = db.relationship('Customer', back_populates='sharecustobj')
    postshareobj = db.relationship('Posting', back_populates='sharepostobj')
    sharenotifyobj = db.relationship('Notification', back_populates='notifyshareobj')
    

class Bookappointment(db.Model):
    ba_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    ba_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    ba_bookingDate = db.Column(db.String(255), nullable=False)
    ba_bookingTime = db.Column(db.String(255), nullable=False)
    ba_collectionDate = db.Column(db.String(255), nullable=False)
    ba_collectionTime = db.Column(db.String(255), nullable=False)
    ba_status = db.Column(db.Enum('accept', 'decline', 'not decided', 'completed', 'not done'), nullable=False, server_default='not decided')
    ba_custstatus = db.Column(db.Enum('collected', 'not collected'), nullable=False, server_default='not collected')
    ba_paystatus = db.Column(db.Enum('pending', 'paid', 'failed'), server_default='pending')
    
    #foreignKey
    ba_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    ba_custid = db.Column(db.Integer(), db.ForeignKey('customer.cust_id'))
    #relationship
    desibaobj = db.relationship('Designer', back_populates='badesiobj')
    custbaobj = db.relationship('Customer', back_populates='bacustobj')
    banotifyobj = db.relationship('Notification', back_populates='notifybaobj')
    bajbobj=db.relationship('Job', back_populates='jbbaobj')
    batpayobj = db.relationship('Transaction_payment', back_populates='tpaybaobj')
    
    def __init__(self, ba_id, ba_bookingDate, ba_date, ba_bookingTime,
                    ba_collectionDate , ba_collectionTime, ba_status, ba_custstatus, ba_paystatus, ba_desiid, ba_custid, desibaobj, custbaobj, bajbobj, batpayobj):
            self.ba_id = ba_id
            self.ba_bookingDate = ba_bookingDate
            self.ba_date = ba_date
            self.ba_bookingTime = ba_bookingTime
            self.ba_collectionDate  = ba_collectionDate 
            self.ba_collectionTime = ba_collectionTime
            self.ba_status = ba_status
            self.ba_custstatus = ba_custstatus
            self.ba_paystatus = ba_paystatus
            self.ba_desiid = ba_desiid
            self.ba_custid = ba_custid
            self.desibaobj = desibaobj
            self.custbaobj = custbaobj
            self.bajbobj = bajbobj
            self.batpayobj = batpayobj

class Job(db.Model):
    jb_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    jb_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    jb_status=db.Column(db.Enum("not done", "completed", "collected"), nullable=False, server_default="not done")
    jb_pic=db.Column(db.String(225), nullable=False)
    
    #foreignKey
    jb_custid=db.Column(db.Integer(), db.ForeignKey('customer.cust_id'))
    jb_desiid=db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    jb_baid = db.Column(db.Integer(), db.ForeignKey('bookappointment.ba_id'))

    #relationship
    jbbaobj=db.relationship('Bookappointment', back_populates='bajbobj')
    jbcustobj=db.relationship('Customer', back_populates='custjbobj')
    jbdesiobj=db.relationship('Designer', back_populates='desijbobj')
    


class Notification(db.Model):
    notify_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    notify_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    notify_read = db.Column(db.Enum('read', 'unread'), nullable=False, server_default='unread')
    # foreignKey
    notify_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    notify_custid = db.Column(db.Integer(), db.ForeignKey('customer.cust_id'))
    notify_postid = db.Column(db.Integer(), db.ForeignKey('posting.post_id'))
    notify_likeid = db.Column(db.Integer(), db.ForeignKey('like.like_id'))
    notify_comid = db.Column(db.Integer(), db.ForeignKey('comment.com_id'))
    notify_shareid = db.Column(db.Integer(), db.ForeignKey('share.share_id'))
    notify_baid = db.Column(db.Integer(), db.ForeignKey('bookappointment.ba_id'))
    notify_subid = db.Column(db.Integer(), db.ForeignKey('subscription.sub_id'))
    notify_paymentid = db.Column(db.Integer(), db.ForeignKey('payment.payment_id'))
    notify_tpayid = db.Column(db.Integer(), db.ForeignKey('transaction_payment.tpay_id'))
    
    # relationship
    notifydesiobj = db.relationship('Designer', back_populates='desinotifyobj')
    notifycustobj = db.relationship('Customer', back_populates='custnotifyobj')
    notifypostobj = db.relationship('Posting', back_populates='postnotifyobj')
    notifylikeobj = db.relationship('Like', back_populates='likenotifyobj')
    notifycomobj = db.relationship('Comment', back_populates='comnotifyobj')
    notifyshareobj = db.relationship('Share', back_populates='sharenotifyobj')
    notifybaobj = db.relationship('Bookappointment', back_populates='banotifyobj')
    notifysubobj = db.relationship('Subscription', back_populates='subnotifyobj')
    notifypayobj = db.relationship('Payment', back_populates='paynotifyobj')
    notifytpayobj = db.relationship('Transaction_payment', back_populates='tpaynotifyobj')
    
   
    def save(self):
        db.session.add(self)
        db.session.commit()

class Report(db.Model):
    report_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    report_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    report_reason = db.Column(db.String(255), nullable=False)
    reporter=db.Column(db.String(255), nullable=False)
    #foreignKey
    report_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    report_custid = db.Column(db.Integer(), db.ForeignKey('customer.cust_id'))
    #relationship
    desireportobj = db.relationship('Designer', back_populates='reportdesiobj')
    custreportobj = db.relationship('Customer', back_populates='reportcustobj')

class Rating(db.Model):
    rat_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    rat_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    rat_rating= db.Column(db.Integer(), nullable=False)
    #foreignKey
    rat_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    rat_custid = db.Column(db.Integer(), db.ForeignKey('customer.cust_id'))
    #relationship
    desiratobj = db.relationship('Designer', back_populates='ratdesiobj')
    custratobj = db.relationship('Customer', back_populates='ratcustobj')

class Newsletter(db.Model):
    news_id=db.Column(db.Integer(), primary_key=True, autoincrement=True)
    news_name=db.Column(db.String(225), nullable=False)
    news_email=db.Column(db.String(225), nullable=False)
    news_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    

class Bank(db.Model):
    bnk_id=db.Column(db.Integer(), primary_key=True, autoincrement=True)
    bnk_acname=db.Column(db.String(225), nullable=False)
    bnk_bankname=db.Column(db.String(225), nullable=False)
    bnk_acno=db.Column(db.String(15), nullable=False)
    bnk_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    
    #forignKey
    bnk_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    
    #relationship
    desibnkobj = db.relationship('Designer', back_populates='bnkdesiobj')

class Bankcodes(db.Model):
    id=db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name=db.Column(db.String(100), nullable=False)
    code=db.Column(db.String(10), nullable=False)
    
    def __init__(self, id, name, code):
        self.id = id
        self.name = name
        self.code = code
    
class Follow(db.Model):
    follow_id=db.Column(db.Integer(), primary_key=True, autoincrement=True)
    #foreignKey
    follow_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    follow_custid = db.Column(db.Integer(), db.ForeignKey('customer.cust_id'))
    #relationship
    desifollowobj = db.relationship('Designer', back_populates='followdesiobj')
    custfollowobj = db.relationship('Customer', back_populates='followcustobj')


class Login(db.Model):
    login_id=db.Column(db.Integer(), primary_key=True, autoincrement=True)
    login_email=db.Column(db.String(225), nullable=False)
    login_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    logout_date = db.Column(db.DateTime(), nullable=False)
    
    #foreignKey
    login_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    login_custid = db.Column(db.Integer(), db.ForeignKey('customer.cust_id'))
    #relationship
    desiloginobj = db.relationship('Designer', back_populates='logindesiobj')
    custloginobj = db.relationship('Customer', back_populates='logincustobj')


class Transfer(db.Model):
    tf_id=db.Column(db.Integer(), primary_key=True, autoincrement=True)
    tf_createdAt = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    tf_updatedAt = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    tf_reference = db.Column(db.Integer(), nullable=True)
    tf_RecipientCode = db.Column(db.String(225), nullable=False)
    tf_receiverAcName = db.Column(db.String(100), nullable=False)
    tf_receiverAcNo = db.Column(db.String(10), nullable=False)
    tf_receiverbankName = db.Column(db.String(100), nullable=False)
    tf_receiverEmail = db.Column(db.String(225), nullable=False)
    tf_amountRemited = db.Column(db.String(225), nullable=False)
    tf_integrationCode = db.Column(db.String(10), nullable=False)
    tf_receiptId = db.Column(db.String(225), nullable=False)
    tf_message = db.Column(db.String(225), nullable=False)
    tf_depositor = db.Column(db.String(225), nullable=False)
    tf_status = db.Column(db.Enum("pending","success", "failed", "reversed"), nullable=False, server_default="pending")
    # ForeignKey
    tf_tpayid = db.Column(db.Integer(), db.ForeignKey('transaction_payment.tpay_id'))
    #Relationship
    tftpayobj = db.relationship('Transaction_payment', back_populates='tpaytfobj')
    
    def __init__(self, tf_id, tf_createdAt, tf_updatedAt, tf_reference, tf_RecipientCode,
                 tf_receiverAcName, tf_receiverAcNo, tf_receiverbankName, tf_receiverEmail,
                 tf_amountRemited, tf_integrationCode, tf_receiptId, tf_message, tf_depositor, 
                 tf_status, tf_tpayid, tftpayobj):
        
        self.tf_id=tf_id
        self.tf_createdAt = tf_createdAt
        self.tf_updatedAt = tf_updatedAt
        self.tf_reference = tf_reference
        self.tf_RecipientCode = tf_RecipientCode
        self.tf_receiverAcName = tf_receiverAcName
        self.tf_receiverAcNo = tf_receiverAcNo
        self.tf_receiverbankName = tf_receiverbankName
        self.tf_receiverEmail = tf_receiverEmail
        self.tf_amountRemited = tf_amountRemited
        self.tf_integrationCode = tf_integrationCode
        self.tf_receiptId = tf_receiptId
        self.tf_message = tf_message
        self.tf_depositor = tf_depositor
        self.tf_status = tf_status
        self.tf_tpayid = tf_tpayid
        self.tftpayobj = tftpayobj
        
        