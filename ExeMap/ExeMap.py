""" EXE Map

    今は日本語版グレイガ専用です。
"""
# pylint: disable=c-extension-no-member, import-error, invalid-name, pointless-string-statement

import argparse
import logging
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import exe_map_settings as settings
import UI_ExeMap as Designer
import CommonAction as Common
import compress
import LZ77Util


""" ロギング設定 """
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setLevel(logging.DEBUG)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(STREAM_HANDLER)

""" パーサ設定 """
PARSER = argparse.ArgumentParser(description=settings.PROGRAM_NAME)
PARSER.add_argument('-f', '--file', help='開くROMファイル')
ARGS = PARSER.parse_args()


class ExeMap(QtWidgets.QMainWindow):
    """ EXE Map
    """
    def __init__(self, parent=None):
        """ init
        """
        super(ExeMap, self).__init__(parent)
        self.ui = Designer.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(settings.PROGRAM_NAME)
        self.setWindowIcon(QtGui.QIcon(settings.ICON_PATH))
        self.graphics_scene = QtWidgets.QGraphicsScene(self)
        self.ui.graphicsView.setScene(self.graphics_scene)
        self.ui.graphicsView.scale(1, 1)
        self.current_map = None
        self.bin_map_bg = b''

        with open('ROCKEXE6_GXX.gba', 'rb') as bin_file:
            self.bin_data = bin_file.read()

        self.map_entry_list = self.init_map_entry_list()

    def init_map_entry_list(self):
        """ マップリストの初期化
        """
        map_entry_offsets = list(range(settings.MAP_ENTRY_START, settings.MAP_ENTRY_END, settings.MAP_ENTRY_SIZE))
        map_entry_list = []
        self.ui.mapList.clear()

        count = 0
        for map_entry_offset in map_entry_offsets:
            tileset = int.from_bytes(self.bin_data[map_entry_offset:map_entry_offset+4], 'little')
            if tileset == 0:  # テーブル内に電脳とインターネットの区切りがあるので除去
                continue

            map_entry = ExeMapEntry(map_entry_offset, self.bin_data)
            map_entry_list.append(map_entry)
            item = QtWidgets.QListWidgetItem(str(count) + ':\t' + hex(map_entry_offset))
            self.ui.mapList.addItem(item)
            count += 1

        return map_entry_list

    def ui_map_entry_selected(self):
        """ マップリストのアイテムがダブルクリックされたときの処理
        """
        index = self.ui.mapList.currentRow()
        self.current_map = self.map_entry_list[index]
        self.ui_map_attribute_update()
        self.draw(self.current_map)

    def ui_map_attribute_update(self):
        """ マップ情報の更新
        """
        self.ui.widthValueLabel.setText(str(self.current_map.width) + ' tile')
        self.ui.heightValueLabel.setText(str(self.current_map.height) + ' tile')
        self.ui.tileMapValueLabel.setText(hex(self.current_map.tilemap_offset))

    def draw(self, map_entry):
        """ マップの描画
        """
        # パレットの更新
        bin_palette = self.bin_data[map_entry.palette_offset: map_entry.palette_offset+0x200]
        palette_list = []
        if map_entry.color_mode == 0:
            palette_list = [Common.GbaPalette(bin_palette) for bin_palette in split_by_size(bin_palette, 0x20)]
        elif map_entry.color_mode == 1:
            palette_list.append(Common.GbaPalette(bin_palette, settings.COLOR_NUM_256))

        # GUIのパレットテーブルの更新
        self.ui.paletteTable.clear()
        for row, palette in enumerate(palette_list):
            for col, color in enumerate(palette.color):
                item = QtWidgets.QTableWidgetItem()
                brush = QtGui.QBrush(QtGui.QColor(color.r, color.g, color.b))
                brush.setStyle(QtCore.Qt.SolidPattern)
                item.setBackground(brush)
                if map_entry.color_mode == 0:
                    self.ui.paletteTable.setItem(row, col % settings.COLOR_NUM_16, item)
                elif map_entry.color_mode == 1:
                    self.ui.paletteTable.setItem(col // settings.COLOR_NUM_16,
                                                 col % settings.COLOR_NUM_16, item)

        # タイルの処理
        bin_tileset_1 = LZ77Util.decompLZ77_10(self.bin_data, map_entry.tileset_offset_1)
        bin_tileset_2 = LZ77Util.decompLZ77_10(self.bin_data, map_entry.tileset_offset_2)
        bin_tileset = bin_tileset_1 + bin_tileset_2
        char_base = []

        if map_entry.color_mode == 0:
            char_base = [Common.GbaTile(bin_char)
                         for bin_char in split_by_size(bin_tileset, settings.TILE_DATA_SIZE_16)]
        elif map_entry.color_mode == 1:
            char_base = [Common.GbaTile(bin_char, settings.COLOR_NUM_256)
                         for bin_char in split_by_size(bin_tileset, settings.TILE_DATA_SIZE_256)]

        for i, char in enumerate(char_base):
            # タイルセットリストの表示
            item = QtWidgets.QTableWidgetItem()
            if map_entry.color_mode == 0:
                char.image.setColorTable(palette_list[1].get_qcolors())
            elif map_entry.color_mode == 1:
                char.image.setColorTable(palette_list[0].get_qcolors())
            tile_image = QtGui.QPixmap.fromImage(char.image)
            item.setIcon(QtGui.QIcon(tile_image))
            self.ui.tilesetTable.setItem(i // settings.COLOR_NUM_16,
                                         i % settings.COLOR_NUM_16, item)

        self.bin_map_bg = LZ77Util.decompLZ77_10(self.bin_data, map_entry.tilemap_offset)
        self.draw_map(map_entry, char_base, palette_list)

    def draw_map(self, map_entry, char_base, palette_list):
        """ GraphicsViewにマップを描画する

        :param map_entry:
        :param char_base:
        :param palette_list:
        """
        self.graphics_scene.clear()
        self.ui.bg1CheckBox.setChecked(True)
        self.ui.bg2CheckBox.setChecked(True)

        for entry_num, tile_entry in enumerate(split_by_size(self.bin_map_bg, 2)):
            bg_num = entry_num // (map_entry.width * map_entry.height)
            x = entry_num % map_entry.width * 8
            y = entry_num // map_entry.width % map_entry.height * 8
            item = TileItem(tile_entry, bg_num)

            if map_entry.color_mode == 0:
                char_base[item.tile_num].image.setColorTable(palette_list[item.palette_num].get_qcolors())

            tile_image = QtGui.QPixmap.fromImage(char_base[item.tile_num].image)
            if item.flip_h:
                tile_image = tile_image.transformed(QtGui.QTransform().scale(-1, 1))
            if item.flip_v:
                tile_image = tile_image.transformed(QtGui.QTransform().scale(1, -1))

            item.setPixmap(tile_image)
            item.setOffset(x, y)
            self.graphics_scene.addItem(item)

    def bg1_visible_changed(self, state: bool):
        """ BG1の表示切り替え
        """
        # self.graphics_group_bg1.setVisible(state)
        pass

    def bg2_visible_changed(self, state: bool):
        """ BG2の表示切り替え
        """
        # self.graphics_group_bg2.setVisible(state)
        pass

    def rubber_band_changed(self, select_rect):
        """

        :param select_rect:
        """
        items = self.ui.graphicsView.items(select_rect)
        LOGGER.debug(items)

    def save(self):
        """ ROMの保存
        """
        base = self.map_entry_list[91]
        LOGGER.debug(base)
        to = 0x900000
        self.bin_data = Common.write_bin(self.bin_data, to,
                                         base.bin_tilemap_entry + base.get_bin_tilemap_compressed(self.bin_data))
        self.bin_data = Common.write_bin(self.bin_data, base.tilemap_pointer,
                                         (to + settings.MEMORY_OFFSET).to_bytes(4, 'little'))

        with open('output/BR5J.gba', 'wb') as output_file:
            LOGGER.info('ファイルを保存しました。')
            output_file.write(self.bin_data)


