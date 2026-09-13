"""Simple module to manage project-wide delay times.

The user can set a global delay factor using `delay().set_factor(<factor>)`
and then use the `delay().get(<wait_time>)` method to retrieve delay times
multiplied by this factor.

Hence, different base wait times can be set depending on the action, while
the global delay factor still enables consistent scaling across the project.

Example:
```python
import aconio.delay as delay
import aconio.bmd.ui as bmd_ui
import aconio.bmd.cli.services as bmd_services

# Set a global wait time modifier (usually based on bot configuration)
delay.delay().set_factor(1.5)

# The value passed to `get()` will be multiplied by the configured
# delay factor. In this case, the timeout will be 6 (4 * 1.5)
bmd_ui.open_application(timeout=delay.delay().get(4))

# Service imports can take longer, so we choose a higher base wait time.
# In this case, the timeout will be 12 (8 * 1.5)
bmd_services.import_services(
    services=[...],
    timeout=int(delay.delay().get(8)),
    use_log_file=False,
)

```
"""

import functools


class DelayManager:
    """Multiply given delays by a configured factor."""

    def __init__(self, factor: float = 1.0) -> None:
        self._factor = factor

    def set_factor(self, factor: float) -> None:
        self._factor = factor

    def get(self, wait_time: float) -> float:
        """Return the given delay time multiplied by the configured factor."""
        return wait_time * self._factor


@functools.lru_cache
def delay() -> DelayManager:
    return DelayManager()
