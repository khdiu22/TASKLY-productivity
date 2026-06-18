import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "..."

#DATABASE = "taskly.db"
DATABASE = r"C:\Tuwaiq\Noof_Abdullah_Alarifi\Taskly\taskly.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    tasks = conn.execute("""
        SELECT tasks.*,
               categories.name AS category_name
        FROM tasks
        LEFT JOIN categories
        ON tasks.category_id = categories.id
        WHERE tasks.user_id = ?
        ORDER BY tasks.id DESC
    """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template("task_list.html", tasks=tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = get_db()

        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("home"))

        else:
            return "Invalid username or password"

    return render_template("login.html")

@app.route("/categories", methods=["GET", "POST"])
def categories():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    if request.method == "POST":
        name = request.form["name"]
        color = request.form["color"]

        conn.execute(
            "INSERT INTO categories (name, color, user_id) VALUES (?, ?, ?)",
            (name, color, session["user_id"])
        )

        conn.commit()
        conn.close()

        return redirect(url_for("categories"))

    categories = conn.execute(
        "SELECT * FROM categories WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template("categories_list.html", categories=categories)


@app.route("/tasks/add", methods=["GET", "POST"])
def add_task():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    categories = conn.execute(
        "SELECT * FROM categories WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        priority = request.form["priority"]
        due_date = request.form["due_date"]
        status = request.form["status"]
        category_id = request.form["category_id"]

        if category_id == "":
            category_id = None

        conn.execute(
            """
            INSERT INTO tasks 
            (title, description, priority, due_date, status, category_id, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                description,
                priority,
                due_date,
                status,
                category_id,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    conn.close()

    return render_template("task_add.html", categories=categories)


@app.route("/tasks/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        priority = request.form["priority"]
        due_date = request.form["due_date"]
        status = request.form["status"]
        category_id = request.form["category_id"]

        if category_id == "":
            category_id = None

        conn.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, priority = ?, due_date = ?, status = ?, category_id = ?
            WHERE id = ? AND user_id = ?
            """,
            (title, description, priority, due_date, status, category_id, task_id, session["user_id"])
        )

        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"])
    ).fetchone()

    categories = conn.execute(
        "SELECT * FROM categories WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template("task_edit.html", task=task, categories=categories)


@app.route("/tasks/delete/<int:task_id>")
def delete_task(task_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    conn.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"])
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)