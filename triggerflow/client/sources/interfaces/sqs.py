from typing import Optional
from ..model import EventSource


class SQSEventSource(EventSource):
    def __init__(self,
                 region: str,
                 account: str,
                 topic: Optional[str] = None,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.region = region
        self.account = account
        self.topic = topic

    def _set_name(self, prefix):
        self.name = '{}-sqs-eventsource'.format(prefix)

    @property
    def json(self):
        d = vars(self)
        d['class'] = self.__class__.__name__
        return d
