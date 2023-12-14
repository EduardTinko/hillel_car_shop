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
run server:
```angular2html
python manage.py runserver
```
