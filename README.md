# <robot_name>
[![Static Badge](https://img.shields.io/badge/Solution_Design-black?logo=eraser)](<link_to_solution_design>)

<robot_description>

## Notes
Important information about the template project.

### ⚙️ Process Config
The configuration in `bot/_config.py` is intended for simple processes which are to be configured via Robocorp Control Room environment variables.

For more complex processes requiring vast configuration options, refer to [The Aconio VZ-Versand Bot](https://github.com/ACONIO/aconio.products.bmd.evz-kvz) where we use a YAML file stored in Azure to configure the process.

### 🔐 Encryption
If encryption of Robocorp Control Room **Secrets** or **Assets** is required, refer to the [IWTH JA Extentsion Bot](https://github.com/ACONIO/iwth.accounting.ja-extension), where we use [Fernet](https://cryptography.io/en/latest/fernet/) to encrypt & decrypt secrets with a 🔑 key residing on the client's infrastructure.

## First Steps
In order for this template to work properly, a few initial setup steps have to be performed.

> [!IMPORTANT]
> After you've completed all setup steps, you may delete the **Notes** and **First Steps** sections from `README.md`.

### 1. Robot Documentation
Find and replace the following placeholders in `README.md`:
- `<robot_name>`
- `<robot_description>`
- `<link_to_solution_design>` *(If available, otherwise you may remove the whole link)*

### 2. VS-Code Settings
Add the according VS-Code settings to your project from our [VS-Code Settings Repo](https://github.com/ACONIO/aconio.common.vscode-settings/tree/main).

### 3. Update `aconio` Library
If the `aconio` library version of the template respository is not the newest version, use the `scripts/install_aconio.py` script to update the `aconio` library to the latest version.

```bash
python scripts/install_aconio.py <git_tag> <github_token>
```

### 4. Resolve `TODO`'s
Some values and directives in the template need to be adapted to the specific needs of your project. These locations are marked with `TODO` in the code.

Search for the string `TODO` in your project and resolve them to prepare the template for your project.

### 5. Remove Readme Instructions
Once you've completed all steps above, you can remove this section from the `README.md`.

## Development
This section holds useful information & commands for the development process.

### Testing Control Room Assets Locally
Sometimes it is necessary to test functionality involving Robocorp Control Room **Assets**. Unfortunately Robocorp does not offer a "local-testing" approach for CR assets similar to what is possible with CR **Vault** secrets (local `vault.json` file). However, it is possible to link `rcc` to an actual Control Room workspace.

Use the following code to retrieve an access token for your Robocorp workspace:
```bash
# Retrieve a CR token of a specific workspace, valid for 90 minutes
rcc cloud authorize -w <workspace-id> -m 90
```

Now, add the following three values to your `env.json` file:
```json
{
  "RC_API_URL_V1": "https://api.eu1.robocorp.com/v1/",
  "RC_WORKSPACE_ID": "<workspace-id>",
  "RC_API_TOKEN_V1": "<workspace-token>"
}
```

This will establish a connection to Robocorp Control Room and therefore provide the process with access to CR assets.

> [!IMPORTANT]
> To make this process more convenient, you may use the `scripts/load_cr_token.py` Python script, which will automatically take the `<workspace-id>` from the `RC_WORKSPACE_ID` variable of the passed `env.json` file, generate a token for it, and set the token to the `RC_API_TOKEN_V1` variable.
> Example:
> ```bash
> python scripts/load_cr_token.py devdata/env-consumer.json
> ```

### Linting

For linting we use Visual Studio Code's [pylint extension](https://marketplace.visualstudio.com/items?itemName=ms-python.pylint) with Google's pylintrc file. Make sure to copy the `settings.json` file from our [VS-Code Settings Repo](https://github.com/ACONIO/aconio.common.vscode-settings/tree/main) in your `.vscode` folder. In rare cases it is necessary to restart the linting server in vscode: `CMD+SHIFT+P > "Pylint: Restart Server" > ENTER`

We try to adhere to Google's Python [styleguide](https://google.github.io/styleguide/pyguide.html).