import json
from flask import jsonify, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user

from core import app, db
from core.models import Comment, User, Post


@app.route("/")
def index():
    # take all posts and send to frontend
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route("/api")
def index_api():

    posts = Post.query.all()
    if posts is None:
        return jsonify({"error": "Invalid id"}), 422
    
    return jsonify({
        "posts_count": len(posts),
        "posts": f"{posts}"
    })    

@app.route("/post/<int:id>")
def post(id):
    # data of a specefic post
    post = Post.query.get(id)
    return render_template("post.html", post=post)


@app.route("/api/post/<int:id>")
def post_api(id):
    
    post = Post.query.get(id)
    if post is None:
        return jsonify({"error": "Invalid id"}), 422

    return jsonify({
        "post_id": f"{post.id}",
        "post_author": f"{post.author}",
        "post_title": post.title,
        "post_body": post.body
    })


@app.route("/post_delete/<int:id>")
def post_delete(id):
    # -- delete post from database --
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    flash("Пост удален", "danger")
    return redirect(url_for("index"))


@app.route("/new_post", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        title = request.form.get('title')
        body = request.form.get('body')
        if len(title) == 0 or title.isspace() or len(body) == 0 or body.isspace():
            flash("Пост не может быть пустым!", "danger")

        else:
            post = Post(title=title, body=body, author_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash("Пост создан успешно", "success")
            return redirect(url_for("index"))
        
    return render_template("new_post.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Данные для входа неверные!", "danger")
    return render_template("login.html")


@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if User.query.filter_by(username=username).first():
            flash('Имя пользователя занято', 'danger')
            return redirect(url_for('registration'))
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Профиль создан успешно", "success")
        return redirect(url_for('login'))
    return render_template("registration.html")


@app.route("/logout")
def logout():
    logout_user()
    flash("До скорой встречи!", "success")
    return redirect(url_for("index"))


@app.route("/add_comment<int:post_id>", methods=["POST"])
def add_comment(post_id):
    if request.method == "POST":
        message = request.form.get("message")
        comment = Comment(message=message, author_id=current_user.id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        flash("Спасибо за комментарий!", "success")
    return redirect(url_for("post", id=post_id))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        flash("Пост создан успешно", "success")
        return redirect(url_for("index"))

    return render_template("profile.html")