import re

KANSUJI_TABLE = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '八', 9: '九', }


class Converter:
    @staticmethod
    def to_hankaku(s: str) -> str:
        return s.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))

    @staticmethod
    def to_kansuji(num_str: str) -> str:
        num10, num1 = divmod(int(num_str), 10)
        result = ""
        if num10 >= 2:
            result += KANSUJI_TABLE[num10]
        if num10 >= 1:
            result += '十'
        if num1 >= 1:
            result += KANSUJI_TABLE[num1]
        return result

    @classmethod
    def replace_area_number_to_kansuji(cls, s: str) -> str:
        hankaku = cls.to_hankaku(s)
        result = re.sub("\\d+", lambda x: cls.to_kansuji(x.group()), hankaku)
        return result
