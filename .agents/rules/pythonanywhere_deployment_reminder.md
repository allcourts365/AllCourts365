---
name: pythonanywhere_deployment_reminder
description: "Reminder to provide PythonAnywhere instructions after committing and pushing code."
---

# Rule: PythonAnywhere Deployment Reminder

Whenever I perform a `git commit` and `git push` on this project, I MUST automatically remind the user of the subsequent steps required to deploy these changes to PythonAnywhere (PA). 

The reminder MUST include the following instructions:
1. Access the PythonAnywhere console (Bash).
2. Navigate to the project directory (e.g., `cd /home/YOUR_USERNAME/AllCourts365`).
3. Run `git pull` to fetch the latest changes.
4. If there were database changes, run `python manage.py migrate`.
5. If there were static file changes, run `python manage.py collectstatic`.
6. Reload the web app from the "Web" tab in the PythonAnywhere dashboard (or by touching the WSGI file).
