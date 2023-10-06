# <Robot_Name>

## First Steps (Important!)
In order for this template to work properly, a few initial setup steps have to be performed.

**TODO:** After you've completed all setup steps, you may delete this section from the README.

### 1. VS-Code Settings
Add the according VS-Code settings to your project from our [VS-Code Settings Repo](https://github.com/ACONIO/aconio.common.vscode-settings/tree/main).

### 2. Download Dependencies
When using this template, there are a few dependencies that must be pulled in order for the template code to work properly.

#### 2.1. Utils Library Subtree
Get the newest version of the utils library which is required for the video recording and some Outlook functionality:

```bash
git remote add -f aconio-library-utils https://github.com/ACONIO/aconio.libraries.robocorp.utils.git
git subtree add --prefix shared/utils aconio-library-utils main --squash
```

#### 2.2. BMD Library Subtree
If the project requires BMD functionality, be sure to also pull the BMD library:

```bash
git remote add -f aconio-library-bmd https://github.com/ACONIO/aconio.libraries.robocorp.bmd.git
git subtree add --prefix shared/bmd aconio-library-bmd main --squash
```

#### 2.3. Using The Organization-Wide `conda.yaml`
If one of the organization-wide `conda.yaml` environments from the [ACONIO Robocorp-Environments Repository](https://github.com/ACONIO/aconio.common.robocorp-environments) fits your process requirements, make sure to also pull this library and use the correct `conda.yaml` file:

```bash
git remote add -f aconio-robocorp-conda https://github.com/ACONIO/aconio.common.robocorp-environments.git
git subtree add --prefix shared/conda aconio-robocorp-conda main --squash
```

Once the new `conda.yaml` file is pulled, update your `robot.yaml` file by specifying the correct environment configuration file:
```yaml
condaConfigFile: shared/conda/<your-environment>/conda.yaml
```

> **Note:** Replace the <your-environment> with the folder name in this repository that contains the correct conda.yaml for your use-case.
> 
> For example, in order to use the `conda.yaml` for BMD robots, use `bmd`. The full value would then be `shared/conda/bmd/conda.yaml`

Now, you don't need the old `conda.yaml` file anymore:
```bash
# Remove the default `conda.yaml` file from the repo
rm conda.yaml
```

### 3. Uncomment Functionality in `bot/common.py`
The `bot/common.py` file holds a lot of standard functionality that is commented-out because it would result in errors without the above library imports in place.

Thus, after the required libraries have been imported, open `bot/common.py`, search for `TODO` and uncomment everything you need for the robot.

### 4. Insert Process Name
There are a few parts in this template repository where the robot name, or name of the repository must be inserted.

Here's a list of places where changes are required:
1. In `README.md` - replace the title `<Robot_Name>` with the name of the project/robot
2. In `config.py` - replace the `<repo_name>` with the repository name
3. In the `devdata/test-robot-data-dir-template` folder, there are two sub-folders (`input_data` and `temp_files`) that each contain a folder, which should be named after the repository

### 5. Remove Template Instructions
Once you've completed all steps above, you can remove this section from the `README.md`.

---
## Robot Logic
The following is an illustration of the robot workflow and how the individual components interact with each other.

![Robot Logic](docs/replace_me.png)

### Components
TODO: exmplain repo components

## Development
This section holds useful commands for the development process with this repository.

### Run the process in dev environment
The following uses the `devTasks:` instead of `tasks:` section in `robot.yaml`:
```sh
rcc run -e "devdata/env.json" --dev
```

### Run the generic test case
The following executes the generic test case defined in `test.robot`:
```sh
rcc run -e "devdata/env.json" --dev --task "Generic Test"
```

### Running Python Scripts
When Python is not installed on the target machine, you can navigate to the Robocorp VS Code extension window and click `Open Robot Terminal`. Within that console you can execute Python commands without having Python installed on the target machine.

### Git Subtree
For working with Git Subtree, refer to our internal documentation (Obsidian vault at `Technical\Git Subtree Cheatsheet`).

You can also use the subtree scripts provided in the `scripts` folder to work with multiple subtree repos at once:

- Add new Git Subtree Project: `python scripts/add_subtree_library.py <repository_url>`
- Pull upstream changes from a Git Subtree project: `python scripts/update_subtrees.py`
- Push changes to a subtree project back upstream: `python scripts/push_subtrees.py`

### Update Root Robot Locators (Workaround)
Currently, it is not possible to include libraries that use their own locators, because if a keyword of this library is called and this keyword references a locator, the execution directory is always the robot root directory, which means that if the locator is not also present in the robot root directory `locators.json`, but only in the `locators.json` of the library, the required locator will not be found.

Thus, we need to use an *"udpate script"*, that copies all locators in the `locators.json` from all included libraries, as well as all files within the `.images` folders from all included libraries, to the respective `.images` folder and `locators.json` file of the main project.

To perform this, execute the following command from the robot root directory:

```sh
python scripts/update_locators.py
```

> **Note:** If the library is update with a new locator, the script has to be executed again!