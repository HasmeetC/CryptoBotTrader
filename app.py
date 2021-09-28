"""Crypto Interview Assessment Module."""

import os
import schedule
import time

from dotenv import find_dotenv, load_dotenv

from crypto_api import main

# load_dotenv(find_dotenv(raise_error_if_not_found=True))

# You can access the environment variables as such, and any variables from the .env file will be loaded in for you to use.
# os.getenv("DB_HOST")

# Start Here
if __name__ == '__main__':
    main()

schedule.every().hour.do(main())  # uncomment this line for scheduling
