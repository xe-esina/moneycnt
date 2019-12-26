from app import db
from app.models import User, Transaction
import datetime
from werkzeug.security import generate_password_hash

# u = User(username="admin",
#          email="admin@admin.com",
#          password_hash=generate_password_hash('password'),
#          role=ROLE_ADMIN
#          )
#
# db.session.add(u)
# db.session.commit()

# u = User.query.filter(User.username == 'colin').first()
# t = Transaction(user_id=u.id,
#                 date=datetime.date.today(),
#                 desc='Muffin',
#                 org='Starbucks',
#                 op=OP_MINUS,
#                 sum=123)
# db.session.add(t)
# db.session.commit()

# users = User.query.all()
# for u in users:
#     db.session.delete(u)
#
# posts = Transaction.query.all()
# for p in posts:
#     db.session.delete(p)
#
# db.session.commit()

