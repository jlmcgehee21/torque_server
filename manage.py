import app
from app.config import DefaultConfig

application = app.create_app(config=DefaultConfig)

if __name__ == "__main__":
    application.run("0.0.0.0", threaded=True, debug=True)
