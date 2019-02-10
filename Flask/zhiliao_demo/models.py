#创建数据库模型文件

from exts import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    telephone = db.Column(db.String(11), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    #对密码进行加密，使得数据库中不能明文显示密码
    def __init__(self,*args,**kwargs):
        telephone = kwargs.get("telephone")
        username = kwargs.get("username")
        password = kwargs.get("password")

        self.telephone = telephone
        self.username = username
        self.password = generate_password_hash(password)

    # 重新登陆时验证密码，因为数据库中的密码已经加密了，和客户输入的不一样
    def check_password(self,raw_password):
        result = check_password_hash(self.password,raw_password)
        return result

class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # now():调用函数值，获取服务器第一次运行的时间，如果写成这样，每次的creat_time的值将会相同
    # now:调用函数，每次创建一次模型，是获取当前的时间
    create_time = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    author = db.relationship("User", backref=db.backref("questions"))

class Answer(db.Model):
    __tablename__ = "answer"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # 在模型中需要使用desc()降序排序
    question = db.relationship("Question", backref=db.backref("answers", order_by=id.desc()))
    author = db.relationship("User", backref=db.backref("answers"))