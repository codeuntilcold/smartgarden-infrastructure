class ConfigClass(object):

    SECRET_KEY = "a_very_big_secret"
    AIO_FEED_IDS = ["bbc-test-json", "bbc-led"]
    AIO_USERNAME = "toilaaihcmut"
    AIO_KEY = "aio_eVKn92mKQRDZCyoUDXowg5meHC4n"

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quickstart_app.sqlite'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-User settings
    USER_APP_NAME = "Super Quick Flask App"
    USER_ENABLE_EMAIL = False
    USER_ENABLE_USERNAME = True
    USER_REQUIRE_RETYPE_PASSWORD = True
    
    # USER_ENABLE_CHANGE_PASSWORD = True
    # USER_ENABLE_FORGOT_PASSWORD = True
    # USER_ENABLE_REGISTER = True
    # USER_ENABLE_REMEMBER_ME = True
    # USER_ALLOW_LOGIN_WITHOUT_CONFIRMED_EMAIL = True

    # USER_CHANGE_PASSWORD_URL = '/user/change-password'
    # USER_CHANGE_USERNAME_URL = '/user/change-username'
    # USER_CONFIRM_EMAIL_URL = '/user/confirm-email/<token>'
    # USER_EDIT_USER_PROFILE_URL = '/user/edit_user_profile'
    # USER_EMAIL_ACTION_URL = '/user/email/<id>/<action>'
    # USER_FORGOT_PASSWORD_URL = '/user/forgot-password'
    # USER_INVITE_USER_URL = '/user/invite'
    # USER_LOGIN_URL = '/user/sign-in'
    # USER_LOGOUT_URL = '/user/sign-out'
    # USER_MANAGE_EMAILS_URL = '/user/manage-emails'
    # USER_REGISTER_URL = '/user/register'
    # USER_RESEND_EMAIL_CONFIRMATION_URL = '/user/resend-email-confirmation'
    # USER_RESET_PASSWORD_URL = '/user/reset-password/<token>'

    # USER_LOGIN_TEMPLATE = 'flask_user/login.html'
    # USER_REGISTER_TEMPLATE = 'flask_user/register.html'