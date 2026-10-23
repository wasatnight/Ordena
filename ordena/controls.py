"""Predictable, accessible inclusion controls; clicking a file name toggles it."""
from PySide6.QtCore import QEvent, Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QCheckBox, QStyledItemDelegate, QStyleOptionViewItem,
    QStyle, QApplication)
from .theme import ASSETS


class CategoryCheckBox(QCheckBox):
    def nextCheckState(self):
        # Partial is a summary of individual files, never a third user action.
        self.setCheckState(Qt.Unchecked if self.checkState() == Qt.Checked else Qt.Checked)

    def hitButton(self, position):
        return self.rect().contains(position)


class FileDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.on_icon = QIcon(str(ASSETS / 'check-on.svg'))
        self.off_icon = QIcon(str(ASSETS / 'check-off.svg'))

    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.state &= ~QStyle.State_HasFocus
        state = index.data(Qt.CheckStateRole)
        if index.column() == 0 and state is not None:
            opt.features &= ~QStyleOptionViewItem.HasCheckIndicator
            opt.features |= QStyleOptionViewItem.HasDecoration
            opt.decorationSize = QSize(20, 20)
            opt.decorationAlignment = Qt.AlignCenter
            opt.icon = self.on_icon if state == Qt.Checked.value else self.off_icon
        style = opt.widget.style() if opt.widget else QApplication.style()
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter, opt.widget)

    def editorEvent(self, event, model, option, index):
        if (index.column() == 0 and index.flags() & Qt.ItemIsEnabled
                and index.flags() & Qt.ItemIsUserCheckable):
            mouse = event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton
            keyboard = event.type() == QEvent.KeyPress and event.key() in (Qt.Key_Space, Qt.Key_Select)
            if mouse or keyboard:
                value = Qt.Unchecked if index.data(Qt.CheckStateRole) == Qt.Checked.value else Qt.Checked
                return model.setData(index, value, Qt.CheckStateRole)
            if event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonDblClick):
                return True
        return super().editorEvent(event, model, option, index)
