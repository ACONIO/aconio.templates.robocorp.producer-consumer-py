"""Handle edge-case notifications in processes.

### Example Jinja2 Template

```html
<!-- template.j2 -->
<p>Warning, a problem occured during the process run!</p>

{% if alert_type == AlertType.MINOR_ALERT %}
    <p>I hit my toe!</p>
{% elif alert_type == AlertType.MAJOR_ALERT %}
    <p>He wiped out 50% of all living creatures!</p>
{% endif %}
```

### Example Usage
```python
from aconio import alerts, outlook

outlook.start()

alerts.configure(
    jinja_env=j2.Environment(
        loader=j2.FileSystemLoader("./templates"),
        undefined=j2.StrictUndefined,
    )
    alert_file="template.j2",
    alert_types=["MINOR_ALERT", "MAJOR_ALERT"]
)

# Note that we can access the MAJOR_ALERT as an enum, which was previously
# passed to the module configuration as a list of enum values
alerts.raise_email(
    to="patrick.krukenfellner@aconio.net",
    subject="Some exception case occured!",
    attachments=["screenshot.png"],
    alert_type=alerts.alert_types().MAJOR_ALERT,
    client_id="200000" # Additional arguments passed to the jinja template
)
```
"""

import jinja2 as j2

from enum import Enum
from functools import lru_cache

from aconio import outlook
from aconio.alerts import _config


@lru_cache  # Always return the same instance.
def config() -> _config.Config:
    return _config.Config()


def configure(
    jinja_env: j2.Environment,
    alert_file: str,
    alert_types: list[str],  # pylint: disable=redefined-outer-name
) -> None:
    """Set the module configuration.

    Args:
        jinja_env:
            A jinja2 environment.

        alert_file:
            Path to the jinja template file.

        alert_types:
            List of possible alert types which should be used in the jinja
            template to decide an appropriate alert text.
    """
    config().jinja_env = jinja_env
    config().alert_file = alert_file
    config().alert_types = alert_types


def alert_types() -> Enum:
    """Return the `AlertTypes` enum initially configured by the module user."""
    return config().alert_types


def raise_email(
    to: str | list[str],
    subject: str,
    alert_type: Enum,
    attachments: list[str] = None,
    draft: bool = False,
    **kwargs,
):
    """Send an alert e-mail to `recipient`.

    Note that this function requires that the Outlook application is running
    (see `aconio.outlook.start()`).

    Args:
        to:
            String or list of recipient e-mail addresses.

        subject:
            E-Mail subject.

        attachments:
            List of filepaths to documents that will be attached to the email.

        alert_type:
            One of the alert types initially configured by the module user.

        draft:
            Set to `True` if the email should be stored in the 'Drafts' folder.

    Additional arguments passed via `kwargs` will be forwarded to the jinja
    template.

    Raises:
        RuntimeError: If Outlook is not running.
    """

    if not outlook.is_open():
        raise RuntimeError(
            "Outlook application not running. "
            "Did you use aconio.outlook.start()?"
        )

    template = config().jinja_env.get_template(config().alert_file)

    # Pass the AlertType enum
    template.globals["AlertType"] = type(alert_type)

    outlook.send_email(
        subject=subject,
        body=template.render(alert_type=alert_type, **kwargs),
        html_body=True,
        to=to,
        attachments=attachments,
        draft=draft,
    )
