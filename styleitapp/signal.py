from styleitapp import app
from flask.signals import Namespace

app_signal=Namespace()

post_signal = app_signal.signal('post')
comment_signal = app_signal.signal('comment')
reply_signal = app_signal.signal('reply')
like_signal = app_signal.signal('like')
unlike_signal = app_signal.signal('unlike')
subactivate_signal = app_signal.signal('subactivate')
subdeactivate_signal = app_signal.signal('subdeactivate')
payment_signal = app_signal.signal('payment')
transpay_signal = app_signal.signal('transpay')
share_signal = app_signal.signal('share')
bookappointment_signal = app_signal.signal('bookappointment')
completetask_signal = app_signal.signal('completetask')
confirmdelivery_signal = app_signal.signal('confirmdelivery')
follow_signal = app_signal.signal('follow')
unfollow_signal = app_signal.signal('unfollow')

