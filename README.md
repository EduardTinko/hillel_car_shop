## Config Vars

- 'DJANGO_ADMIN_PASSWORD': Site admin password (Default "admin").
- 'DJANGO_SECRET_KEY': The secret key used to secure user sessions.
- 'EMAIL_HOST_PASSWORD': Password SMTP
- 'GOOGLE_APPLICATION_CREDENTIALS': 'google_application_credentials.json'
 Add the content of your JSON file with Google Cloud credentials to a file named google_application_credentials.json.
- 'GOOGLE_CLIENT_ID': Client ID in GOOGLE API
- 'GOOGLE_CLIENT_SECRET': Client secret in GOOGLE API
- 'MONOBANK_TOKEN': Your monobank token

Installation:
```angular2html
pip install -r requirements.txt
```
Run Doker:
```angular2html
docker run -p 5432:5432 -e POSTGRES_PASSWORD=password postgres
```
Create database:
```angular2html
python manage.py migrate
```
Load demo database(optional):
```angular2html
python manage.py fake_date
```
Create admin(optional):
```angular2html
python manage.py create_admin
```
For login:
username = admin
password = DJANGO_ADMIN_PASSWORD

Run server:
```angular2html
python manage.py runserver
```
