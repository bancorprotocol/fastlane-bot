import argparse
import importlib

def main():
    parser = argparse.ArgumentParser(description='Run scripts with arguments')
    parser.add_argument('--script', choices=['script_1', 'script_2'], help='Script to run')
    # Define expected arguments for each script here or dynamically handle them
    parser.add_argument('--option1', type=int, help='Option for script 1')
    parser.add_argument('--option2', type=str, help='Option for script 2')
    args = parser.parse_args()

    # Dynamically import the chosen script module
    script_module = importlib.import_module(f'scripts.{args.script}')

    # Call the run function of the imported module with appropriate arguments
    if args.script == 'script_1' and args.option1 is not None:
        script_module.run(args.option1)
    elif args.script == 'script_2' and args.optionA is not None:
        script_module.run(args.optionA)

if __name__ == '__main__':
    main()
