#!/usr/bin/python
# coding: utf-8

u"""
    ロックマンエグゼ６の文字コードや各種アドレスの辞書

    ロックマンエグゼ６用文字コード対応表（http://www65.atwiki.jp/mmnbhack/pages/17.html）を少し改変

"""

import binascii
import sys

# 1バイト文字
CP_EXE6_1 = {
"\x00":" ",  "\x01":"０", "\x02":"１", "\x03":"２", "\x04":"３", "\x05":"４", "\x06":"５", "\x07":"６",
"\x08":"７", "\x09":"８", "\x0A":"９", "\x0B":"ウ", "\x0C":"ア", "\x0D":"イ", "\x0E":"オ", "\x0F":"エ",
"\x10":"ケ", "\x11":"コ", "\x12":"カ", "\x13":"ク", "\x14":"キ", "\x15":"セ", "\x16":"サ", "\x17":"ソ",
"\x18":"シ", "\x19":"ス", "\x1A":"テ", "\x1B":"ト", "\x1C":"ツ", "\x1D":"タ", "\x1E":"チ", "\x1F":"ネ",
"\x20":"ノ", "\x21":"ヌ", "\x22":"ナ", "\x23":"ニ", "\x24":"ヒ", "\x25":"ヘ", "\x26":"ホ", "\x27":"ハ",
"\x28":"フ", "\x29":"ミ", "\x2A":"マ", "\x2B":"メ", "\x2C":"ム", "\x2D":"モ", "\x2E":"ヤ", "\x2F":"ヨ",
"\x30":"ユ", "\x31":"ロ", "\x32":"ル", "\x33":"リ", "\x34":"レ", "\x35":"ラ", "\x36":"ン", "\x37":"熱",
"\x38":"斗", "\x39":"ワ", "\x3A":"ヲ", "\x3B":"ギ", "\x3C":"ガ", "\x3D":"ゲ", "\x3E":"ゴ", "\x3F":"グ",
"\x40":"ゾ", "\x41":"ジ", "\x42":"ゼ", "\x43":"ズ", "\x44":"ザ", "\x45":"デ", "\x46":"ド", "\x47":"ヅ",
"\x48":"ダ", "\x49":"ヂ", "\x4A":"ベ", "\x4B":"ビ", "\x4C":"ボ", "\x4D":"バ", "\x4E":"ブ", "\x4F":"ピ",
"\x50":"パ", "\x51":"ペ", "\x52":"プ", "\x53":"ポ", "\x54":"ゥ", "\x55":"ァ", "\x56":"ィ", "\x57":"ォ",
"\x58":"ェ", "\x59":"ュ", "\x5A":"ヴ", "\x5B":"ッ", "\x5C":"ョ", "\x5D":"ャ", "\x5E":"Ａ", "\x5F":"Ｂ",
"\x60":"Ｃ", "\x61":"Ｄ", "\x62":"Ｅ", "\x63":"Ｆ", "\x64":"Ｇ", "\x65":"Ｈ", "\x66":"Ｉ", "\x67":"Ｊ",
"\x68":"Ｋ", "\x69":"Ｌ", "\x6A":"Ｍ", "\x6B":"Ｎ", "\x6C":"Ｏ", "\x6D":"Ｐ", "\x6E":"Ｑ", "\x6F":"Ｒ",
"\x70":"Ｓ", "\x71":"Ｔ", "\x72":"Ｕ", "\x73":"Ｖ", "\x74":"Ｗ", "\x75":"Ｘ", "\x76":"Ｙ", "\x77":"Ｚ",
"\x78":"＊", "\x79":"－", "\x7A":"×", "\x7B":"＝", "\x7C":"：", "\x7D":"％", "\x7E":"？", "\x7F":"＋",
"\x80":"■", "\x81":"(ｺｳﾓﾘ)", "\x82":"ー", "\x83":"！", "\x84":"(RV)", "\x85":"(BX)", "\x86":"＆", "\x87":"、",
"\x88":"。", "\x89":"．", "\x8A":"・", "\x8B":"；", "\x8C":"’", "\x8D":"”", "\x8E":"～", "\x8F":"／",
"\x90":"（", "\x91":"）", "\x92":"「", "\x93":"」", "\x94":"(EX)", "\x95":"(SP)", "\x96":"(FZ)", "\x97":"□",
"\x98":"＿", "\x99":"ｚ", "\x9A":"周", "\x9B":"え", "\x9C":"お", "\x9D":"う", "\x9E":"あ", "\x9F":"い",
"\xA0":"け", "\xA1":"く", "\xA2":"き", "\xA3":"こ", "\xA4":"か", "\xA5":"せ", "\xA6":"そ", "\xA7":"す",
"\xA8":"さ", "\xA9":"し", "\xAA":"つ", "\xAB":"と", "\xAC":"て", "\xAD":"た", "\xAE":"ち", "\xAF":"ね",
"\xB0":"の", "\xB1":"な", "\xB2":"ぬ", "\xB3":"に", "\xB4":"へ", "\xB5":"ふ", "\xB6":"ほ", "\xB7":"は",
"\xB8":"ひ", "\xB9":"め", "\xBA":"む", "\xBB":"み", "\xBC":"も", "\xBD":"ま", "\xBE":"ゆ", "\xBF":"よ",
"\xC0":"や", "\xC1":"る", "\xC2":"ら", "\xC3":"り", "\xC4":"ろ", "\xC5":"れ", "\xC6":"究", "\xC7":"ん",
"\xC8":"を", "\xC9":"わ", "\xCA":"研", "\xCB":"げ", "\xCC":"ぐ", "\xCD":"ご", "\xCE":"が", "\xCF":"ぎ",
"\xD0":"ぜ", "\xD1":"ず", "\xD2":"じ", "\xD3":"ぞ", "\xD4":"ざ", "\xD5":"で", "\xD6":"ど", "\xD7":"づ",
"\xD8":"だ", "\xD9":"ぢ", "\xDA":"べ", "\xDB":"ば", "\xDC":"び", "\xDD":"ぼ", "\xDE":"ぶ", "\xDF":"ぽ",
"\xE0":"ぷ", "\xE1":"ぴ", "\xE2":"ぺ", "\xE3":"ぱ",
"\xE4":"<E4>",    "\xE5":"<E5>",    "\xE6":"<E6:閉>",    "\xE7":"<E7:終端>",
"\xE8":"<E8:開>",    "\xE9":"<E9:改行>",    "\xEA":"<EA>",    "\xEB":"<EB>",
"\xEC":"<EC:Cursor>",    "\xED":"<ED:Select>",    "\xEE":"<EE:Pause>",    "\xEF":"<skip?>",
"\xF0":"<F0:ch_speaker>",    "\xF1":"<F1:Speed>",    "\xF2":"<F2:消去>",    "\xF3":"<F3>",
"\xF4":"<F4:Sound>",    "\xF5":"<F5:顔>",    "\xF6":"<F6>",    "\xF7":"<F7>",
"\xF8":"<F8>",    "\xF9":"<F9>",    "\xFA":"<FA>",    "\xFB":"<FB>",
"\xFC":"<FC>",    "\xFD":"<FD>",    "\xFE":"<FE>",    "\xFF":"<FF>"
}

