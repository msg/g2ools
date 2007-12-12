
from distutils.core import setup, Extension
#from numpy.distutils.core import setup, Extension

module = Extension('bits', sources = ['bits.c'])

setup (name = 'G2 Bit Processing',
       version = '1.0',
       description = 'Nord G2 File Bit Processing',
       ext_modules = [module])
