"""Count processed work items for billing purposes."""

import json
import requests

from typing import List, Optional
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin

from robocorp import storage


class ItemCounter:
    """Count processed work items for billing purposes.

    A wrapper class for a Robocorp Control Room asset, used to count processed
    work items for billing purposes.

    The asset holds a list of billing periods, where each billing period has a
    start date, end date, and a count of processed items.
    The start date represents the first date where an item has been processed
    and the end date is the start date plus one year, since each billing period
    is exactly one year.

    The asset is used to determine how many items a bot has already processed,
    which is necessary to check if a client is still within the limits of his
    automation package.

    ### Notification Mechanism
    The asset also implements a notification mechanism, which can be utilized
    by specifying the `notification_endpoint` URL. If this URL is set, the
    process will send a POST request to this endpoint upon two certain events:
    1. A period is about to end (you can use the `period_ending_msg_weeks`
    property to specify how many weeks before the period end this notification
    is sent)

    2. The `max_counter` is exceeded.

    Each period tracks if one of the above notifications has already been sent
    for this period with the `counter_exceeded_msg_sent` and
    `period_ending_msg_sent` properties. Thus, no notification is sent twice.

    ### Example Asset

    ```json
    {
        "process_name": "EVZ/KVZ Versand",
        "client_name": "My Client",
        "max_counter": 500,
        "notification_endpoint": "https://hooks.zapier.com/hooks/catch/my/ep/",
        "period_ending_msg_weeks": 3,
        "periods": [
            {
                "start_date": "01.02.2024",
                "end_date": "01.02.2025",
                "count": 50,
                "counter_exceeded_msg_sent": "False",
                "period_ending_msg_sent": "False"
            }
        ]
    }
    ```
    """

    def __init__(self, asset_name: str):
        self._asset_name = asset_name

    def increment(self):
        """Increment the counter by 1.

        If no billing periods have been created in the asset yet, a new period
        will be created automatically. Also, if the current date has surpassed
        the end date of the latest billing period, a new period will be created
        as well.
        """
        counter = _Counter.from_dict(storage.get_json(self._asset_name))
        counter.increment()

        storage.set_json(self._asset_name, counter.to_dict())


@dataclass
class _Period(DataClassJsonMixin):
    """Represent a period with start and end date and a count of items."""

    start_date: str
    end_date: str
    count: int

    # Notifications
    counter_exceeded_msg_sent: Optional[bool] = False
    period_ending_msg_sent: Optional[bool] = False

    def increment(self):
        """Increment the counter by 1."""
        self.count += 1
        return self

    @property
    def start(self) -> date:
        return datetime.strptime(self.start_date, "%d.%m.%Y").date()

    @property
    def end(self) -> date:
        return datetime.strptime(self.end_date, "%d.%m.%Y").date()

    def is_current(self, today: date = date.today()) -> bool:
        """Checks whether the current date is in this period."""
        return today >= self.start and today <= self.end


@dataclass
class _Counter(DataClassJsonMixin):
    """Count work items for process and client."""

    process_name: str
    client_name: str
    max_counter: int
    periods: List[_Period]

    # Notifications
    notification_endpoint: Optional[str] = ""
    period_ending_msg_weeks: Optional[int] = 3

    def increment(self):
        """
        Increment the counter of the current period by 1.

        If no billing periods have been created yet, a new period will be
        added automatically.

        If the current date has surpassed the end date of the latest
        billing period, a new period will be created.

        Notifications:
            If the period ends within the amount of weeks given in
            `period_ending_msg_weeks`, a notification will be sent
            to the `notification_endpoint`.

            If the counter of the updated period exceeds `max_counter`,
            a notification will be sent to the `notification_endpoint`
        """
        curr_period = self.__get_curr_period(self.periods)
        if curr_period is None:
            curr_period = self.__create_period()
            self.periods.append(curr_period.increment())
        else:
            curr_period.increment()

        if (
            curr_period.count > self.max_counter
            and not curr_period.counter_exceeded_msg_sent
        ):
            self.__send_notification(curr_period, "MAX_COUNTER_EXCEEDED")
            curr_period.counter_exceeded_msg_sent = True

        if (
            self.__period_is_ending(curr_period)
            and not curr_period.period_ending_msg_sent
        ):
            self.__send_notification(curr_period, "PERIOD_ABOUT_TO_END")
            curr_period.period_ending_msg_sent = True

    def __create_period(self, today: date = date.today()) -> _Period:
        """Create a new period based on the given date (default = today)."""
        return _Period(
            start_date=today.strftime("%d.%m.%Y"),
            end_date=(today + relativedelta(years=1)).strftime("%d.%m.%Y"),
            count=0,
        )

    def __get_curr_period(self, periods: List[_Period]) -> _Period:
        """Return the index of the current period from a list of periods."""
        return next((p for p in periods if p.is_current()), None)

    def __period_is_ending(self, period: _Period) -> bool:
        """Checks if the period ends in the amount of weeks given in
        `period_ending_msg_weeks`.
        """
        return (
            period.end - date.today()
        ).days < self.period_ending_msg_weeks * 7

    def __send_notification(self, period: _Period, msg: str):
        """Sends a POST request to the given notification endpoint."""
        response = requests.post(
            self.notification_endpoint,
            data={
                "process_name": self.process_name,
                "client_name": self.client_name,
                "max_counter:": self.max_counter,
                "period": {
                    "start_date": period.start_date,
                    "end_date": period.end_date,
                },
                "message": msg,
            },
            timeout=5,
        )

        if json.loads(response.text).get("status") != "success":
            raise RuntimeError(
                f'Failed to notify endpoint "{self.notification_endpoint}"'
            )
