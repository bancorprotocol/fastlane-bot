import time

import click
import re
from datetime import datetime, timedelta
import os
import time
import re
from datetime import datetime

def is_valid_timestamp_dir(name, time_format):
    try:
        datetime.strptime(name, time_format)
        return True
    except ValueError:
        return False

def find_latest_log_with_string(logs_dir, search_string, time_format="%Y%m%d-%H%M%S"):
    latest_time = None
    latest_folder = None

    for folder_name in os.listdir(logs_dir):
        folder_path = os.path.join(logs_dir, folder_name)
        if os.path.isdir(folder_path) and is_valid_timestamp_dir(folder_name, time_format):
            log_file_path = os.path.join(folder_path, "bot.log")
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r') as file:
                    if search_string in file.read():
                        folder_time = datetime.strptime(folder_name, time_format)
                        if not latest_time or folder_time > latest_time:
                            latest_time = folder_time
                            latest_folder = folder_path

    return latest_folder



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
@click.option('--logs_directory',
                default="./logs",
              type=str)
@click.option('--interval',
                default=30,
                type=int)
@click.option('--search_pattern',
                default="arb_mode: multi_pairwise_all",
                type=str)
def main(logs_directory, interval, search_pattern):

    latest_folder = find_latest_log_with_string(logs_directory, search_pattern)

    if latest_folder:
        print(f"Latest folder containing '{search_pattern}': {latest_folder}")
    else:
        print("No folder found with the specified pattern.")
        raise ValueError("No folder found with the specified pattern.")

    print("Starting continuous scan of log file.")
    while True:
        last_timestamp = datetime.now() - timedelta(minutes=5)
        try:
            logs = read_log_file(f"{latest_folder}/bot.log")
            scan_logs_for_opportunity(logs, r"Opportunity with profit:", last_timestamp)
            print("Everything is OK...")
        except ValueError as e:
            next_latest_folder = find_latest_log_with_string(logs_directory, search_pattern)
            if next_latest_folder and next_latest_folder != latest_folder:
                print(f"Latest folder containing '{search_pattern}': {next_latest_folder}")
                latest_folder = next_latest_folder
                continue
            else:
                print(e)
                break
        except Exception as ex:
            next_latest_folder = find_latest_log_with_string(logs_directory, search_pattern)
            if next_latest_folder and next_latest_folder != latest_folder:
                print(f"Latest folder containing '{search_pattern}': {next_latest_folder}")
                latest_folder = next_latest_folder
                continue
            else:
                print(f"An error occurred: {ex}")
                break
        time.sleep(interval)


if __name__ == '__main__':
    main()
