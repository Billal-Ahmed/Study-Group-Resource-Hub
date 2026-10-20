# Study Group & Resource Hub

#### Video Demo: https://youtu.be/ZXwhw0cq7A0

#### Description

Study Group & Resource Hub is a small web application for students who want one place to organize peer study groups, exchange useful materials, and keep track of coursework due dates. It was built with Flask, SQLite, Jinja templates, Bootstrap, and JavaScript as my CS50x final project. The original community context for the project is students at Degree College Skardu, but the group and course fields are flexible enough to be used by other classes too.

The app starts with account registration and login. Once signed in, a student sees a dashboard of groups they belong to and future deadlines associated with those groups. The groups page lists available groups and supports searching by group name or course code. Students can create a group with a name, course code, and description, or join an existing group. A new group’s creator is automatically enrolled as its first member.

Each group has a detail page with a member list and separate Resources and Deadlines tabs. Members can post either a link or a short note as a resource, and can add a deadline with a title and due date. The dashboard brings upcoming dates from all of a student’s joined groups together so they do not have to open every group to check what is due. A student can leave a group, and a confirmation dialog helps prevent doing so accidentally. Visitors who are not logged in are redirected to the login page for protected features.

### Implementation and design

Flask routes in `app.py` handle registration, login/logout, the dashboard, group discovery and creation, membership changes, and resource and deadline submissions. SQLite is accessed directly using Python’s `sqlite3` module and parameterized queries. I chose raw SQL instead of an ORM because it keeps the project’s data operations visible and gives practice with SQL fundamentals. The database schema is created with `CREATE TABLE IF NOT EXISTS` when the app starts, so a new local database is initialized automatically.

The database separates users, groups, group membership, resources, and deadlines into related tables. A unique constraint on each group/user membership pair prevents duplicate membership, while a check constraint limits resource types to links and notes. Passwords are stored as hashes generated and checked with Werkzeug rather than being stored in plaintext. Routes that create group content verify membership on the server before writing it; the browser interface is not treated as an authorization boundary.

The interface uses server-rendered Jinja templates and Bootstrap rather than a separate front-end framework. This keeps the application straightforward to run while still providing responsive layouts, navigation, forms, alerts, and tabs. Client-side validation improves feedback, while the Flask routes also perform their own essential checks before accepting submitted values.

### Project files

- `app.py` defines the Flask application, initializes the SQLite schema, queries and updates the database, validates form data, and renders pages.
- `helpers.py` provides the `login_required` decorator used to redirect unauthenticated visitors away from protected routes.
- `requirements.txt` lists the Python packages needed to run the app: Flask and Werkzeug.
- `templates/layout.html` is the shared page shell, including navigation, flash messages, external Bootstrap assets, and the footer.
- `templates/index.html` renders the dashboard’s joined groups and upcoming deadlines.
- `templates/groups.html` renders group search results, membership actions, and the create-group modal.
- `templates/group_detail.html` renders group information, members, resources, deadlines, and the forms for members to add content.
- `templates/login.html` and `templates/register.html` contain the authentication forms.
- `static/styles.css` defines the project’s colors, cards, badges, spacing, and responsive adjustments.
- `static/script.js` adds browser-side form validation, password confirmation, resource-type hints, and the leave-group confirmation dialog.
- `hub.db` is the local SQLite database created and populated while the application runs; it is runtime data, not required source code.

### Run locally

Use Python 3 and install the dependencies from the project directory:

```bash
py -m pip install -r requirements.txt
py -m flask --app app run
```

Then open `http://127.0.0.1:5000` in a browser, register an account, and create or join a group to explore the features. The database is stored in `hub.db` beside `app.py`. For local development, Flask can use its built-in development server; a real deployment should use a production WSGI server and set a private `SECRET_KEY` environment variable rather than relying on the development fallback in the source.
