# pylint: skip-file
# Performs an `rcc cloud authorize` command, grabbing the CR workspace ID from the
# given JSON file and then setting the generated token to this JSON file.
#
# Usage (from project root):
# python scripts/load_cr_token.py devdata/env-producer.json
#
# This will take the `RC_WORKSPACE_ID` from `devdata/env-producer.json` and perform an
# `rcc cloud authorize` with this workspace ID. Then, it saves the generated token to
# the `RC_API_TOKEN_V1` key in `devdata/env-producer.json`.

import sys
import json
import subprocess

with open(sys.argv[1]) as f:
    data = json.load(f)

rc_workspace_id = data["RC_WORKSPACE_ID"]
print(f"Workspace ID: {rc_workspace_id}")

output = subprocess.getoutput(
    f"rcc cloud authorize -w {rc_workspace_id} -m 120 --silent"
)
cr_token = json.loads(output)["token"]
print(f"Generated token (valid for 120 minutes): {cr_token}")

data["RC_API_TOKEN_V1"] = cr_token
with open(sys.argv[1], "w") as f:
    json.dump(data, f)
