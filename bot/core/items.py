import dataclasses
import dataclasses_json as dj


@dataclasses.dataclass
class Item(dj.DataClassJsonMixin):
    pass


@dataclasses.dataclass
class ReporterItem(dj.DataClassJsonMixin):
    """ Represents a work item consumed by the reporter process. """

    failed_wi_id: str
    failed_wi_code: str
    failed_wi_payload: Item