class TileItem(QtWidgets.QGraphicsPixmapItem):
    """ TileItem

    """
    def __init__(self, bin_tile, bg_num):
        super().__init__()
        self.ItemIsSelectable = True
        self.bin_tile = bin_tile
        self.bg_num = bg_num

        attribute = bin(int.from_bytes(bin_tile, 'little'))[2:].zfill(16)
        self.palette_num = int(attribute[:4], 2)
        self.flip_v = bool(int(attribute[4], 2))
        self.flip_h = bool(int(attribute[5], 2))
        self.tile_num = int(attribute[6:], 2)

    def __str__(self):
        string = 'BG:\t' + str(self.bg_num) + '\n' \
                 'Palette:\t' + str(self.palette_num) + '\n' \
                 'Flip V:\t' + str(self.flip_v) + '\n' \
                 'Flip H:\t' + str(self.flip_h) + '\n' \
                 'Tile:\t' + str(self.tile_num) + '\n'
        return string

    def mousePressEvent(self, event):
        LOGGER.debug(self)


class ExeMapEntry:
    """ EXE Map Entry
    """
    def __init__(self, map_entry_offset, bin_rom_data):
        self.offset = map_entry_offset  # マップエントリ開始位置のアドレス
        self.tileset_pointer = map_entry_offset  # タイルセットのポインタのアドレス（＝エントリ開始位置）
        self.palette_pointer = map_entry_offset + 4  # パレットのポインタのアドレス
        self.tilemap_pointer = map_entry_offset + 8  # タイルマップのポインタのアドレス

        self.bin_map_entry = bin_rom_data[map_entry_offset:map_entry_offset+settings.MAP_ENTRY_SIZE]
        self.tileset, self.palette, self.tilemap = \
            [int.from_bytes(offset, 'little') - settings.MEMORY_OFFSET
             for offset in split_by_size(self.bin_map_entry, 4)]

        self.palette_offset = self.palette + 0x4

        self.tileset_offset_1 = self.tileset + 0x18
        self.tileset_offset_2 = self.tileset + int.from_bytes(
            bin_rom_data[self.tileset + 0x10: self.tileset + 0x14], 'little')

        self.bin_tilemap_entry = bin_rom_data[self.tilemap:self.tilemap + 0xC]
        self.width = bin_rom_data[self.tilemap]
        self.height = bin_rom_data[self.tilemap + 1]
        self.color_mode = bin_rom_data[self.tilemap + 2]  # おそらく（0: 16色、1: 256色）
        self.tilemap_offset = self.tilemap + 0xC

    def get_bin_tilemap(self, bin_rom_data):
        """ 非圧縮のタイルマップを取得する

        :param bin_rom_data:
        :return:
        """
        return LZ77Util.decompLZ77_10(bin_rom_data, self.tilemap_offset)

    def get_bin_tilemap_compressed(self, bin_rom_data):
        """ 圧縮したタイルマップを取得する

        :param bin_rom_data:
        :return:
        """
        tilemap = LZ77Util.decompLZ77_10(bin_rom_data, self.tilemap_offset)
        return compress.compress(tilemap)

    def __str__(self):
        string = 'Entry Offset:\t' + hex(self.offset) + '\n' +\
                 'Tile Set Entry:\t' + hex(self.tileset) + '\n' +\
                 'Palette Entry:\t' + hex(self.palette) + '\n' +\
                 'Tile Map Entry:\t' + hex(self.tilemap) + '\n' +\
                 'Width:\t' + str(self.width) + ' Tile\n' +\
                 'Height:\t' + str(self.height) + ' Tile\n' +\
                 'Tile Map Offset:\t' + hex(self.tilemap_offset)
        return string


def split_by_size(data, size):
    """ 文字列をn文字ずつに分割したリストを返す

    :param data:
    :param size:

    :return:
    """
    return [data[i:i+size] for i in [i for i in range(0, len(data), size)]]


if __name__ == '__main__':
    APP = QtWidgets.QApplication(sys.argv)
    WINDOW = ExeMap()
    WINDOW.show()
    sys.exit(APP.exec_())