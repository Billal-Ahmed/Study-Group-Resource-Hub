import os
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cs50-study-hub-dev-key")

DB_PATH = os.path.join(os.path.dirname(__file__), "hub.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT UNIQUE NOT NULL,
            hash       TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS groups (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            description TEXT,
            course_code TEXT,
            created_by  INTEGER NOT NULL REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS group_members (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id  INTEGER NOT NULL REFERENCES groups(id),
            user_id   INTEGER NOT NULL REFERENCES users(id),
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(group_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS resources (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id      INTEGER NOT NULL REFERENCES groups(id),
            user_id       INTEGER NOT NULL REFERENCES users(id),
            title         TEXT NOT NULL,
            link_or_note  TEXT NOT NULL,
            resource_type TEXT NOT NULL CHECK(resource_type IN ('link', 'note')),
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS deadlines (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id   INTEGER NOT NULL REFERENCES groups(id),
            title      TEXT NOT NULL,
            due_date   TEXT NOT NULL,
            created_by INTEGER NOT NULL REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()


init_db()


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")

        if not username:
            flash("Username is required.", "danger")
            return render_template("register.html")
        if not password:
            flash("Password is required.", "danger")
            return render_template("register.html")
        if password != confirmation:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        hashed = generate_password_hash(password)
        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                (username, hashed)
            )
            conn.commit()
            user = conn.execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            ).fetchone()
            conn.close()
        except sqlite3.IntegrityError:
            flash("Username already taken.", "danger")
            return render_template("register.html")

        session["user_id"] = user["id"]
        flash("Account created! Welcome to Study Hub.", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please provide both username and password.", "danger")
            return render_template("login.html")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if user is None or not check_password_hash(user["hash"], password):
            flash("Invalid username or password.", "danger")
            return render_template("login.html")

        session["user_id"] = user["id"]
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route("/")
@login_required
def index():
    uid = session["user_id"]
    conn = get_db()

    my_groups = conn.execute("""
        SELECT g.*, u.username AS creator
        FROM groups g
        JOIN group_members gm ON gm.group_id = g.id
        JOIN users u ON u.id = g.created_by
        WHERE gm.user_id = ?
        ORDER BY g.name
    """, (uid,)).fetchall()

    group_ids = [g["id"] for g in my_groups]
    upcoming = []
    if group_ids:
        placeholders = ",".join("?" * len(group_ids))
        upcoming = conn.execute(f"""
            SELECT d.*, g.name AS group_name
            FROM deadlines d
            JOIN groups g ON g.id = d.group_id
            WHERE d.group_id IN ({placeholders})
              AND d.due_date >= DATE('now')
            ORDER BY d.due_date ASC
        """, group_ids).fetchall()

    conn.close()
    return render_template("index.html", my_groups=my_groups, upcoming=upcoming)


# ── Groups ────────────────────────────────────────────────────────────────────

@app.route("/groups", methods=["GET", "POST"])
@login_required
def groups():
    uid = session["user_id"]
    conn = get_db()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        course_code = request.form.get("course_code", "").strip().upper()

        if not name:
            flash("Group name is required.", "danger")
        else:
            cur = conn.execute(
                "INSERT INTO groups (name, description, course_code, created_by) VALUES (?, ?, ?, ?)",
                (name, description, course_code, uid)
            )
            group_id = cur.lastrowid
            # Auto-join creator
            conn.execute(
                "INSERT INTO group_members (group_id, user_id) VALUES (?, ?)",
                (group_id, uid)
            )
            conn.commit()
            flash(f'Group "{name}" created!', "success")
            conn.close()
            return redirect(url_for("group_detail", group_id=group_id))

    query = request.args.get("q", "").strip()
    if query:
        all_groups = conn.execute("""
            SELECT g.*, u.username AS creator,
                   COUNT(gm.user_id) AS member_count
            FROM groups g
            JOIN users u ON u.id = g.created_by
            LEFT JOIN group_members gm ON gm.group_id = g.id
            WHERE g.name LIKE ? OR g.course_code LIKE ?
            GROUP BY g.id
            ORDER BY g.name
        """, (f"%{query}%", f"%{query}%")).fetchall()
    else:
        all_groups = conn.execute("""
            SELECT g.*, u.username AS creator,
                   COUNT(gm.user_id) AS member_count
            FROM groups g
            JOIN users u ON u.id = g.created_by
            LEFT JOIN group_members gm ON gm.group_id = g.id
            GROUP BY g.id
            ORDER BY g.name
        """).fetchall()

    # Collect groups the current user has already joined
    joined_ids = {
        row["group_id"]
        for row in conn.execute(
            "SELECT group_id FROM group_members WHERE user_id = ?", (uid,)
        ).fetchall()
    }
    conn.close()
    return render_template("groups.html", all_groups=all_groups,
                           joined_ids=joined_ids, query=query)


@app.route("/groups/<int:group_id>")
@login_required
def group_detail(group_id):
    uid = session["user_id"]
    conn = get_db()

    group = conn.execute("SELECT * FROM groups WHERE id = ?", (group_id,)).fetchone()
    if not group:
        flash("Group not found.", "danger")
        conn.close()
        return redirect(url_for("groups"))

    is_member = conn.execute(
        "SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?",
        (group_id, uid)
    ).fetchone()

    members = conn.execute("""
        SELECT u.username, gm.joined_at
        FROM group_members gm
        JOIN users u ON u.id = gm.user_id
        WHERE gm.group_id = ?
        ORDER BY gm.joined_at
    """, (group_id,)).fetchall()

    resources = conn.execute("""
        SELECT r.*, u.username AS posted_by
        FROM resources r
        JOIN users u ON u.id = r.user_id
        WHERE r.group_id = ?
        ORDER BY r.created_at DESC
    """, (group_id,)).fetchall()

    deadlines = conn.execute("""
        SELECT d.*, u.username AS added_by
        FROM deadlines d
        JOIN users u ON u.id = d.created_by
        WHERE d.group_id = ?
        ORDER BY d.due_date ASC
    """, (group_id,)).fetchall()

    conn.close()
    return render_template("group_detail.html", group=group, members=members,
                           resources=resources, deadlines=deadlines,
                           is_member=is_member)


@app.route("/groups/<int:group_id>/join", methods=["POST"])
@login_required
def join_group(group_id):
    uid = session["user_id"]
    conn = get_db()
    group = conn.execute("SELECT id FROM groups WHERE id = ?", (group_id,)).fetchone()
    if not group:
        flash("Group not found.", "danger")
        conn.close()
        return redirect(url_for("groups"))
    try:
        conn.execute(
            "INSERT INTO group_members (group_id, user_id) VALUES (?, ?)",
            (group_id, uid)
        )
        conn.commit()
        flash("You joined the group!", "success")
    except sqlite3.IntegrityError:
        flash("You are already a member.", "warning")
    conn.close()
    return redirect(url_for("group_detail", group_id=group_id))


@app.route("/groups/<int:group_id>/leave", methods=["POST"])
@login_required
def leave_group(group_id):
    uid = session["user_id"]
    conn = get_db()
    conn.execute(
        "DELETE FROM group_members WHERE group_id = ? AND user_id = ?",
        (group_id, uid)
    )
    conn.commit()
    conn.close()
    flash("You left the group.", "info")
    return redirect(url_for("groups"))


@app.route("/groups/<int:group_id>/resource", methods=["POST"])
@login_required
def add_resource(group_id):
    uid = session["user_id"]
    title = request.form.get("title", "").strip()
    link_or_note = request.form.get("link_or_note", "").strip()
    resource_type = request.form.get("resource_type", "")

    if not title or not link_or_note or resource_type not in ("link", "note"):
        flash("All resource fields are required.", "danger")
        return redirect(url_for("group_detail", group_id=group_id))

    conn = get_db()
    # Only members may post
    is_member = conn.execute(
        "SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?",
        (group_id, uid)
    ).fetchone()
    if not is_member:
        flash("Join the group to post resources.", "warning")
        conn.close()
        return redirect(url_for("group_detail", group_id=group_id))

    conn.execute(
        "INSERT INTO resources (group_id, user_id, title, link_or_note, resource_type) VALUES (?, ?, ?, ?, ?)",
        (group_id, uid, title, link_or_note, resource_type)
    )
    conn.commit()
    conn.close()
    flash("Resource added!", "success")
    return redirect(url_for("group_detail", group_id=group_id))


@app.route("/groups/<int:group_id>/deadline", methods=["POST"])
@login_required
def add_deadline(group_id):
    uid = session["user_id"]
    title = request.form.get("title", "").strip()
    due_date = request.form.get("due_date", "").strip()

    if not title or not due_date:
        flash("Deadline title and date are required.", "danger")
        return redirect(url_for("group_detail", group_id=group_id))

    conn = get_db()
    is_member = conn.execute(
        "SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?",
        (group_id, uid)
    ).fetchone()
    if not is_member:
        flash("Join the group to add deadlines.", "warning")
        conn.close()
        return redirect(url_for("group_detail", group_id=group_id))

    conn.execute(
        "INSERT INTO deadlines (group_id, title, due_date, created_by) VALUES (?, ?, ?, ?)",
        (group_id, title, due_date, uid)
    )
    conn.commit()
    conn.close()
    flash("Deadline added!", "success")
    return redirect(url_for("group_detail", group_id=group_id))