# 2バイト文字（\xE4 + \xXX）
CP_EXE6_2 = {
"\x00":"ぅ",    "\x01":"ぁ",    "\x02":"ぃ",    "\x03":"ぉ",    "\x04":"ぇ",    "\x05":"ゅ",    "\x06":"ょ",    "\x07":"っ",
"\x08":"ゃ",    "\x09":"a",    "\x0A":"b",    "\x0B":"c",    "\x0C":"d",    "\x0D":"e",    "\x0E":"f",    "\x0F":"g",
"\x10":"h",    "\x11":"i",    "\x12":"j",    "\x13":"k",    "\x14":"l",    "\x15":"m",    "\x16":"n",    "\x17":"o",
"\x18":"p",    "\x19":"q",    "\x1A":"r",    "\x1B":"s",    "\x1C":"t",    "\x1D":"u",    "\x1E":"v",    "\x1F":"w",
"\x20":"x",    "\x21":"y",    "\x22":"z",    "\x23":"容",    "\x24":"量",    "\x25":"全",    "\x26":"木",    "\x27":"(MB)",
"\x28":"無",    "\x29":"現",    "\x2A":"実",    "\x2B":"○",    "\x2C":"×",    "\x2D":"緑",    "\x2E":"道",    "\x2F":"不",
"\x30":"止",    "\x31":"彩",    "\x32":"起",    "\x33":"父",    "\x34":"集",    "\x35":"院",    "\x36":"一",    "\x37":"二",
"\x38":"三",    "\x39":"四",    "\x3A":"五",    "\x3B":"六",    "\x3C":"七",    "\x3D":"八",    "\x3E":"陽",    "\x3F":"十",
"\x40":"百",    "\x41":"千",    "\x42":"万",    "\x43":"脳",    "\x44":"上",    "\x45":"下",    "\x46":"左",    "\x47":"右",
"\x48":"手",    "\x49":"来",    "\x4A":"日",    "\x4B":"目",    "\x4C":"月",    "\x4D":"獣",    "\x4E":"名",    "\x4F":"人",
"\x50":"入",    "\x51":"出",    "\x52":"山",    "\x53":"口",    "\x54":"光",    "\x55":"電",    "\x56":"気",    "\x57":"綾",
"\x58":"科",    "\x59":"次",    "\x5A":"名",    "\x5B":"前",    "\x5C":"学",    "\x5D":"校",    "\x5E":"省",    "\x5F":"祐",
"\x60":"室",    "\x61":"世",    "\x62":"界",    "\x63":"高",    "\x64":"朗",    "\x65":"枚",    "\x66":"野",    "\x67":"悪",
"\x68":"路",    "\x69":"闇",    "\x6A":"大",    "\x6B":"小",    "\x6C":"中",    "\x6D":"自",    "\x6E":"分",    "\x6F":"間",
"\x70":"系",    "\x71":"鼻",    "\x72":"問",    "\x73":"究",    "\x74":"門",    "\x75":"城",    "\x76":"王",    "\x77":"兄",
"\x78":"化",    "\x79":"葉",    "\x7A":"行",    "\x7B":"街",    "\x7C":"屋",    "\x7D":"水",    "\x7E":"見",    "\x7F":"終",
"\x80":"新",    "\x81":"桜",    "\x82":"先",    "\x83":"生",    "\x84":"長",    "\x85":"今",    "\x86":"了",    "\x87":"点",
"\x88":"井",    "\x89":"子",    "\x8A":"言",    "\x8B":"太",    "\x8C":"属",    "\x8D":"風",    "\x8E":"会",    "\x8F":"性",
"\x90":"持",    "\x91":"時",    "\x92":"勝",    "\x93":"赤",    "\x94":"毎",    "\x95":"年",    "\x96":"火",    "\x97":"改",
"\x98":"計",    "\x99":"画",    "\x9A":"職",    "\x9B":"体",    "\x9C":"波",    "\x9D":"回",    "\x9E":"外",    "\x9F":"地",
"\xA0":"員",    "\xA1":"正",    "\xA2":"造",    "\xA3":"値",    "\xA4":"合",    "\xA5":"戦",    "\xA6":"川",    "\xA7":"秋",
"\xA8":"原",    "\xA9":"町",    "\xAA":"晴",    "\xAB":"用",    "\xAC":"金",    "\xAD":"郎",    "\xAE":"作",    "\xAF":"数",
"\xB0":"方",    "\xB1":"社",    "\xB2":"攻",    "\xB3":"撃",    "\xB4":"力",    "\xB5":"同",    "\xB6":"武",    "\xB7":"何",
"\xB8":"発",    "\xB9":"少",    "\xBA":"教",    "\xBB":"以",    "\xBC":"白",    "\xBD":"早",    "\xBE":"暮",    "\xBF":"面",
"\xC0":"組",    "\xC1":"後",    "\xC2":"文",    "\xC3":"字",    "\xC4":"本",    "\xC5":"階",    "\xC6":"明",    "\xC7":"才",
"\xC8":"者",    "\xC9":"向",    "\xCA":"犬",    "\xCB":"々",    "\xCC":"ヶ",    "\xCD":"連",    "\xCE":"射",    "\xCF":"舟",
"\xD0":"戸",    "\xD1":"切",    "\xD2":"土",    "\xD3":"炎",    "\xD4":"伊",    "\xD5":"夫",    "\xD6":"鉄",    "\xD7":"国",
"\xD8":"男",    "\xD9":"天",    "\xDA":"老",    "\xDB":"師",    "\xDC":"xDC",    "\xDD":"xDD",    "\xDE":"xDE",    "\xDF":"xDF",
"\xE0":"xE0",    "\xE1":"xE1",    "\xE2":"xE2",    "\xE3":"xE3",    "\xE4":"xE4",    "\xE5":"xE5",    "\xE6":"xE6",    "\xE7":"xE7",
"\xE8":"xE8",    "\xE9":"xE9",    "\xEA":"xEA",    "\xEB":"xEB",    "\xEC":"xEC",    "\xED":"xED",    "\xEE":"xEE",    "\xEF":"xEF",
"\xF0":"xF0",    "\xF1":"xF1",    "\xF2":"xF2",    "\xF3":"xF3",    "\xF4":"xF4",    "\xF5":"xF5",    "\xF6":"xF6",    "\xF7":"xF7",
"\xF8":"xF8",    "\xF9":"xF9",    "\xFA":"xFA",    "\xFB":"xFB",    "\xFC":"xFC",    "\xFD":"xFD",    "\xFE":"xFE",    "\xFF":"xFF"
}

