import time

import click
import re
from datetime import datetime, timedelta

def read_log_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def scan_logs_for_opportunity(logs, search_pattern, latest_opportunity_timestamp=None):
    time_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3}"
    search_regex = re.compile(time_pattern + r".*" + search_pattern)
    error_detected = True

    for line in logs.split('\n'):
        match = search_regex.search(line)
        if match:
            last_timestamp = match.group(1)
            if latest_opportunity_timestamp and datetime.strptime(last_timestamp, '%Y-%m-%d %H:%M:%S') > latest_opportunity_timestamp:
                error_detected = False
                print(f"Opportunity found at {last_timestamp}")
                break

    if error_detected:
        raise ValueError("Opportunity not found within 5 minutes interval.")


@click.command()
@click.option('--file_path',
              prompt='Path to bot.log file',
              type=str)
def main(file_path, interval=30):
    print("Starting continuous scan of log file.")
    while True:
        last_timestamp = datetime.now() - timedelta(minutes=5)
        try:
            logs = read_log_file(file_path)
            scan_logs_for_opportunity(logs, r"Opportunity with profit:", last_timestamp)
            print("Everything is OK...")
        except ValueError as e:
            print(e)
            break
        except Exception as ex:
            print(f"An error occurred: {ex}")
            break
        time.sleep(interval)


if __name__ == '__main__':
    main()
