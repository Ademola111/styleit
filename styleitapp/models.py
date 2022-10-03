import datetime
from email.policy import default

from sqlalchemy import ForeignKey
from styleitapp import db

class Posting(db.Model):
    post_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    post_title = db.Column(db.String(255), nullable=False)
    post_body = db.Column(db.Text(), nullable=True)
    post_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    #foreignkey
    post_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    #relationship
    imagepostobj = db.relationship("Image", back_populates='postimageobj')
    designerobj = db.relationship("Designer", back_populates='designerpostobj')
    postcomobj = db.relationship('Comment', back_populates='compostobj')
    # likes = db.relationship('Like', backref='posting', lazy='dynamic')
    likes = db.relationship('Like', back_populates='posts')
    sharepostobj = db.relationship('Share', back_populates='postshareobj')

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
    #foreignkey
    com_postid = db.Column(db.Integer(), db.ForeignKey('posting.post_id'))
    com_custid = db.Column(db.Integer(), db.ForeignKey('customer.cust_id'))
    com_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    parent_id = db.Column(db.Integer(), db.ForeignKey('comment.com_id'))
    #relationship
    compostobj = db.relationship('Posting', back_populates='postcomobj')
    comcustobj = db.relationship('Customer', back_populates='custcomobj')
    comdesiobj = db.relationship('Designer', back_populates='desicomobj')
    
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
    cust_fname = db.Column(db.String(255), nullable=False)
    cust_lname = db.Column(db.String(255), nullable=False)
    cust_username = db.Column(db.String(255), nullable=False)
    cust_gender = db.Column(db.Enum('male','female'), nullable=False)
    cust_phone = db.Column(db.String(225), nullable=False)
    cust_email = db.Column(db.String(255), nullable=False)
    cust_pass = db.Column(db.String(255), nullable=False)
    cust_address = db.Column(db.Text(), nullable=True)
    cust_pic = db.Column(db.String(255), nullable=True)
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
    desi_fname = db.Column(db.String(255), nullable=False)
    desi_lname = db.Column(db.String(255), nullable=False)
    desi_businessName = db.Column(db.String(255), nullable=False)
    desi_gender = db.Column(db.Enum('male','female'), nullable=False)
    desi_phone = db.Column(db.String(225), nullable=False)
    desi_email = db.Column(db.String(255), nullable=False)
    desi_pass = db.Column(db.String(255), nullable=False)
    desi_address = db.Column(db.Text(), nullable=True)
    desi_pic = db.Column(db.String(255), nullable=True)
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

class Subscription(db.Model):
    sub_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    sub_plan = db.Column(db.Enum('500','1350', '2400','4200'), nullable=False)
    sub_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    sub_startdate = db.Column(db.String(255), nullable=False)
    sub_enddate = db.Column(db.String(255), nullable=False)
    sub_ref = db.Column(db.Integer(), nullable=True)
    sub_status = db.Column(db.Enum('active', 'deactive'), server_default='active')
    sub_paystatus = db.Column(db.Enum('pending', 'paid', 'failed'), server_default='pending')
    #foreignkey
    sub_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    #relationship
    subdesiobj = db.relationship('Designer', back_populates='desisubobj')
    paysubobj=db.relationship('Payment', back_populates='subpaymentobj')


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


class Admin (db.Model):
    admin_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    admin_fname = db.Column(db.String(255), nullable=False)
    admin_lname = db.Column(db.String(255), nullable=False)
    admin_gender = db.Column(db.Enum('male','female'), nullable=False)
    admin_phone = db.Column(db.String(225), nullable=False)
    admin_email = db.Column(db.String(255), nullable=False)
    admin_pass = db.Column(db.String(255), nullable=False)
    admin_address = db.Column(db.Text(), nullable=True)
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

class Bookappointment(db.Model):
    ba_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    ba_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow(), index=True)
    ba_bookingDate = db.Column(db.String(255), nullable=False)
    ba_bookingTime = db.Column(db.String(255), nullable=False)
    ba_collectionDate = db.Column(db.String(255), nullable=False)
    ba_collectionTime = db.Column(db.String(255), nullable=False)
    ba_status = db.Column(db.Enum('accept', 'decline', 'not decided'), nullable=False, default='not decided')

    #foreignKey
    ba_desiid = db.Column(db.Integer(), db.ForeignKey('designer.desi_id'))
    ba_custid = db.Column(db.Integer(), db.ForeignKey('customer.cust_id'))
    #relationship
    desibaobj = db.relationship('Designer', back_populates='badesiobj')
    custbaobj = db.relationship('Customer', back_populates='bacustobj')
