import argparse
import os


def cli():
    parser = argparse.ArgumentParser(
        prog='add_subtree.py',
        description='Creates a remote for a subtree library and adds it.'
    )

    parser.add_argument('remote', help='The URL of the subtree repository to include.')
    parser.add_argument('name', help='The name of the subtree folder created in your project.')

    return parser.parse_args()


args = cli()

REMOTE_URL = args.remote
REMOTE_NAME = f'subtree-{args.name}'  # Subtree remotes are always prefixed with 'subtree'
SUBTREE_FOLDER = f'shared/{args.name}'  # Subtrees are always stored in the 'shared' folder

# Generate the commands
cmd_remote_add = f"git remote add -f {REMOTE_NAME} {REMOTE_URL}"
cmd_subtree_add = f"git subtree add --prefix {SUBTREE_FOLDER} {REMOTE_NAME} main --squash"

# Ask user if commands are correct and if they should be executed
print("Based on your parameters, the following two commands will be executed:", '\n')
print('\t', cmd_remote_add)
print('\t', cmd_subtree_add, '\n')
print("Proceed? (Type in 'y' to continue, or anything else to stop)")

if input().lower() == 'y':
    print(f"Adding subtree library '{REMOTE_NAME}' in folder '{SUBTREE_FOLDER}'...")
    os.system(cmd_remote_add)
    os.system(cmd_subtree_add)
else:
    print("Script stopped.")
