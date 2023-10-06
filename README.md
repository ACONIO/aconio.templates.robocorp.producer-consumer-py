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

### 4. Copy Templates
The `devdata` directory holds a template folder for the `robot-data-dir`, `env.json`, and `vault.json`.

This is because those files/directories are excluded from the repository in the `.gitignore`, due to them possibly containing sensitive data. Via the template files/directory, a developer easily has a template in place that can be copied and filled with the required data.

Thus, please **don't remove** the template files/directories, but use them to configure your dev environment.

> When copying the `env-template.json` and creating the `env.json`, make sure to adapt the filepath of `ROBOT_DATA_DIR`.

### 5. Remove Readme Instructions
Once you've completed all steps above, you can remove this section from the `README.md`.

---
## Description & Robot Logic
<TODO: Explain robot>

## Repository Components & Project Structure
The following offers a short explanation of each component (files & folders) contained within this robot project.

### `robot.yaml`
This file represents the heart of the robot. It defines which tasks the bot contains, what environment it uses, and many more configuration options. See [the official Robocorp documentation](https://robocorp.com/docs/setup/robot-yaml-format) for more info.

As a best practice, the required `rcc` command to run a certain task in the development environment will always be mentioned as a comment above the actual task definition. In doing so, the developer can easily copy the command when testing certain functionlity of the robot locally.

**Example:**
```yaml
tasks:
    # rcc run -e "devdata/env.json" --task "Producer"
    Producer:
        shell: python -m robocorp.tasks run tasks.py -t producer
```

### `conda.yaml`
Here, the dependencies of the project are defined. See our [ACONIO Robocorp-Environments Repository](https://github.com/ACONIO/aconio.common.robocorp-environments) for a set of organization-wide `conda.yaml` files, which are recommended to use in order to maintain consistency over our robot projects, and keep Holotree disk usage low.

See [the official Robocorp documentation on environment control](https://robocorp.com/docs/setup/environment-control) for more info.

### `tasks.py`
Within this file, the most high-level logic of the robot is defined. It is solely responsible for starting the individual robot tasks (e.g. `Consumer` and `Producer`), handling possible errors, and managing work items (e.g. creating work items when it's a **Producer** taks, or consuming work items when it's a **Consumer** task).

As a best practice, the individual task files (e.g. `bot/producer.py` or `bot/consumer.py`) should always offer a `run()` function, which should be the only taks-specific function invoked within the `tasks.py` file.

### `tests.py`
The `tests.py` file holds a set of common test-cases that are required multiple times during robot development. This not only entails unit-tests, but also tasks for integration testing multiple logically coherent steps.

For each test case in the `tests.py` file, there's also a corresponding entry in the `devTasks` section of the `robot.yaml` file.

**Example:**
```yaml
devTasks:
  # rcc run -e "devdata/env.json" --dev --task "Generic Test"
  Generic Test:
    shell: python -m robocorp.tasks run tests.py -t generic_test
```

#### The Generic Test
The `tests.py` file always contains one `generic_test` function. The purpose of this function is to provide a way for the developer to easily test small bits of code without running the whole producer taks, or creating a separate test case only for a minor test.


### `config.py`
Here, all configuration options of the robot are contained in the `Config` class, which loads the configuration from environment variables, or sets a default vaule if available. Using this file, a developer can quickly inspect all available configuration options of the robot.

### `locators.json`
This file holds a set of locators (mainly image locators) used by the `RPA.Desktop` library throughout the robot. The locators defined in the `locators.json` file can be referenced from the code by using the `alias` directive (see the [RPA.Desktop documentation](https://robocorp.com/docs/libraries/rpa-framework/rpa-desktop) for more info).

[Here](https://github.com/robocorp/example-desktop-image-template-matching/blob/master/locators.json) is an example for a proper `locators.json` file.

> See section [Update Root Robot Locators (Workaround)](#update-root-robot-locators-workaround) for a guide on how to use existing locators from subtree libraries.

### The `bot` Directory
This directory holds the main functionality of all robot tasks. For each taks in the robot, a `.py` file should be held within this directory. For example, if the project defines a `Producer` and a `Consumer` task, the `bot directory` should hold a `producer.py` and a `consumer.py` that hold the main functionality of the tasks.

As a best pratice, each task-specific file (e.g. `producer.py`) should provide a `run()` function which is invoked by the task function in `tasks.py` and hols the high-level logic of this specific task.

In addition to the task-specific files, the `bot` directory also offers a `common.py` file, which holds functions that are used across multiple tasks (e.g. `setup()` and `teardown()`).

### The `devdata` Directory
Here, all files relevant for the development process are held. For more information about the `env.json` and `vault.json` see [environment variables](https://robocorp.com/docs/development-guide/variables-and-secrets/configuring-robots-using-environment-variables) and [local vault file](https://robocorp.com/docs/development-guide/variables-and-secrets/vault#local-vault-file-an-alternative-way-for-storing-local-secrets) from the official Robocorp documentation.

#### The `robot-data-dir` Directory
Since most robots require some input data in the form of files, and a way to temporarily store data, each robot offers a `ROBOT_DATA_DIR` environment variable, that defines the place where robot data is stored.

> As a best practice, the `ROBOT_DATA_DIR` in production environments should be `C:\Users\<prod-username>\Documents\robot_data\<repo-name>`.

However, we also want to have this directory in our repository for development purposes, so we can test the functionality of the robot. Thus, we have the `robot-data-dir` directory, holding an `input` and a `temp` directory for obtaining fixed input data or storing temporary files during the development process.

> So the `robot-data-dir` directory basically represents the `ROBOT_DATA_DIR` of production environments.

#### The Template Files
The `devdata` directory also holds templates for all `env.json`, and `vault.json` files required by the process, as well as a template directory for the `robot-data-dir` folder.

This is because those files/directories are excluded from the repository in the `.gitignore`, due to them possibly containing sensitive data. Via the template files/directory, a developer easily has a template in place that can be copied and filled with the required data.

Thus, please **don't remove** the template files/directories, but use them to configure your dev environment.

## Development
This section holds useful information & commands for the development process.

### Running Python Scripts
When Python is not installed on the target machine, you can navigate to the Robocorp VS Code extension window and click `Open Robot Terminal`. Within that console you can execute Python commands without having Python installed on the target machine.

### Update Root Robot Locators (Workaround)
Currently, it is not possible to include libraries that use their own locators, because if a keyword of this library is called and this keyword references a locator, the execution directory is always the robot root directory, which means that if the locator is not also present in the robot root directory `locators.json`, but only in the `locators.json` of the library, the required locator will not be found.

Thus, we need to use a script that copies all locators in the `locators.json` from all included libraries, as well as all files within the `.images` folders from all included libraries, to the respective `.images` folder and `locators.json` file of the main project.

To perform this, execute the following command from the robot root directory:

```bash
python scripts/update_locators.py
```

> **Note:** If the library is updated with a new locator, the script has to be executed again!