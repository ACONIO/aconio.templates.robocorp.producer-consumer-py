"""Scripts which require the robot ht environment to run."""

import os
import json

from robocorp import tasks

from bot import _config


@tasks.task
def generate_json_schema():
    """Generate a JSON schema from the bot config."""

    schema = _config.Config.model_json_schema()

    out_path = os.path.join(tasks.get_output_dir(), "config_schema.json")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(schema, indent=2))
