# ACONIO Collection of Robocorp Environments
This repository holds a collection of organization-wide Robocorp environments in the form of `conda.yaml` files. The purpose of this is to reduce the management effort for environment handling and minimize the amount of problems due to environmental inconsistencies in robot projects.

Each `conda.yaml` file within this repository represents a set of dependencies that work for multiple robots in the same "use-case category" (for example, BMD-related robots nearly always require the same dependencies, which are represented by the `bmd/conda.yaml` file within this repository).

To reduce the disk-size occupied by Holotree environments and avoid producing various different environments that all differ slightly but serve the same use-case, it is highly recommended to use a `conda.yaml` file from this repository whenever applicable.

> **Warning:** Changes to any file within this repository should always be discussed throughly internally before being carried out, since this will affect multiple robot projects!

## How to Use This Repository
Once you have your robot-repository in place and it represents a common robot use-case in the ACONIO space (such as a BMD-Robot), you should use this collection of `conda.yaml` files to pick a fitting environment for your robot.

### 1. Add a remote for this repository
Use the following line to add a new remote in your robot-repository, pointing to this repo:
```sh
git remote add -f aconio-robocorp-conda https://github.com/ACONIO/aconio.common.robocorp-environments.git
```

This line has no effect apart from allowing you to reference this repository via the (significantly shorter) remote name in further subtree commands.

### 2. Add a subtree for this repository
The following line adds this repository to your robot-repository in form of a subtree:
```sh
git subtree add --prefix shared/conda aconio-robocorp-conda main --squash
```

### 3. Use the new `conda.yaml`
Now, you have to tell your robot to use the correct `conda.yaml` file. In you `robot.yaml`, you should have a property called `condaConfigFile` which lets you specify the location of the environment file you want to use. Change this this property to the following:

```yaml
condaConfigFile: shared/conda/<your-environment>/conda.yaml
```

> **Note:** Replace the `<your-environment>` with the folder name in this repository that contains the correct `conda.yaml` for your use-case. For example, in order to use the `conda.yaml` for BMD robots, use `bmd`. The full value would then be `shared/conda/bmd/conda.yaml`

### 4. Pull New Updates
Whenever this repository is updated, robot-repositories using an organization-wide `conda.yaml` file should be updated as soon as possible to maintain consistent environments.

This can be achieved using the following subtree command:
```sh
git subtree pull --prefix shared/conda aconio-robocorp-conda main --squash
```

## How To Contribute
When there's a new use-case that should be covered or an existing `conda.yaml` that should be updated, the following command can be used to verify if the specified dependencies in a `conda.yaml` would work without causing any dependency-collision:
```sh
rcc holotree variables <folder-name>/conda.yaml
```