import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, Task

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ------------ DB: use Neon when DATABASE_URL is set; fallback to SQLite locally ------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///todo.db")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
# ------------------------------------------------------------------------------------------

login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------- Routes ---------------- #

@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials")

    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"], method="pbkdf2:sha256", salt_length=16)

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("register"))

        # Create new user
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        # Automatically log in the user after registration
        login_user(new_user)

        flash("Registration successful! You are now logged in.")
        return redirect(url_for("dashboard"))  # Redirect to the dashboard after successful registration

    return render_template("register.html")

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        title = request.form["title"]
        due_date = datetime.strptime(request.form["due_date"], "%Y-%m-%dT%H:%M")  # Proper datetime formatting
        task = Task(user_id=current_user.id, title=title, due_date=due_date)
        db.session.add(task)
        db.session.commit()
        flash("Task added successfully!")
        return redirect(url_for("dashboard"))

    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", tasks=tasks)



@app.route("/task/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("Not authorized to edit this task.")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        task.title = request.form["title"]
        task.due_date = datetime.strptime(request.form["due_date"], "%Y-%m-%dT%H:%M")
        db.session.commit()
        flash("Task updated successfully!")
        return redirect(url_for("dashboard"))

    return render_template("edit_task.html", task=task)


@app.route("/task/delete/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("Not authorized to delete this task.")
        return redirect(url_for("dashboard"))

    db.session.delete(task)
    db.session.commit()
    flash("Task deleted successfully!")
    return redirect(url_for("dashboard"))


@app.route("/task/complete/<int:task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("Not authorized to mark this task as completed.")
        return redirect(url_for("dashboard"))

    task.completed = True
    db.session.commit()
    flash("Task marked as completed!")
    return redirect(url_for("dashboard"))


# ---------------- Main ---------------- #
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
