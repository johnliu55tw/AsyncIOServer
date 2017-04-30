import datetime


class Displayer(object):

    def __init__(self, stream, name=None):
        self.stream = stream
        self.name = name
        self.counter = 0

    @staticmethod
    def buildHeadString(name, timestamp, counter):
        headString = ""
        if name is not None:
            headString += " * {}\n".format(name)
        headString += " * {} - {}\n".format(timestamp.isoformat(), counter)

        return headString

    def show(self, data, timestamp=None):
        if timestamp is None:
            timestamp = datetime.datetime.now()
        elif not isinstance(timestamp, datetime.datetime):
            raise ValueError("timestamp must be datetime object.")

        self.counter += 1

        dataStringLength = len(data) * 3 - 1
        dataString = ":".join("{:02X}".format(c) for c in data) + '\n'
        headString = self.buildHeadString(name=self.name,
                                          timestamp=timestamp,
                                          counter=self.counter)
        endString = "-" * dataStringLength + '\n'

        self.stream.write(headString + dataString + endString)
