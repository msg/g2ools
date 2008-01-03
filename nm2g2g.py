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

import os, sys
from PyQt4.Qt import *
from PyQt4 import uic

sys.setcheckinterval(10)

class ConvertThread(QThread):
  def __init__(self, main):
    QThread.__init__(self)
    self.main = main
    self.connect(self, SIGNAL('write'), self.main.write)

  def run(self):
    self.str = ''
    g2oolsdir = os.path.dirname(sys.argv[0])
    prog = os.path.join(g2oolsdir, 'nm2g2.py')
    sys.path.append(g2oolsdir)
    script=open(prog).read()
    globs = globals()
    exec 'from nm2g2 import *' in globs
    nm2g2log = main([prog ,'-r']+self.files, self)
    nm2g2log.error('Convertion Finished.')
    self.exit(0)
  
  def write(self, s):
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

form_class, base_class = uic.loadUiType("nm2g2g.ui")

class NM2G2G(QMainWindow, form_class):
  def __init__(self, parent=None):
    QMainWindow.__init__(self, parent)

    self.setupUi(self)

    self.dirmodel = CheckableDirModel()
    self.dirmodel.setSorting(QDir.Name|QDir.DirsFirst)
    tree = self.treeView
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
    self.textEdit.document().clear()
    self.convert.files = files
    self.convert.start()

  @pyqtSignature('bool')
  def on_action_Stop_triggered(self, checked):
    global maindone
    maindone = True

  def write(self, s):
    #self.ui.textEdit.insertHtml(s)
    self.textEdit.insertPlainText(s)
    self.textEdit.ensureCursorVisible()
    
if __name__ == "__main__":
  app = QApplication(sys.argv)
  nm2g2g = NM2G2G()
  nm2g2g.show()
  sys.exit(app.exec_())

