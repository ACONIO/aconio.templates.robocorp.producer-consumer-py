import logging
import json
import os
import shutil

# Directory that contains all libraries
libs_directory = "./shared"

# Robot root directory
robot_root_dir = "."

# Get all locators of the root project
with open("locators.json") as root_locators_file:
    root_locators_json = json.load(root_locators_file)


# Iterate through all libraries in the "shared" folder
for curr_lib in os.listdir(libs_directory):
    try:
        # Get all locators of the library
        with open(f"{libs_directory}/{curr_lib}/locators.json") as lib_locators_file:
            lib_locators_json = json.load(lib_locators_file)

            # Append all locators of this library to the locators file of the root project
            root_locators_json.update(lib_locators_json)
    except FileNotFoundError:
        logging.warning(
            f"The library '{curr_lib}' contains no locators! Skipping locator copy for this library...")

    try:
        # Copy all files from the ".images" folder of the library to the ".images" folder of the root project
        shutil.copytree(f"{libs_directory}/{curr_lib}/.images/",
                        f"{robot_root_dir}/.images", dirs_exist_ok=True)
    except FileNotFoundError:
        logging.warning(
            f"The library '{curr_lib}' contains no image files! Skipping image copy for this library...")

with open(f"{robot_root_dir}/locators.json", "w") as outfile:
    json.dump(root_locators_json, outfile, sort_keys=True, indent=4)
