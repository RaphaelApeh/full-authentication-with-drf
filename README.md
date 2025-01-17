## Full authentication with rest framework 🔓

### Get Started 🚀
- Create virtural environment 👾
```bash
python -m venv .venv
```
- <b>Activate</b> ✨
```bash
# Windows
.\.venv\Scripts\activate
# MacOs
source .venv/bin/activate
```
- Install denpendencies 🛠<br>
```sh
pip install -r requirements.txt
```
- Set in  `.env` ⚙
```python
DJANGO_SECRET_KEY=""
DJANGO_DEBUG=True or False
```
### Settings ⚙
Email setup 🚀
```bash
# settings.py
# for production
DEFAULT_FROM_EMAIL = "your-email"
EMAIL_BACKEND = "django.core.mail.backends.smpt.EmailBackend"
EMAIL_HOST = "" # "smtp.gmail"
EMAIL_POST = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your-email"
EMAIL_HOST_PASSWORD = "password"
```
## API Routes 🕹

| HTTP Method | Route               | Description                       |
|-------------|---------------------|-----------------------------------|
| GET         | `/api/users/`         | Get all users                     |
| GET         | `/api/user/`    | Get a user by Authorization Token                  |
| POST        | `/api/register/`         | Create a new user                 |
| POST         | `/api/login/`    | Login a user           |
| POST     | `/api/confirm-email/{user_id}/{token}/`    | Confirm user email               |
| POST         | `/api/logout/`      | Logout a user                  |
| POST         | `/api/change-password/` | Change a user password by sending the current password and the new password               |
| POST        | `/api/forgot-passsword/`      | User forgot password               |
| POST     | `/api/new-password/{user_id}/{token}/`    | Change user forgot password               |


## Clone repository 📌
```bash
git clone https://github.com/RaphaelApeh/full-authentication-with-drf.git 
```
