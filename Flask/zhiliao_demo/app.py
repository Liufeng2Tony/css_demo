
from flask import Flask, render_template, request, redirect, url_for, session, g
import config
from models import User, Question, Answer
from exts import db
from decorators import login_required
from sqlalchemy import or_


app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)



@app.route('/')
def index():
    context = {
        # order_by()用于排序，create_time表示按照时间从小到大，在.py中使用"-"表示从大到小
        "questions":Question.query.order_by("-create_time").all()
    }
    return render_template("index.html", **context)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        telephone = request.form.get("telephone")
        password = request.form.get("password")
        user = User.query.filter(User.telephone == telephone, User.password ==password).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session.permanent = True
            return redirect(url_for("index"))
        else:
            return u"手机号码或者密码错误，请确认后登陆！"

@app.route("/regist", methods=["GET", "POST"])
def regist():
    if request.method == "GET":
        return render_template("regist.html")
    else:
        telephone = request.form.get("telephone")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user = User.query.filter(User.telephone == telephone).first()
        if user:
            return u"该手机号码已注册，请更换手机号码！"
        else:
            if password1 != password2:
                return u"两次密码不相同，请核对后再填写"
            else:
                user = User(telephone=telephone, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for("login"))

@app.route("/logout/")
def logout():
    # session.pop("user_id")
    # del session("user_id")
    session.clear()
    return redirect(url_for("login"))

@app.route("/question/", methods=["GET", "POST"])
@login_required
def question():
    if request.method == "GET":
        return render_template("question.html")
    else:
        title = request.form.get("title")
        content = request.form.get("content")
        question = Question(title=title, content=content)
        # user_id = session.get("user_id")
        # user = User.query.filter(User.id == user_id).first()
        question.author = g.user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for("index"))

@app.route("/detail/<question_id>")
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    return render_template("detail.html", question_model=question_model)

@app.route("/add_answer/", methods=["POST"])
@login_required
def add_answer():
    content = request.form.get("answer_content")
    question_id = request.form.get("question_id")

    answer = Answer(content=content)

    # user_id = session["user_id"]
    # user = User.query.filter(User.id == user_id).first()
    answer.author = g.user

    question = Question.query.filter(Question.id == question_id).first()
    answer.question = question

    db.session.add(answer)
    db.session.commit()

    return redirect(url_for("detail", question_id=question_id))

@app.route("/search/")
def search():
    q = request.args.get("q")
    questions = Question.query.filter(or_(Question.title.contains(q),Question.content.contains(q))).order_by("-create_time")
    return render_template("index.html", questions=questions)

# 使用g全局变量和钩子函数，来简化重复的代码
@app.before_request
def my_before_request():
    user_id = session.get("user_id")
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            g.user = user


# 利用上下文钩子函数，实现页面显示用户名和注销
# @app.context_processor
# def my_context_processor():
#     user_id = session.get("user_id")
#     if user_id:
#         user = User.query.filter(User.id == user_id).first()
#         if user:
#             return {"user":user}
#     return {}

# 执行顺序：before_request  ->  视图函数  ->  context_processor
# 因此可以使用g来优化代码，减少访问数据库查询的次数，提高数据库性能
@app.context_processor
def my_context_processor():
    if hasattr(g, "user"):
        return {"user":g.user}
    return {}


if __name__ == '__main__':
    app.run()
