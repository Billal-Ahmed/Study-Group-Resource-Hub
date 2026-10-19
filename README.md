# Study Group & Resource Hub

#### Video Demo: https://youtu.be/ZXwhw0cq7A0

## Description
This project is a web app built for students at Degree College Skardu to help organize study groups, share class resources, and track upcoming assignment deadlines in one place.

I built this as my CS50x final project using Flask, SQLite, Bootstrap, and plain JavaScript.

## Project Files

* `app.py`: Handles all routes (login, registration, main dashboard, group pages, joining/leaving groups, posting notes/links, and adding deadlines). It initializes the SQLite database tables on startup and uses parameterized SQL queries.
* `helpers.py`: Contains the `login_required` decorator function to protect routes from unauthenticated users.
* `hub.db`: SQLite database file storing 5 tables: `users`, `groups`, `group_members`, `resources`, and `deadlines`.
* `templates/`: Jinja2 templates for rendering HTML:
  * `layout.html`: Base template with Bootstrap navbar and flash alerts.
  * `index.html`: Dashboard showing joined groups and upcoming deadlines.
  * `groups.html`: Page to search and discover public groups, plus a modal form to create a new group.
  * `group_detail.html`: Individual group page containing resources, deadlines, and member list.
  * `login.html` & `register.html`: Auth forms with validation.
* `static/styles.css`: Custom CSS for card layouts, badges, and minor visual adjustments.
* `static/script.js`: Client-side validation, password matching checks, dynamic form placeholder toggling, and confirmation popups.

## Design Choices

* **Raw SQL over ORM:** Used direct SQLite queries with `?` placeholders instead of SQLAlchemy to practice raw SQL as taught in CS50.
* **Server-side Membership Checks:** Re-checks database membership on every write operation to ensure users can only post resources or deadlines to groups they actually belong to.
* **Modals and Tabs:** Used Bootstrap modals for group creation and tabs inside group workspaces to keep page reloads to a minimum without needing a full frontend framework like React.

## How to Run

```bash


pip install -r requirements.txt
flask run

# Git Bash
py -m flask --app app run

# PowerShell:
py -m flask --app app run
```
Open `http://127.0.0.1:5000` in your browser.# Study-Group-Resource-Hub
