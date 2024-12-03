from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from sqlalchemy.orm import selectinload

from db.db_setup import get_db_session
from db.models import User, Group

routes = Blueprint("routes", __name__)


# Dummy user authentication for simplicity
def authenticate(username, password):
    with get_db_session() as session:
        user = session.query(User).filter_by(chat_id=username, role="admin").first()
        return user if user and password == "adminpass" else None  # TODO: fix this line (improve security)


@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = authenticate(username, password)
        if user:
            session["user_id"] = user.id
            return redirect(url_for("routes.dashboard"))
        return "Invalid credentials", 401
    return render_template("login.html")


@routes.route('/search_students', methods=['GET'])
def search_students():
    query = request.args.get("query", "").strip().lower()
    if not query:
        return jsonify([])

    # Fetch students whose names match the query
    with get_db_session() as session:
        students = session.query(User).filter(
            User.role == "student",
            User.fullname.ilike(f"%{query}%")
        ).all()

    return jsonify([
        {"id": student.id, "fullname": student.fullname, "chat_id": student.chat_id}
        for student in students
    ])


@routes.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")  # Flask session
    if not user_id:
        return redirect(url_for("routes.login"))

    with get_db_session() as db_session:  # Use a different name for the SQLAlchemy session
        user = db_session.query(User).get(user_id)

    return render_template("dashboard.html", user=user)


@routes.route("/manage_users")
def manage_users():
    with get_db_session() as session:
        users = session.query(User).all()
    return render_template("manage_users.html", users=users)


@routes.route("/manage_groups")
def manage_groups():
    with get_db_session() as session:
        groups = session.query(Group).all()
    return render_template("manage_groups.html", groups=groups)


@routes.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("routes.login"))


@routes.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        chat_id = request.form.get("chat_id")
        name = request.form.get("fullname")
        role = request.form.get("role")
        profile_data = request.form.get("profile_data")

        if not chat_id or not name or not role:
            flash("User ID, name, and role are required!", "danger")
            return redirect(url_for("routes.add_user"))

        with get_db_session() as db_session:
            existing_user = db_session.query(User).filter_by(chat_id=chat_id).first()
            if existing_user:
                flash("User ID already exists!", "danger")
                return redirect(url_for("routes.add_user"))

            new_user = User(chat_id=chat_id, fullname=name, role=role, profile_data=profile_data)
            db_session.add(new_user)
            db_session.commit()

        flash("User added successfully!", "success")
        return redirect(url_for("routes.manage_users"))

    return render_template("add_user.html")


@routes.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    user_session_id = session.get("user_id")
    if not user_session_id:
        return redirect(url_for("routes.login"))

    with get_db_session() as db_session:
        user = db_session.query(User).get(user_id)
        if not user:
            flash("User not found!", "danger")
            return redirect(url_for("routes.manage_users"))

        if request.method == "POST":
            user.chat_id = request.form.get("chat_id", user.chat_id)
            user.fullname = request.form.get("fullname", user.fullname)
            user.role = request.form.get("role", user.role)
            user.profile_data = request.form.get("profile_data", user.profile_data)
            db_session.commit()
            flash("User updated successfully!", "success")
            return redirect(url_for("routes.manage_users"))

    return render_template("edit_user.html", user=user)


@routes.route('/edit_group/<group_id>', methods=['GET', 'POST'])
def edit_group(group_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("routes.login"))

    with get_db_session() as db_session:
        group = db_session.query(Group).options(
            selectinload(Group.students),  # Preload students relationship
            selectinload(Group.teachers)  # Preload teachers relationship
        ).filter_by(id=group_id).first()

        if not group:
            return "Group not found", 404

        if request.method == "POST":
            # Get and process selected student IDs
            group_name = request.form.get("group_name")
            teacher_ids = request.form.getlist("teacher_ids")
            student_ids = request.form.get("student_ids", "").split(",")
            student_ids = [int(sid) for sid in student_ids if sid.isdigit()]

            # Update group students
            group.name = group_name
            selected_teacher_ids = request.form.getlist('teacher_ids')
            group.teachers = [
                db_session.query(User).filter_by(id=teacher_id).first()
                for teacher_id in selected_teacher_ids
            ]
            students = db_session.query(User).filter(User.id.in_(student_ids)).all()
            group.students = students
            db_session.commit()
            flash("Group updated successfully!")
            return redirect(url_for("routes.edit_group", group_id=group_id))

        # Fetch all students for the search feature
        all_students = db_session.query(User).filter(User.role == "student").all()
        all_teachers = db_session.query(User).filter(User.role == "teacher").all()

    # Pass data to the template
    return render_template("edit_group.html", group=group, students=all_students, teachers=all_teachers)



@routes.route("/delete_user/<int:user_id>", methods=["GET", "POST"])
def delete_user(user_id):
    user_session_id = session.get("user_id")
    if not user_session_id:
        return redirect(url_for("routes.login"))

    with get_db_session() as db_session:
        user = db_session.query(User).get(user_id)
        if user:
            db_session.delete(user)
            db_session.commit()
            flash("User deleted successfully!", "success")
        else:
            flash("User not found!", "danger")

    return redirect(url_for("routes.manage_users"))


@routes.route("/delete_group/<int:group_id>", methods=["GET", "POST"])
def delete_group(group_id):
    user_session_id = session.get("user_id")
    if not user_session_id:
        return redirect(url_for("routes.login"))

    with get_db_session() as db_session:
        group = db_session.query(Group).get(group_id)
        if group:
            db_session.delete(group)
            db_session.commit()
            flash("Group deleted successfully!", "success")
        else:
            flash("Group not found!", "danger")

    return redirect(url_for("routes.manage_groups"))


@routes.route("/assign_groups/<int:user_id>", methods=["GET", "POST"])
def assign_groups(user_id):
    user_session_id = session.get("user_id")
    if not user_session_id:
        return redirect(url_for("routes.login"))

    with get_db_session() as db_session:
        user = db_session.query(User).get(user_id)
        if not user:
            flash("User not found!", "danger")
            return redirect(url_for("routes.manage_users"))

        all_groups = db_session.query(Group).all()
        if request.method == "POST":
            group_ids = request.form.getlist("groups")  # Selected group IDs
            selected_groups = db_session.query(Group).filter(Group.id.in_(group_ids)).all()
            if user.role == "teacher":
                user.teaching_groups = selected_groups
            elif user.role == "student":
                user.student_groups = selected_groups
            db_session.commit()
            flash("Groups assigned successfully!", "success")
            return redirect(url_for("routes.manage_users"))

    return render_template("assign_groups.html", user=user, groups=all_groups)