# 逆引き辞書
CP_EXE6_1_inv = {v:k for k, v in CP_EXE6_1.items()}
CP_EXE6_2_inv = {v:k for k, v in CP_EXE6_2.items()}

# テキストからバイナリに変換するときに半角にも対応する
half = {
"0":"\x01",    "1":"\x02",    "2":"\x03",    "3":"\x04",    "4":"\x05",
"5":"\x06",    "6":"\x07",    "7":"\x08",    "8":"\x09",    "9":"\x0A",
"A":"\x5E",    "B":"\x5F",    "C":"\x60",    "D":"\x61",    "E":"\x62",
"F":"\x63",    "G":"\x64",    "H":"\x65",    "I":"\x66",    "J":"\x67",
"K":"\x68",    "L":"\x69",    "M":"\x6A",    "N":"\x6B",    "O":"\x6C",
"P":"\x6D",    "Q":"\x6E",    "R":"\x6F",    "S":"\x70",    "T":"\x71",
"U":"\x72",    "V":"\x73",    "W":"\x74",    "X":"\x75",    "Y":"\x76",
"Z":"\x77",    "*":"\x78",    "-":"\x79",    "=":"\x7B",    ":":"\x7C",
"%":"\x7D",    "?":"\x7E",    "+":"\x7F",    "!":"\x83",    "&":"\x86",
}
CP_EXE6_1_inv.update(half)

