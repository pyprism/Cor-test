# cor-test

#### Run locally
```
docker-compose up
```
#### Run test
```
docker-compose exec web python manage.py test
```

### Work flow
  - Create superuser from terminal `docker-compose exec web python manage.py createsuperuser`
  - Go to `http://127.0.0.1:8000/v1/api/account/` and login, after login superuser can create employee and restaurant owner
  - Logout and login again using restaurant user, then go to `http://127.0.0.1:8000/v1/api/restaurant/` to create restaurant
  - A restaurant owner can create menu using this `http://127.0.0.1:8000/v1/api/restaurant/create_menu/` endpoint
  - A restaurant owner can view all menu from his restaurant using this endpoint `http://127.0.0.1:8000/v1/api/restaurant/get_all_menu/`
  - Restaurant owner and employee both can see all available menu from this endpoint `http://127.0.0.1:8000/v1/api/menu/`
  - Logout and login again using employee account, then go to `http://127.0.0.1:8000/v1/api/vote/` for vote status
  - Only employee can cast a vote using this endpoint `http://127.0.0.1:8000/v1/api/vote/`
  - Anyone can see vote result in this endpoint `http://127.0.0.1:8000/v1/api/vote_result/`
