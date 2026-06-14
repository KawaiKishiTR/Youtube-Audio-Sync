from dotenv import load_dotenv
load_dotenv()

from app.main import main as app_main
from app.database.database import init_db



def main():
    init_db()
    app_main()


if __name__ == "__main__":
    main()
