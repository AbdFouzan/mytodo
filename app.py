from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    deadline = db.Column(db.String(20), nullable=True)
    priority = db.Column(db.String(10), nullable=False, default="Medium")
    status = db.Column(db.String(10), nullable=False, default="Pending")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Task {self.id}>"

# Home (View + Add Task)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form["content"]
        deadline = request.form.get("deadline")
        priority = request.form.get("priority", "Medium")
        new_task = Task(content=content, deadline=deadline, priority=priority)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("index"))
    
    tasks = Task.query.order_by(Task.date_created.desc()).all()
    return render_template("index.html", tasks=tasks)

# Update Task
@app.route("/update/<int:task_id>", methods=["GET", "POST"])
def update(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == "POST":
        task.content = request.form["content"]
        task.deadline = request.form.get("deadline")
        task.priority = request.form.get("priority")
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("update.html", task=task)

# Delete Task
@app.route("/delete/<int:task_id>")
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("index"))

# Mark as Completed
@app.route("/complete/<int:task_id>")
def complete(task_id):
    task = Task.query.get_or_404(task_id)
    task.status = "Done" if task.status == "Pending" else "Pending"
    db.session.commit()
    return redirect(url_for("index"))

# Prevent 304 cache issues
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store"
    return response

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
