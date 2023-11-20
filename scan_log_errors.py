import os
import re
import time
from datetime import datetime
from datetime import timedelta

import click


def is_valid_timestamp_dir(name, time_format):
    try:
        datetime.strptime(name, time_format)
        return True
    except ValueError:
        return False


def contains_only_one_specific_word(file_path, target_word, other_words):
    with open(file_path, "r") as file:
        file_contents = file.read()

    # Define a regex pattern with word boundaries for the target word
    target_word_pattern = r"\b" + re.escape(target_word) + r"\b"
    target_word_count = len(re.findall(target_word_pattern, file_contents))
    if target_word_count == 0:
        return False

    # Check for other words
    for word in other_words:
        if word != target_word:
            # Define a regex pattern with word boundaries for each other word
            word_pattern = r"\b" + re.escape(word) + r"\b"
            if re.search(word_pattern, file_contents):
                return False

    return True


def find_latest_log_with_string(
    logs_dir, search_string, non_search_patterns, time_format="%Y%m%d-%H%M%S"
):
    latest_time = None
    latest_folder = None

    for folder_name in os.listdir(logs_dir):
        folder_path = os.path.join(logs_dir, folder_name)
        if os.path.isdir(folder_path) and is_valid_timestamp_dir(
            folder_name, time_format
        ):
            log_file_path = os.path.join(folder_path, "bot.log")
            if os.path.exists(log_file_path):
                is_match = contains_only_one_specific_word(
                    log_file_path, search_string, non_search_patterns
                )
                if is_match:
                    folder_time = datetime.strptime(folder_name, time_format)
                    if not latest_time or folder_time > latest_time:
                        latest_time = folder_time
                        latest_folder = folder_path

    return latest_folder


def read_log_file(file_path):
    with open(file_path, "r") as file:
        return file.read()


def scan_logs_for_opportunity(
    logs, search_pattern, max_minutes, latest_opportunity_timestamp=None
):
    time_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3}"
    search_regex = re.compile(time_pattern + r".*" + search_pattern)
    error_detected = True

    for line in logs.split("\n"):
        match = search_regex.search(line)
        if match:
            last_timestamp = match.group(1)
            if (
                latest_opportunity_timestamp
                and datetime.strptime(last_timestamp, "%Y-%m-%d %H:%M:%S")
                > latest_opportunity_timestamp
            ):
                error_detected = False
                print(f"Opportunity found at {last_timestamp}")
                break

    if error_detected:
        raise ValueError(
            f"Opportunity not found within {max_minutes} minutes interval."
        )


@click.command()
@click.option("--logs_directory", default="logs", type=str)
@click.option("--interval", default=30, type=int)
@click.option("--search_pattern", default="multi_pairwise_all", type=str)
@click.option("--max_minutes", default=10, type=int)
def main(logs_directory, interval, search_pattern, max_minutes):

    all_patterns = [
        "single",
        "multi",
        "triangle",
        "multi_triangle",
        "bancor_v3",
        "b3_two_hop",
        "multi_pairwise_pol",
        "multi_pairwise_bal",
        "multi_pairwise_all",
    ]

    if search_pattern not in all_patterns:
        print(f"Invalid search pattern. Valid patterns are: {all_patterns}")
        raise ValueError("Invalid search pattern.")

    non_search_patterns = [
        f"arb_mode: {pattern}" for pattern in all_patterns if pattern != search_pattern
    ]

    search_pattern = f"arb_mode: {search_pattern}"

    latest_folder = find_latest_log_with_string(
        logs_directory, search_pattern, non_search_patterns
    )

    if latest_folder:
        print(f"Latest folder containing '{search_pattern}': {latest_folder}")
    else:
        print("No folder found with the specified pattern.")
        raise ValueError("No folder found with the specified pattern.")

    print("Starting continuous scan of log file.")
    while True:
        last_timestamp = datetime.now() - timedelta(minutes=max_minutes)
        try:
            logs = read_log_file(f"{latest_folder}/bot.log")
            scan_logs_for_opportunity(
                logs, r"Opportunity with profit:", max_minutes, last_timestamp
            )
            print("Everything is OK...")
        except ValueError as e:
            next_latest_folder = find_latest_log_with_string(
                logs_directory, search_pattern, non_search_patterns
            )
            if next_latest_folder and next_latest_folder != latest_folder:
                print(
                    f"Latest folder containing '{search_pattern}': {next_latest_folder}"
                )
                latest_folder = next_latest_folder
                continue
            else:
                print(e)
                break
        except Exception as ex:
            next_latest_folder = find_latest_log_with_string(
                logs_directory, search_pattern, non_search_patterns
            )
            if next_latest_folder and next_latest_folder != latest_folder:
                print(
                    f"Latest folder containing '{search_pattern}': {next_latest_folder}"
                )
                latest_folder = next_latest_folder
                continue
            else:
                print(f"An error occurred: {ex}")
                break
        time.sleep(interval)


if __name__ == "__main__":
    main()
