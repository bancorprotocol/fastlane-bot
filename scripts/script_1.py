import argparse

def run(option1):
    print(f"Running Script 1 with option1 = {option1}")

def main():
    parser = argparse.ArgumentParser(description='Script 1')
    parser.add_argument('--option1', type=int, help='An option for script 1')
    args = parser.parse_args()
    run(args.option1)

if __name__ == '__main__':
    main()
