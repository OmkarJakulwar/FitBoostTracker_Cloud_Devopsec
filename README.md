# FitBoostTracker

A Django web app for logging workouts and exercises, tracking fitness progress, and viewing weekly stats on a personal dashboard. It is deployed to **AWS Elastic Beanstalk** through a **CI/CD pipeline in GitHub Actions** that runs automated tests, static code analysis (SAST with SonarCloud), and dynamic security testing (DAST with OWASP ZAP).

This was built as an academic project in Cloud DevSecOps.

---

## Features

- **User accounts**: sign up, log in and log out with `django-allauth`. Google and GitHub providers are configured.
- **Dashboard**: shows today's workouts, calories burned this week, workouts this month and BMI, with Chart.js charts for weekly duration, daily calories and the exercise breakdown.
- **Workouts**: create, edit and delete workouts with a type (Cardio, Strength, Yoga, Running and more), duration, intensity (1 to 5), calories and notes.
- **Exercises**: add sets, reps, weight and distance to each workout, and filter every exercise by workout type.
- **Profile**: upload an avatar, update age, height, weight, gender and fitness goal, and change the password. BMI is calculated automatically.
- **Per-user data isolation**: each query is scoped to the logged-in user, so users can't view or edit each other's records.

## Tech Stack

| Area | Tools |
|---|---|
| Backend | Python 3.12, Django 5.2, django-allauth |
| Frontend | Django Templates, Bootstrap 5, Bootstrap Icons, Chart.js, crispy-forms |
| Database | SQLite (local) / MySQL (production, via PyMySQL) |
| App server | Gunicorn behind Nginx |
| Cloud (AWS) | Elastic Beanstalk, S3 (deployment artifacts), IAM |
| CI/CD | GitHub Actions |
| Code quality / SAST | SonarCloud, coverage.py |
| DAST | OWASP ZAP Baseline Scan |

## CI/CD Pipeline

The pipeline is made of three GitHub Actions workflows. Each one starts after the previous one finishes.

**1. CI Tests and SonarCloud** (`.github/workflows/sonar-ci.yml`)
Runs on every push and pull request to `main`/`master`:
- Installs dependencies and runs the Django unit tests with `coverage`.
- Sends the code and the coverage report to **SonarCloud** for static analysis. SonarCloud checks for bugs, code smells, security hotspots and vulnerabilities.
- Packages the app into a ZIP and uploads it to an **S3 bucket**.

**2. Deploy to Elastic Beanstalk** (`.github/workflows/deploy-eb.yml`)
Runs only if the CI workflow **succeeds**:
- Creates a new application version in Elastic Beanstalk from the ZIP in S3.
- Updates the environment to that version. On deploy, `.ebextensions` runs `migrate` and `collectstatic`.

**3. ZAP Security Scan** (`.github/workflows/zap-scan.yml`)
Runs after deployment. It can also be started manually.
- Polls Elastic Beanstalk until the environment health is **Green**.
- Runs an **OWASP ZAP baseline scan** against the live URL to find runtime issues such as missing security headers, cookie flags and information leaks. The report is saved as a workflow artifact.

All AWS credentials, the Django secret key and the Sonar token are stored as **GitHub Secrets**. Third-party actions are pinned to a full commit SHA to reduce supply-chain risk.

## Project Structure

```
fitboostracker/     Django project settings, root URLs, WSGI
fittracker/         Auth, dashboard, profile, chart data API, base templates
fitworkouts/        Workout model, forms and CRUD views
fitexercises/       Exercise model (linked to Workout), forms and CRUD views
.github/workflows/  CI, deploy and ZAP scan pipelines
.ebextensions/      Elastic Beanstalk packages, env config, migrate/collectstatic
.platform/nginx/    Nginx config that serves static files on Elastic Beanstalk
sonar-project.properties   SonarCloud configuration
Procfile            Gunicorn start command
```

## Run Locally

```bash
git clone https://github.com/OmkarJakulwar/FitBoostTracker_Cloud_Devopsec.git
cd FitBoostTracker_Cloud_Devopsec

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser  # optional, for /admin
python manage.py runserver
```

Open http://127.0.0.1:8000. Locally the app uses SQLite. When the environment variable `EB_ENV=production` is set, it switches to MySQL and reads the `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` and `DB_PORT` variables.

## Running Tests

```bash
coverage run manage.py test
coverage report
```

The suite covers views, forms, authentication redirects and per-user access across all three apps.

## GitHub Secrets Required

| Secret | Purpose |
|---|---|
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_REGION` | AWS access for S3 and Elastic Beanstalk |
| `S3_BUCKET_NAME` | Bucket that stores the deployment ZIP |
| `EB_APP_NAME`, `EB_ENV_NAME` | Elastic Beanstalk application and environment |
| `APP_URL` | Live URL scanned by OWASP ZAP |
| `SONAR_TOKEN` | SonarCloud authentication |
| `DJANGO_SECRET_KEY` | Django secret key |

## Author

**Omkar Jakulwar**