# グレイガ版の各種アドレス[名前, 先頭アドレス, 終端アドレス]
GXX_Addr_List = [
["Map",      "0x6EB560", "0x6EBC09"],
["ChipText", "0x70C36E", "0x7102A2"],
["Enemy",    "0x710FFE", "0x71163F"],
["Navi",     "0x7117B0", "0x711B7F"],
["KeyItem",  "0x75F094", "0x75F37A"],
["NaviCus",  "0x75FF39", "0x7600A0"]
]

# ロックマンのスプライトのポインタ周辺をとりあえず使ってみる
# このアドレスの直前にポインタのテーブルっぽいものがある
# テーブルのポインタが示すアドレスには白玉がある．スプライトのまとまりを区切ってるのだろうか
GXX_Sprite_Table = {
"startAddr":0x032CA8,
"endAddr":0x033963
}

# ファルザー版の各種アドレス
RXX_Addr_List = [
["Map",      "0x6ED62C", "0x6EDCD6"],
["ChipText", "0x70E40E", "0x712342"],
["Enemy",    "0x71309E", "0x7136DF"],
["Navi",     "0x713850", "0x713C1F"],
["KeyItem",  "0x761160", "0x761446"],
["NaviCus",  "0x762005", "0x76216C"]
]

RXX_Sprite_Table = {
"startAddr":0x032CA8,
"endAddr":0x033963
}

