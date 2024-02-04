## Config Vars

- 'DJANGO_ADMIN_PASSWORD': Site admin password (Default "admin").
- 'DJANGO_SECRET_KEY': The secret key used to secure user sessions.
- 'EMAIL_HOST_PASSWORD': Password SMTP.
- 'S3_BUCKET_NAME': Amazon S3 bucket name.
- 'AWS_S3_ACCESS_KEY_ID': Access key for user Amazon S3.
- 'AWS_S3_SECRET_ACCESS_KEY': Secret access key for user Amazon S3.
- 'AWS_S3_REGION_NAME': AWS Region.
- 'GOOGLE_CLIENT_ID': Client ID in GOOGLE API
- 'GOOGLE_CLIENT_SECRET': Client secret in GOOGLE API
- 'MONOBANK_TOKEN': Your monobank token

Installation:

```
pip install -r requirements.txt
```

Run Doker:

```
docker run -p 5432:5432 -e POSTGRES_PASSWORD=password postgres
```

Create database:

```
python manage.py migrate
```

Load demo database(optional):

Windows

```
$env:S3_BUCKET_NAME="bucket_name"; $env:AWS_S3_ACCESS_KEY_ID="key_id"; $env:AWS_S3_SECRET_ACCESS_KEY="access_key"; $env:AWS_S3_REGION_NAME="region_name"; python manage.py fake_date
```
Unix / Linux / macOS
```
AWS_STORAGE_BUCKET_NAME="bucket_name" AWS_S3_ACCESS_KEY_ID="key_id" AWS_S3_SECRET_ACCESS_KEY="access_key" AWS_S3_REGION_NAME="region_name" python manage.py fake_date
```

Create admin(optional):

Windows
```
$env:DJANGO_ADMIN_PASSWORD="password"; python manage.py create_admin
```
Unix / Linux / macOS
```
DJANGO_ADMIN_PASSWORD="password" python manage.py create_admin
```

For login:
username = admin, password = DJANGO_ADMIN_PASSWORD

Run server:

```
python manage.py runserver
```
