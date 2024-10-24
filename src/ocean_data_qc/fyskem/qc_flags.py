from dataclasses import dataclass, field
from typing import Sequence

from ocean_data_qc.fyskem.qc_flag import QcFlag
from ocean_data_qc.fyskem.qc_flag_tuple import QcField, QcFlagTuple


@dataclass
class QcFlags:
    _incoming: QcFlag = QcFlag.NO_QC_PERFORMED
    _automatic: QcFlagTuple = field(
        default_factory=lambda: QcFlagTuple((QcFlag.NO_QC_PERFORMED,) * len(QcField))
    )
    _manual: QcFlag = QcFlag.NO_QC_PERFORMED
    _total: QcFlag = QcFlag.NO_QC_PERFORMED

    def __post_init__(self):
        self._incoming = self._incoming or QcFlag.NO_QC_PERFORMED
        self._automatic = self._automatic or QcFlagTuple(
            (QcFlag.NO_QC_PERFORMED,) * len(QcField)
        )
        self._manual = self._manual or QcFlag.NO_QC_PERFORMED
        self._update_total()

    def get_field(self, field_name: QcField):
        return self.automatic[field_name]

    @property
    def incoming(self) -> QcFlag:
        return self._incoming

    @incoming.setter
    def incoming(self, value: QcFlag):
        self._incoming = value
        self._update_total()

    @property
    def automatic(self) -> QcFlagTuple:
        return self._automatic

    @automatic.setter
    def automatic(self, value: Sequence):
        self._automatic = QcFlagTuple(value)
        self._update_total()

    @property
    def manual(self) -> QcFlag:
        return self._manual

    @manual.setter
    def manual(self, value: QcFlag):
        self._manual = value
        self._update_total()

    @property
    def total(self) -> QcFlag:
        return self._total

    def _update_total(self):
        # Manual QC should always be used if it is performed.
        # If not, use the worst flag.
        self._total = self.manual or min(
            [flag for flag in (self.incoming,) + tuple(self.automatic)],
            key=QcFlag.key_function,
            default=QcFlag.NO_QC_PERFORMED,
        )

    def __str__(self):
        return (
            f"{self.incoming.value}_"
            f"{''.join(str(flag.value) for flag in self.automatic)}_"
            f"{self.manual.value}_"
            f"{self.total.value}"
        )

    @classmethod
    def from_string(cls, value: str):
        if not value:
            return cls()

        incoming, automatic, manual, total = value.split("_")
        incoming = QcFlag(int(incoming))
        automatic = QcFlagTuple(QcFlag(flag) for flag in map(int, automatic))
        manual = QcFlag(int(manual))

        return cls(incoming, automatic, manual)
