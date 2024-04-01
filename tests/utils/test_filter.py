"""Unittest module for media downloader."""
import sys
import unittest
from datetime import datetime

import mock

from module.filter import Filter, MetaData
from module.pyrogram_extension import set_meta_data
from tests.test_common import (
    Chat,
    Date,
    MockAudio,
    MockDocument,
    MockMessage,
    MockPhoto,
    MockUser,
    MockVideo,
    MockVideoNote,
    MockVoice,
    get_extension,
)
from utils.format import replace_date_time

sys.path.append("..")  # Adds higher directory to python modules path.


def filter_exec(download_filter: Filter, filter_str: str) -> bool:
    filter_str = replace_date_time(filter_str)
    return download_filter.exec(filter_str)


def check_filter_exec(download_filter: Filter, filter_str: str) -> bool:
    filter_str = replace_date_time(filter_str)
    return download_filter.check_filter(filter_str)


@mock.patch("module.pyrogram_extension.get_extension", new=get_extension)
class FilterTestCase(unittest.TestCase):
    def test_string_filter(self):
        download_filter = Filter()
        self.assertRaises(ValueError, filter_exec, download_filter, "213")

        meta = MetaData()

        message = MockMessage(
            id=5,
            media=True,
            date=datetime(2022, 8, 5, 14, 35, 12),
            chat_title="test2",
            caption=None,
            video=MockVideo(
                mime_type="video/mp4",
                file_size=1024 * 1024 * 10,
                file_name="test.mp4",
                width=1920,
                height=1080,
                duration=35,
            ),
            from_user=MockUser(
                username="coco",
                id=123,
            ),
        )

        set_meta_data(meta, message)

        self.assertEqual(meta.message_id, 5)
        self.assertEqual(meta.message_date, datetime(2022, 8, 5, 14, 35, 12))
        self.assertEqual(meta.message_caption, "")
        self.assertEqual(meta.media_file_size, 1024 * 1024 * 10)
        self.assertEqual(meta.media_width, 1920)
        self.assertEqual(meta.media_height, 1080)
        self.assertEqual(meta.media_file_name, "test.mp4")
        self.assertEqual(meta.media_duration, 35)
        self.assertEqual(meta.media_type, "video")
        self.assertEqual(meta.file_extension, "mp4")

        download_filter.set_meta_data(meta)

        self.assertEqual(filter_exec(download_filter, "media_file_size == 1"), False)
        self.assertEqual(filter_exec(download_filter, "media_file_size > 1024"), True)

        # str
        self.assertEqual(
            filter_exec(download_filter, "media_file_name == 'test.mp4'"), True
        )
        self.assertEqual(
            filter_exec(download_filter, "media_file_name == 'test2.mp4'"), False
        )
        # re str
        self.assertEqual(
            filter_exec(download_filter, "media_file_name == r'test.*mp4'"), True
        )

        self.assertEqual(
            filter_exec(download_filter, "media_file_name == r'test\.*mp4'"), True
        )

        self.assertEqual(
            filter_exec(download_filter, "media_file_name == r'test2.*mp4'"), False
        )

        self.assertEqual(
            filter_exec(download_filter, "media_file_name != r'test2.*mp4'"), True
        )
        self.assertEqual(
            filter_exec(download_filter, "media_file_name != r'test2.*mp4'"), True
        )

        # int
        self.assertEqual(filter_exec(download_filter, "media_duration > 60"), False)
        self.assertEqual(filter_exec(download_filter, "media_duration <= 60"), True)
        self.assertEqual(
            filter_exec(
                download_filter, "media_width >= 1920 and media_height >= 1080"
            ),
            True,
        )
        self.assertEqual(
            filter_exec(download_filter, "media_width >= 2560 && media_height >= 1440"),
            False,
        )
        self.assertEqual(
            filter_exec(
                download_filter,
                "media_width >= 2560 && media_height >= 1440 or media_file_name == 'test.mp4'",
            ),
            True,
        )

        # datetime
        # 2020.03
        self.assertEqual(
            filter_exec(
                download_filter, "message_date >= 2022.03 and message_date <= 2022.08"
            ),
            False,
        )
        self.assertEqual(
            filter_exec(
                download_filter, "message_date >= 2022.03 and message_date <= 2022.09"
            ),
            True,
        )

        # 2020.03.04
        self.assertEqual(
            filter_exec(
                download_filter,
                "message_date >= 2022.03.04 and message_date <= 2022.03.08",
            ),
            False,
        )
        self.assertEqual(
            filter_exec(
                download_filter,
                "message_date >= 2022.03.04 and message_date <= 2022.08.06",
            ),
            True,
        )

        # 2020.03.04 14:50
        self.assertEqual(
            filter_exec(
                download_filter,
                "message_date >= 2022.03.04 14:50 and message_date <= 2022.03.08",
            ),
            False,
        )
        self.assertEqual(
            filter_exec(
                download_filter,
                "message_date >= 2022.03.04 and message_date <= 2022.08.05 14:36",
            ),
            True,
        )

        # 2020.03.04 14:50:15
        self.assertEqual(
            filter_exec(
                download_filter,
                "message_date >= 2022.03.04 14:50:15 and message_date <= 2022.03.08",
            ),
            False,
        )
        self.assertEqual(
            filter_exec(
                download_filter,
                "message_date >= 2022.03.04 14:50:15 and message_date <= 2022.08.05 14:35:12",
            ),
            True,
        )

        # test not exist value
        self.assertRaises(
            ValueError,
            filter_exec,
            download_filter,
            "message_date >= 2022.03.04 && message_date <= 2022.08.06 && not_exist == True",
        )

        download_filter.set_debug(True)

        # test file_size
        self.assertEqual(filter_exec(download_filter, "file_size >= 10MB"), True)

        self.assertEqual(filter_exec(download_filter, "file_size >= 11MB"), False)

        self.assertEqual(filter_exec(download_filter, "file_size >= 11GB"), False)

        self.assertEqual(filter_exec(download_filter, "file_size <= 11GB"), True)

        self.assertEqual(
            filter_exec(download_filter, "1024 * 1024 * 1024 * 11 == 11GB"), True
        )

        # test caption
        self.assertEqual(filter_exec(download_filter, "caption == r'.*#test.*'"), False)

        # test media_type
        self.assertEqual(filter_exec(download_filter, "media_type == 'video'"), True)

        self.assertEqual(filter_exec(download_filter, "media_type == 'audio'"), False)

        self.assertEqual(
            filter_exec(download_filter, "media_type == r'(video|audio)'"), True
        )

        self.assertEqual(
            filter_exec(download_filter, "media_type != r'(video|audio)'"), False
        )

        # test file_extension
        self.assertEqual(filter_exec(download_filter, "file_extension == 'mp4'"), True)

        self.assertEqual(filter_exec(download_filter, "file_extension == 'mp3'"), False)

        self.assertEqual(
            filter_exec(download_filter, "file_extension == r'(mp4|mp3)'"), True
        )

        self.assertEqual(
            filter_exec(download_filter, "file_extension != r'(mp4|mp3)'"), False
        )

        # test sender
        self.assertEqual(filter_exec(download_filter, "sender_name == 'coco'"), True)

        self.assertEqual(filter_exec(download_filter, "sender_id == 1"), False)

    def test_null_obj(self):
        download_filter = Filter()

        meta = MetaData()

        message = MockMessage(
            id=5,
            media=True,
            date=datetime(2022, 8, 5, 14, 35, 12),
            chat_title="test2",
            caption=None,
            video=MockPhoto(
                file_size=1024 * 1024 * 10,
                date=datetime(2019, 8, 5, 14, 35, 12),
                file_unique_id="ADAVKJYIFV",
            ),
        )

        set_meta_data(meta, message)

        download_filter.set_meta_data(meta)

        # test media_duration
        self.assertEqual(filter_exec(download_filter, "media_duration < 1"), False)
        self.assertEqual(filter_exec(download_filter, "media_duration <= 1"), False)
        self.assertEqual(filter_exec(download_filter, "media_duration != 1"), False)
        self.assertEqual(filter_exec(download_filter, "media_duration == 1"), False)

    def test_str_obj(self):
        download_filter = Filter()
        self.assertRaises(ValueError, filter_exec, download_filter, "213")

        meta = MetaData()

        message = MockMessage(
            id=5,
            media=True,
            date=datetime(2022, 8, 5, 14, 35, 12),
            chat_title="test2",
            caption="#中文最吊 #哈啰",
            video=MockVideo(
                mime_type="video/mp4",
                file_size=1024 * 1024 * 10,
                file_name="test.mp4",
                width=1920,
                height=1080,
                duration=35,
            ),
            reply_to_message_id=4,
        )

        set_meta_data(meta, message)

        self.assertEqual(meta.message_id, 5)
        self.assertEqual(meta.message_date, datetime(2022, 8, 5, 14, 35, 12))
        self.assertEqual(meta.message_caption, "#中文最吊 #哈啰")
        self.assertEqual(meta.media_file_size, 1024 * 1024 * 10)
        self.assertEqual(meta.media_width, 1920)
        self.assertEqual(meta.media_height, 1080)
        self.assertEqual(meta.media_file_name, "test.mp4")
        self.assertEqual(meta.media_duration, 35)

        download_filter.set_meta_data(meta)
        download_filter.set_debug(True)

        # test caption
        self.assertEqual(filter_exec(download_filter, "caption == r'.*#test.*'"), False)

        self.assertEqual(filter_exec(download_filter, "caption == r'.*#中文.*'"), True)

        self.assertEqual(filter_exec(download_filter, "caption == r'.*#中文啊.*'"), False)

        self.assertEqual(filter_exec(download_filter, "reply_to_message_id == 4"), True)
        self.assertEqual(
            filter_exec(download_filter, "reply_to_message_id != 4"), False
        )
        self.assertEqual(filter_exec(download_filter, "reply_to_message_id >= 4"), True)

    def test_check_filter(self):
        download_filter = Filter()
        meta = MetaData()

        message = MockMessage(
            id=5,
            media=True,
            date=datetime(2022, 8, 5, 14, 35, 12),
            chat_title="test2",
            caption=None,
            video=MockVideo(
                mime_type="video/mp4",
                file_size=1024 * 1024 * 10,
                file_name="test.mp4",
                width=1920,
                height=1080,
                duration=35,
            ),
        )

        set_meta_data(meta, message)

        download_filter.set_debug(True)
        download_filter.set_meta_data(meta)

        # 1. ==
        # 1.1 restring
        self.assertEqual(
            check_filter_exec(download_filter, "caption == rr'.*#中文啊.*'"),
            (False, "Syntax error at '.*#中文啊.*'"),
        )
        self.assertEqual(
            check_filter_exec(download_filter, "caption == r'.*#中文啊.*'"), (True, None)
        )
        self.assertEqual(
            check_filter_exec(download_filter, "caption tis r'.*#中文啊.*'"),
            (False, "Syntax error at 'tis'"),
        )
        # 1.2 string
        self.assertEqual(
            check_filter_exec(download_filter, "caption = '.*#中文啊.*'"), (True, None)
        )

        # 2. check type
        # 2.1 str
        self.assertEqual(
            check_filter_exec(download_filter, "caption = 1"),
            (False, "caption is str but 1 is not"),
        )
        self.assertEqual(
            check_filter_exec(download_filter, "caption = 3KB"),
            (False, "caption is str but 3072 is not"),
        )
        # 2.2 datetime
        self.assertEqual(
            check_filter_exec(download_filter, "message_date == '.*#中文啊.*'"),
            (False, "2022-08-05 14:35:12 is datetime but .*#中文啊.* is not"),
        )

        # 2.3 int
        self.assertEqual(
            check_filter_exec(download_filter, "id == '.*'"),
            (False, "5 is int but .* is not"),
        )
        self.assertEqual(
            check_filter_exec(download_filter, "id == .*"),
            (False, "Syntax error at '*'"),
        )
        self.assertEqual(
            check_filter_exec(download_filter, "id == ."),
            (False, "Syntax error at EOF"),
        )
        self.assertEqual(
            check_filter_exec(download_filter, "id == ."),
            (False, "Syntax error at EOF"),
        )
        # 2.3.1 custom token
        self.assertEqual(
            check_filter_exec(download_filter, "file_size == 3KB"), (True, None)
        )
        self.assertEqual(
            check_filter_exec(download_filter, "file_size == 3kb"),
            (False, "Syntax error at 'kb'"),
        )

        # 3. error name
        self.assertEqual(
            check_filter_exec(download_filter, "caption2 == .*#中文啊.*'"),
            (False, "Undefined name caption2"),
        )

        # 4. datetime
        self.assertEqual(
            check_filter_exec(download_filter, "message_date == 2023/0b-05"),
            (False, "Syntax error at 'b'"),
        )
        self.assertEqual(
            check_filter_exec(download_filter, "message_date == 2023/01/45")[0], False
        )

    def test_normal(self):
        download_filter = Filter()
        print(download_filter.filter.names)
        meta = MetaData(datetime(2022, 3, 8, 10, 0, 0), 0, "#高桥千x", 0, 0, 0, "", 0)
        download_filter.set_meta_data(meta)
        self.assertEqual(check_filter_exec(download_filter, "id > 1"), (True, None))
        download_filter.set_debug(True)
        filter_exec(download_filter, "caption == r'.*高桥.*'")

        download_filter2 = Filter()
        meta2 = MetaData(datetime(2022, 3, 8, 10, 0, 0), 0, "", 0, 0, 0, "", 0)
        download_filter2.set_meta_data(meta2)
        download_filter2.set_debug(True)
        filter_exec(download_filter2, "caption == r'.*高桥.*'")
        print(download_filter.filter.names)

        download_filter.set_meta_data(meta)
        self.assertEqual(check_filter_exec(download_filter, "id > 1"), (True, None))
        download_filter.set_debug(True)
        filter_exec(download_filter, "caption == r'.*高桥.*'")
        filter_exec(download_filter, "caption == r'.*高桥.*'")
