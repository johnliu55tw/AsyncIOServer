import unittest
import datetime
from unittest import mock

import show_data


class ShowDataTestCase(unittest.TestCase):

    def setUp(self):
        self.mockedStdout = mock.MagicMock()
        self.datetimeNow = datetime.datetime.now()

    def testShowDataInit(self):
        displayer = show_data.Displayer(stream=self.mockedStdout)
        self.assertIsNotNone(displayer)

        displayer = show_data.Displayer(stream=self.mockedStdout,
                                        name="TheDataDisplayer")
        self.assertIsNotNone(displayer)

    @mock.patch("show_data.datetime")
    def testShowMethod(self, mockedDatetime):
        # Setup the datetime.datetime.now return value
        mockedDatetime.datetime.now.return_value = self.datetimeNow

        displayer = show_data.Displayer(stream=self.mockedStdout)

        displayer.show(b"\xAB\x01\x10\x0F")

        self.mockedStdout.write.assert_called_with(
            " * {} - 1\nAB:01:10:0F\n{}\n".format(
                self.datetimeNow.isoformat(),
                "-----------"))

    def testShowMethodWithTimestamp(self):
        displayer = show_data.Displayer(stream=self.mockedStdout)

        anotherDatetime = datetime.datetime(2016, 1, 2, 11, 22, 33, 123456)
        displayer.show(b"\xAB\x01\x10\x0F", timestamp=anotherDatetime)

        self.mockedStdout.write.assert_called_with(
            " * 2016-01-02T11:22:33.123456 - 1\nAB:01:10:0F\n-----------\n")

    def testShowMethodRaise(self):
        displayer = show_data.Displayer(stream=self.mockedStdout)

        # timestamp must be datetime object
        with self.assertRaisesRegex(ValueError,
                                    "timestamp must be datetime object."):
            displayer.show(b"\xAB\x01\x10\x0F", timestamp=1234567890)

    def testShowMethodWithName(self):
        displayer = show_data.Displayer(stream=self.mockedStdout,
                                        name='ThePacketDisplayer')

        displayer.show(b"\xAB\x01\x10\x0F",
                       timestamp=self.datetimeNow)

        self.mockedStdout.write.assert_called_with(
            " * ThePacketDisplayer\n * {} - 1\nAB:01:10:0F\n{}\n".format(
                self.datetimeNow.isoformat(),
                "-----------"))
