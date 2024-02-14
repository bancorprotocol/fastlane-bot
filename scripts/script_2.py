import argparse

def run(option2):
    print(f"Running Script 2 with option2 = '{option2}'")

def main():
    parser = argparse.ArgumentParser(description='Script 2')
    parser.add_argument('--option2', type=str, help='An option for script 2')
    args = parser.parse_args()
    run(args.option2)

if __name__ == '__main__':
    main()
