#!/usr/bin/python
#
# Copyright (c) 2006,2007 Matt Gerassimoff
#
# This file is part of g2ools.
#
# g2ools is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# g2ools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import sys
from PyQt4.Qt import *

from nm2g2g_ui import Ui_NM2G2G

sys.setcheckinterval(10)

class ConvertThread(QThread):
  def __init__(self,main):
    QThread.__init__(self)
    self.main = main
    self.connect(self, SIGNAL('write'), self.main.write)

  def run(self):
    self.str = ''
    script=open('nm2g2.py').read()
    globs = globals()
    exec 'from nm2g2 import *' in globs
    logging = globs['logging']
    logging.basicConfig(stream=self, format='%(message)s')
    main(['nm2g2.py','-v0','-r']+self.files)
    logging.critical('Convertion finished.')
    self.exit(0)
  
  def write(self, s):
    #c = s.find(':')
    #if c < 0:
    #  pass
    #elif '---' == s[:3]:
    #  s = '<b>'+s+'</b>'
    #elif 'Writing Patch' == s[:13]:
    #  s = s[:13]+' <b>'+s[15:]+'</b>'
    #else:
    #  s = '<b>'+s[:c+1]+'</b>'+s[c+1:]
    #s += '<br>'
    self.str += s

  def flush(self):
    self.emit(SIGNAL('write'), self.str)
    self.str = ''

class CheckableDirModel(QDirModel):
  def __init__(self, *args):
    self.checkmap = {}
    QDirModel.__init__(self, *args)
    self.setResolveSymlinks(False)

  def hasSiblings(self, index):
    if index.row() == 0:
      return QDirModel.index(self, index.row()+1, index.column(), index.parent()).isValid()
    else:
      return True

  def flags(self, index):
    return QDirModel.flags(self, index)|\
        Qt.ItemIsUserCheckable|Qt.ItemIsTristate

  def setData(self, index, value, role=Qt.DisplayRole):
    if index.isValid():
      id = self.filePath(index)
      checked = self.checkmap[id] = value.toInt()[0]
      self.emit(SIGNAL('dataChanged(const QModelIndex&, const QModelIndex&)'), index, index)
      self.emit(SIGNAL('selectionChanged()'))
      return True
    return False

  def data(self, index, role=Qt.DisplayRole):
    if role == Qt.CheckStateRole and \
       index.isValid() and \
       index.column() == 0:
      id = self.filePath(index)
      if self.checkmap.has_key(id):
        return QVariant(self.checkmap[id])
      return QVariant(Qt.Unchecked)
    return QDirModel.data(self, index, role)

class NM2G2G(QMainWindow):
  def __init__(self, parent=None):
    QMainWindow.__init__(self, parent)

    self.ui = Ui_NM2G2G()
    self.ui.setupUi(self)

    self.dirmodel = CheckableDirModel()
    self.dirmodel.setSorting(QDir.Name|QDir.DirsFirst)
    tree = self.ui.treeView
    tree.setModel(self.dirmodel)
    tree.setRootIndex(self.dirmodel.index(QDir.currentPath()))
    tree.resizeColumnToContents(0)

    self.guimutex = QMutex()
    self.convert = ConvertThread(self)

  @pyqtSignature('bool')
  def on_action_Quit_triggered(self, checked):
    self.close()

  @pyqtSignature('bool')
  def on_action_Run_triggered(self, checked):
    cm = self.dirmodel.checkmap
    files = [ str(k) for k in self.dirmodel.checkmap.keys() if cm[k] ]
    files.sort()
    self.ui.textEdit.document().clear()
    self.convert.files = files
    self.convert.start()

  def write(self, s):
    #self.ui.textEdit.insertHtml(s)
    self.ui.textEdit.insertPlainText(s)
    self.ui.textEdit.ensureCursorVisible()
    
if __name__ == "__main__":
  app = QApplication(sys.argv)
  nm2g2g = NM2G2G()
  nm2g2g.show()
  sys.exit(app.exec_())

