"""Scripts which require the robot ht environment to run."""

import os
import json

import robocorp.tasks

import bot._config as _config


@robocorp.tasks.task
def generate_json_schema():
    """Generate a JSON schema from the bot config."""

    schema = _config.Config.model_json_schema()

    out_path = os.path.join(
        robocorp.tasks.get_output_dir(), "config_schema.json"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(schema, indent=2))
