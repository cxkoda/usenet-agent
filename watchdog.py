from main import main
from UsenetAgent.ConfigLoader import ConfigLoader

import schedule
import time


def job():
    main()


if __name__ == "__main__":
    cfg = ConfigLoader.load()
    schedule.every().day.at(cfg['agent']['dailyChecktime']).do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)
