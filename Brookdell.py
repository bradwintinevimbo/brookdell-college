from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)

# Secret key for admin login sessions
app.secret_key = "brookdell-secret-key"


# ==============================
# DATABASE SETUP
# ==============================

def init_db():

    connection = sqlite3.connect("applications.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            course TEXT NOT NULL,
            message TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    connection.commit()
    connection.close()


# ==============================
# HOME PAGE
# ==============================

@app.route("/")
def home():

    return render_template("index.html")


# ==============================
# ABOUT US PAGE
# ==============================

@app.route("/about")
def about():

    return render_template("about.html")


# ==============================
# ACADEMICS PAGE
# ==============================

@app.route("/academics")
def academics():

    return render_template("academics.html")


# ==============================
# PROGRAMMES PAGE
# ==============================

@app.route("/programs")
def programs():

    return render_template("programs.html")


# ==============================
# GALLERY PAGE
# ==============================

@app.route("/gallery")
def gallery():

    return render_template("gallery.html")


# ==============================
# NEWS AND EVENTS PAGE
# ==============================

@app.route("/news")
def news():

    return render_template("news.html")


# ==============================
# CONTACT US PAGE
# ==============================

@app.route("/contact")
def contact():

    return render_template("contact.html")


# ==============================
# STUDENT LIFE PAGE
# ==============================

@app.route("/student-life")
def student_life():

    return render_template("student-life.html")


# ==============================
# APPLICATION FORM
# ==============================

@app.route("/apply", methods=["GET", "POST"])
def apply():

    if request.method == "POST":

        fullname = request.form.get("fullname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        course = request.form.get("course")
        message = request.form.get("message")

        connection = sqlite3.connect("applications.db")

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO applications
            (fullname, email, phone, course, message)
            VALUES (?, ?, ?, ?, ?)
        """, (
            fullname,
            email,
            phone,
            course,
            message
        ))

        connection.commit()

        connection.close()

        return redirect(
            url_for("application_success")
        )

    return render_template("apply.html")


# ==============================
# APPLICATION SUCCESS PAGE
# ==============================

@app.route("/application-success")
def application_success():

    return render_template(
        "application-success.html"
    )


# ==============================
# CHECK APPLICATION STATUS
# ==============================

@app.route("/check-status", methods=["GET", "POST"])
def check_status():

    application = None

    error = None

    if request.method == "POST":

        application_id = request.form.get(
            "application_id"
        )

        if not application_id:

            error = "Please enter your Application ID."

        else:

            connection = sqlite3.connect(
                "applications.db"
            )

            connection.row_factory = sqlite3.Row

            cursor = connection.cursor()

            cursor.execute("""
                SELECT *
                FROM applications
                WHERE id = ?
            """, (
                application_id,
            ))

            application = cursor.fetchone()

            connection.close()

            if application is None:

                error = (
                    "No application was found "
                    "with that Application ID."
                )

    return render_template(
        "check-status.html",
        application=application,
        error=error
    )


# ==============================
# ADMIN LOGIN
# ==============================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )

        # ADMIN LOGIN DETAILS
        if (
            username == "admin"
            and password == "brookdell123"
        ):

            session[
                "admin_logged_in"
            ] = True

            return redirect(
                url_for("admin_dashboard")
            )

        else:

            return render_template(
                "admin-login.html",
                error="Invalid username or password"
            )

    return render_template(
        "admin-login.html"
    )


# ==============================
# ADMIN DASHBOARD
# ==============================

@app.route("/admin/dashboard")
def admin_dashboard():

    # Check if admin is logged in
    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_login")
        )

    connection = sqlite3.connect(
        "applications.db"
    )

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM applications
        ORDER BY id DESC
    """)

    applications = cursor.fetchall()

    connection.close()

    return render_template(
        "admin-dashboard.html",
        applications=applications
    )


# ==============================
# UPDATE APPLICATION STATUS
# ==============================

@app.route(
    "/admin/update/<int:application_id>",
    methods=["POST"]
)
def update_application(application_id):

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_login")
        )

    status = request.form.get(
        "status"
    )

    connection = sqlite3.connect(
        "applications.db"
    )

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE applications
        SET status = ?
        WHERE id = ?
    """, (
        status,
        application_id
    ))

    connection.commit()

    connection.close()

    return redirect(
        url_for("admin_dashboard")
    )


# ==============================
# DELETE APPLICATION
# ==============================

@app.route(
    "/admin/delete/<int:application_id>",
    methods=["POST"]
)
def delete_application(application_id):

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_login")
        )

    connection = sqlite3.connect(
        "applications.db"
    )

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM applications
        WHERE id = ?
    """, (
        application_id,
    ))

    connection.commit()

    connection.close()

    return redirect(
        url_for("admin_dashboard")
    )


# ==============================
# ADMIN LOGOUT
# ==============================

@app.route("/admin/logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(
        url_for("admin_login")
    )


# ==============================
# START APPLICATION
# ==============================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )