""" EXE Map
"""
# pylint: disable=c-extension-no-member

# import os
import logging
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import UI_ExeMap as designer
import CommonAction as common
# import compress
import LZ77Util


stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


PROGRAM_NAME = "EXE MAP  ver 0.7"
MEMORY_OFFSET = 0x8000000
MAP_SIZE = 144
MAP_ENTRY_START = 0x339dc
MAP_ENTRY_END = 0x33F28
TILE_DATA_SIZE_16 = 0x20    # 16色タイルのデータサイズ
TILE_DATA_SIZE_256 = 0x40   # 256色タイルのデータサイズ


class ExeMap(QtWidgets.QMainWindow):
    """ EXE Map
    """
    def __init__(self, parent=None):
        """ init
        """
        super(ExeMap, self).__init__(parent)
        self.ui = designer.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(PROGRAM_NAME)
        self.graphics_scene = QtWidgets.QGraphicsScene(self)
        self.ui.graphicsView.setScene(self.graphics_scene)
        self.ui.graphicsView.scale(1, 1)
        self.graphics_group_bg1 = QtWidgets.QGraphicsItemGroup()
        self.graphics_group_bg2 = QtWidgets.QGraphicsItemGroup()

        with open('ROCKEXE6_GXX.gba', 'rb') as bin_file:
            self.bin_data = bin_file.read()

        self.map_entry_list = self.init_map_entry_list()
        self.draw(self.map_entry_list[0])

    def init_map_entry_list(self):
        """ マップリストの初期化
        """
        map_entries = split_by_size(self.bin_data[MAP_ENTRY_START:MAP_ENTRY_END], 0xC)
        map_entry_list = []
        self.ui.mapList.clear()

        for bin_map_entry in map_entries:
            tileset = int.from_bytes(bin_map_entry[0:4], 'little')
            if tileset == 0:  # テーブル内に電脳とインターネットの区切りがあるので除去
                continue

            map_entry = ExeMapEntry(bin_map_entry, self.bin_data)
            map_entry_list.append(map_entry)
            item = QtWidgets.QListWidgetItem(hex(map_entry.tilemap))
            self.ui.mapList.addItem(item)

        return map_entry_list

    def map_entry_selected(self):
        """ マップリストのアイテムがダブルクリックされたときの処理
        """
        index = self.ui.mapList.currentRow()
        self.draw(self.map_entry_list[index])

    def draw(self, map_entry):
        """ マップの描画
        """
        self.graphics_scene.clear()

        # パレットの更新
        bin_palette = self.bin_data[map_entry.palette_offset: map_entry.palette_offset+0x200]
        palette_list = []
        if map_entry.color_mode == 0:
            for bin_palette in split_by_size(bin_palette, 0x20):
                palette_list.append(common.GbaPalette(bin_palette))
        elif map_entry.color_mode == 1:
            palette_list.append(common.GbaPalette(bin_palette, 256))

        # GUIのパレットテーブルの更新
        self.ui.paletteTable.clear()
        for row, palette in enumerate(palette_list):
            for col, color in enumerate(palette.color):
                item = QtWidgets.QTableWidgetItem()
                brush = QtGui.QBrush(QtGui.QColor(color.r, color.g, color.b))
                brush.setStyle(QtCore.Qt.SolidPattern)
                item.setBackground(brush)
                if map_entry.color_mode == 0:
                    self.ui.paletteTable.setItem(row, col % 16, item)
                elif map_entry.color_mode == 1:
                    self.ui.paletteTable.setItem(col // 16, col % 16, item)

        # タイルの処理
        bin_tileset_1 = LZ77Util.decompLZ77_10(self.bin_data, map_entry.tileset_offset_1)
        bin_tileset_2 = LZ77Util.decompLZ77_10(self.bin_data, map_entry.tileset_offset_2)
        bin_tileset = bin_tileset_1 + bin_tileset_2
        char_base = []

        if map_entry.color_mode == 0:
            for bin_char in split_by_size(bin_tileset, TILE_DATA_SIZE_16):
                char_base.append(common.GbaTile(bin_char))
        elif map_entry.color_mode == 1:
            for bin_char in split_by_size(bin_tileset, TILE_DATA_SIZE_256):
                char_base.append(common.GbaTile(bin_char, 256))

        for i, char in enumerate(char_base):
            # タイルセットリストの表示
            item = QtWidgets.QTableWidgetItem()
            if map_entry.color_mode == 0:
                char.image.setColorTable(palette_list[1].get_qcolors())
            elif map_entry.color_mode == 1:
                char.image.setColorTable(palette_list[0].get_qcolors())
            tile_image = QtGui.QPixmap.fromImage(char.image)
            item.setIcon(QtGui.QIcon(tile_image))
            self.ui.tilesetTable.setItem(i // 16, i % 16, item)

        bin_map_bg = LZ77Util.decompLZ77_10(self.bin_data, map_entry.tilemap_offset)
        self.graphics_group_bg1 = QtWidgets.QGraphicsItemGroup()
        self.graphics_group_bg2 = QtWidgets.QGraphicsItemGroup()
        for i, tile_entry in enumerate(split_by_size(bin_map_bg, 2)):
            # タイルマップに基づいてタイルを描画
            attribute = bin(int.from_bytes(tile_entry, 'little'))[2:].zfill(16)
            palette_num = int(attribute[:4], 2)
            flip_v = int(attribute[4], 2)
            flip_h = int(attribute[5], 2)
            tile_num = int(attribute[6:], 2)

            if map_entry.color_mode == 0:
                char_base[tile_num].image.setColorTable(palette_list[palette_num].get_qcolors())

            tile_image = QtGui.QPixmap.fromImage(char_base[tile_num].image)
            if flip_h == 1:
                tile_image = tile_image.transformed(QtGui.QTransform().scale(-1, 1))
            if flip_v == 1:
                tile_image = tile_image.transformed(QtGui.QTransform().scale(1, -1))
            item = QtWidgets.QGraphicsPixmapItem(tile_image)
            item.ItemIsSelectable = True
            item.ItemIsMovable = True
            item.setOffset(i % map_entry.width * 8, i // map_entry.width % map_entry.height * 8)
            bg = i // (map_entry.width * map_entry.height)
            if bg == 0:
                self.graphics_group_bg1.addToGroup(item)
            elif bg == 1:
                self.graphics_group_bg2.addToGroup(item)

        self.graphics_scene.addItem(self.graphics_group_bg1)
        self.graphics_scene.addItem(self.graphics_group_bg2)

    def bg1_visible_changed(self, state):
        """ BG1の表示切り替え
        """
        self.graphics_group_bg1.setVisible(state)

    def bg2_visible_changed(self, state):
        """ BG2の表示切り替え
        """
        self.graphics_group_bg2.setVisible(state)

    def movement_visible_changed(self):
        """

        :return:
        """
        pass

    def rubber_band_changed(self, select_rect):
        """

        :param select_rect:
        :return:
        """
        items = self.ui.graphicsView.items(select_rect)
        logger.debug(items)


class ExeMapEntry:
    """ EXE Map Entry
    """
    def __init__(self, bin_map_entry, bin_rom_data):
        self.bin_map_entry = bin_map_entry
        tileset, palette, tilemap = [int.from_bytes(offset, 'little')
                                     for offset in split_by_size(bin_map_entry, 4)]

        self.tileset = tileset - MEMORY_OFFSET
        self.tilemap = tilemap - MEMORY_OFFSET
        self.palette = palette - MEMORY_OFFSET

        self.width = bin_rom_data[self.tilemap]
        self.height = bin_rom_data[self.tilemap + 1]
        self.palette_offset = self.palette + 0x4
        self.tileset_offset_1 = self.tileset + 0x18
        self.tileset_offset_2 = self.tileset + int.from_bytes(
            bin_rom_data[self.tileset + 0x10: self.tileset + 0x14], 'little')
        self.color_mode = bin_rom_data[self.tilemap + 2]  # おそらく（0: 16色、1: 256色）
        self.tilemap_offset = self.tilemap + 0xC


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