def encodeByEXE6Dict(data):
    u"""バイナリ文字列をエグゼ６のテキストとしてエンコード
    """

    readPos = 0 # 読み取るアドレス
    L = []  # 出力するデータの配列

    while readPos < len(data):
        currentChar = data[readPos]

        if currentChar == "\xE4":
            u""" ２バイト文字フラグ
            """
            readPos += 1  # 次の文字を
            L.append( CP_EXE6_2[ data[readPos] ] )  # 2バイト文字として出力

        elif currentChar in ["\xF0", "\xF5"]:
            u""" 次の2バイトを使うコマンド
            """

            #L.append("\n" + hex(readPos) + ": ")
            #L.append("\n\n## ")
            L.append(CP_EXE6_1[currentChar])
            L.append( "[0x" + binascii.hexlify(data[readPos+1] + data[readPos+2]) + "]")    # 文字コードの値をそのまま文字列として出力（'\xAB' -> "AB"）

            if currentChar in ["\xF0", "\xF5"]:
                L.append("\n")

            readPos += 2

        elif currentChar in ["\xEE"]:
            u""" 次の3バイトを使うコマンド
            """

            L.append(CP_EXE6_1[currentChar])
            L.append( "[0x" + binascii.hexlify(data[readPos+1:readPos+4]) + "]")
            readPos += 3

        # \xE6 リスト要素の終わりに現れるようなので、\xE6が現れたら次の要素の先頭アドレスを確認できるようにする
        elif currentChar == "\xE6":
            L.append(CP_EXE6_1[currentChar])
            #L.append("\n" + hex(readPos+1) + ": ")
            L.append("\n\n@ "  + hex(readPos+1) + " @\n")

        # テキストボックスを開く\xE8の次の1バイトは\0x00，\xE7も同様？
        elif currentChar in ["\xE7", "\xE8"]:
            #L.append("\n\n---\n")
            L.append(CP_EXE6_1[currentChar])
            readPos += 1
            L.append( "[0x" + binascii.hexlify(data[readPos]) + "]")
            if currentChar in ["\xE7"]:
                L.append("\n")
            elif currentChar in ["\xE8"]:
                L.append("\n")

        elif currentChar in ["\xE9", "\xF2"]:
            u""" 改行，テキストウインドウのクリア
            """
            L.append(CP_EXE6_1[ currentChar])
            L.append("\n")

        # 1バイト文字
        else:
            L.append( CP_EXE6_1[ currentChar ] )

        readPos += 1

        if readPos % 10000 == 0:    # 進捗表示
            sys.stdout.write(".")

    result = "".join(L)    # 配列を一つの文字列に連結
    return result


def decodeByEXE6Dict(self, string):
    u"""エグゼ６のテキストをバイナリ文字列にデコード
    """
    result = ""
    readPos = 0

    while readPos < len(string):
        currentChar = string[readPos].encode('utf-8')   # Unicode文字列から1文字取り出してString型に変換

        if currentChar == "@":
            u""" コメントは@で囲んでいる
            """
            readPos += 1
            while string[readPos] != "@":
                readPos += 1
            continue

        # BXなどは(BX)と表記している
        if currentChar == "(":
            readPos += 1
            while string[readPos] != ")":
                currentChar += string[readPos]
                readPos += 1
            currentChar += string[readPos]

        # 改行などは<改行>などのコマンドとして表示している
        if currentChar == "<":
            readPos += 1
            while string[readPos] != ">":
                currentChar += string[readPos]
                readPos += 1
            currentChar += string[readPos]
            result += binascii.unhexlify(currentChar[1:3]) # <F5:顔>のF5だけ取り出して数値に戻す
            readPos += 1
            continue

        # 値は[0037]などのパラメータとして表示している
        if currentChar == "[":
            readPos += 1
            while string[readPos] != "]":
                currentChar += string[readPos]
                readPos += 1
            currentChar += string[readPos]
            result += binascii.unhexlify(currentChar[3:-1]) # [0xHHHH]のHHHHだけ取り出して数値に戻す
            readPos += 1
            continue

        if currentChar in CP_EXE6_2_inv:    # 2バイト文字なら
            result += "\xE4" + CP_EXE6_2_inv[currentChar]
        elif currentChar in CP_EXE6_1_inv:  # 1バイト文字なら
            result += CP_EXE6_1_inv[currentChar]
        else:   # 辞書に存在しない文字なら
            result += "\x80"    # ■に置き換え
            print u"辞書に「" + currentChar + "」と一致する文字がありません"

        readPos += 1

    return result
