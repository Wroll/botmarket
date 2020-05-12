from botshop.bot.configs import DEBUG
from flask import Flask
from botshop.api.routes import app_rest
from botshop.bot.main import set_webhook, bot, bot_app

app = Flask(__name__)
app.register_blueprint(app_rest)
app.register_blueprint(bot_app)


if __name__ == '__main__':
    if not DEBUG:
        set_webhook()
        print(app.url_map)
        app.run(port=8000)
    else:
        bot.polling()