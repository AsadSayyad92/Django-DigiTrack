# Django-DigiTrack

A Django-based web application for managing student attendance. Modern UI with Tailwind CSS, modular structure, and role-based authentication.

## Features
- Track student attendance and absences
- Dashboard and summary views
- Tailwind-based UI and reusable templates
- Authentication and role-based access
- Modular app layout for easy extension

## Project structure
```
Django-DigiTrack/
├─ attendance/           # Main Django app (models, views, templates)
├─ attendance_app/       # Additional attendance logic / modules
├─ static/               # CSS, JS, images
├─ theme/                # Tailwind config and custom styles
├─ myenv/                # (optional) virtual environment
├─ db.sqlite3            # Development DB
├─ manage.py             # Django CLI entrypoint
├─ requirements.txt      # Python dependencies
├─ student_temp.txt      # Sample student template
└─ student_view.txt      # Sample student view
```

## Prerequisites
- Python 3.8+
- pip
- (Optional) Node.js & npm for Tailwind build tools

## Installation
Clone and install dependencies:
```bash
git clone https://github.com/AsadSayyad92/Django-DigiTrack.git
cd Django-DigiTrack
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Apply migrations and run the server:
```bash
python manage.py migrate
python manage.py createsuperuser   # optional: create admin user
python manage.py runserver
```
Open http://localhost:8000

## Usage
- Add or update student attendance records via the app UI
- View dashboards and summary reports
- Customize styling in the `theme/` and `static/` folders

## Development notes
- Tailwind: rebuild assets if you modify `theme/` (npm scripts / build pipeline)
- App structure is modular — add new apps or views under the project folder

## Contributing
1. Fork the repo
2. Create a branch: git checkout -b feature/YourFeature
3. Commit changes: git commit -am "Add feature"
4. Push: git push origin feature/YourFeature
5. Open a Pull Request

## License
MIT — see LICENSE file.

## Tech stack
Python, Django, JavaScript, HTML, CSS, Tailwind CSS

For questions or issues, open a GitHub Issue in the repository.
