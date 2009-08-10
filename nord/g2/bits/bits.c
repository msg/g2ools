#define PY_SSIZE_T_CLEAN
#include <stdarg.h>
#include <Python.h>
#include <structmember.h>

struct arrayobject;

struct arraydescr {
  int typecode;
  int itemsize;
  PyObject * (*getitem)(struct arrayobject *, int);
  int (*setitem)(struct arrayobject *, int, PyObject *);
};

typedef struct arrayobject {
  PyObject_VAR_HEAD
  char *ob_item;
  int allocated;
  struct arraydescr *ob_descr;
  PyObject *weakreflist;
} arrayobject;

static PyObject *ErrorObject;

static void
error(char *fmt, ...)
{
  char buf[256];
  va_list ap;
  va_start(ap, fmt);
  vsprintf(buf, fmt, ap);
  PyErr_SetString(ErrorObject, buf);
}

static const unsigned short crc_table[256] = {
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
    0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
    0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
    0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
    0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
    0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
    0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
    0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
    0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
    0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
    0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
    0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
    0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
    0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
    0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
    0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
    0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
    0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
    0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
    0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
    0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
    0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
    0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
    0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
    0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
    0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
    0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
    0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
    0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
    0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
    0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
    0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0
};

short crc_update(short crc, const unsigned char *data, size_t data_len)
{
    unsigned int tbl_idx;

    while (data_len--) {
        tbl_idx = ((crc >> 8) ^ *data) & 0xff;
        crc = (crc_table[tbl_idx] ^ (crc << 8)) & 0xffff;

        data++;
    }
    return crc & 0xffff;
}

static inline int bswap32(int x) {
  return ((x&0xff000000) >> 24) |
         ((x&0x00ff0000) >>  8) |
	 ((x&0x0000ff00) >>  8) |
	 ((x&0x000000ff) << 24);
}

static inline short bswap16(short x) {
  return ((x&0xff00) >> 8) | ((x&0x00ff) << 8);
}

static inline int getbits(int x, int p, int n)
{
  return (x >> p) & ~(~0 << n);
}

static inline int setbits(int x, int p, int n, int y)
{
  int m = ~(~0 << n);
  return (x & ~(m << p)) | ((m & y) << p);
}

PyDoc_STRVAR(crc__doc__,
"crc(string) -> crc\n\
\n\
Calculate the crc of a string used in the nord g2 pch2 and prf2 files.");

static PyObject *
crc(PyObject *self, PyObject *args)
{
  char *s;
  int l;
  unsigned short ccrc;

  if(!PyArg_ParseTuple(args, "s#", &s, &l)) {
    return NULL;
  }
  ccrc = crc_update(0, s, l);
  return Py_BuildValue("i", ccrc);
}

PyDoc_STRVAR(pysetbits__doc__,
"setbits(bit,nbits,array,value) -> bit+nbit\n\
\n\
Set from 'bit' to 'bit+nbit' within 'array' (python array module) to\n\
value and return the 'bit+nbit'.  It can only handle 'bits'+'nbits' <= 16\n\
as the bit area is converted to a 16-bit number, set, and stored\n\
into 'array'.  The 'array' is assumed large enough to handle\n\
'(bit+nbits)/8' characters.  The numbers are processed as big-endian\n\
as that is the storage format within a g2 pch2 or prf2 file.");

static PyObject *
pysetbits(PyObject *self, PyObject *args)
{
  int bit, nbits, value, byte;
  short *sp;
  arrayobject *array;
  char *ap;
  int l;
  if(!PyArg_ParseTuple(args, "iiOi", &bit, &nbits, &array, &value)) {
    return NULL;
  }
  ap = array->ob_item;
  l = array->ob_size;
  byte = bit >> 3;
  sp = (short *)(ap + byte);
  /* zero low bits (big-endian) because array may have junk */
  *sp = bswap16(setbits(bswap16(*sp), 0, 16-(bit&7)-nbits, 0));
  *sp = bswap16(setbits(bswap16(*sp), 16-(bit&7)-nbits, nbits, value));
  return Py_BuildValue("i", bit+nbits);
}

PyDoc_STRVAR(pygetbits__doc__,
"getbits(bit,nbits,string,signed=0) -> (bit+nbit, value)\n\
\n\
Get from 'bit' to 'bit+nbit' within 'string'\n\
return the 'bit+nbit' and 'value' as a tuple.  It can only handle a\n\
'bits'+'nbits' <= 16 as the bit area is converted to a 16-bit number\n\
from 'array'.  The 'array' is assumed large enough to handle\n\
'(bit+nbits)/8' characters.  The numbers are processed as big-endian\n\
as that is the storage format within a g2 pch2 or prf2 file. If\n\
signed is non-zero, the value will handle sign bit.");

static PyObject *
pygetbits(PyObject *self, PyObject *args)
{
  int bit, nbits, sign=0, value, byte;
  short *sp;
  char *ap;
  int l;
  if(!PyArg_ParseTuple(args, "iis#|i", &bit, &nbits, &ap, &l, &sign)) {
    return NULL;
  }
  byte = bit >> 3;
  sp = (short *)(ap + byte);
  value = getbits(bswap16(*sp),16-(bit&7)-nbits,nbits);
  if (sign) {
    value |= ~0 << nbits;
  }
  return Py_BuildValue("ii", bit+nbits, value);
}

static PyMethodDef G2BitsMethods[] = {
  { "crc", crc, METH_VARARGS, crc__doc__ },
  { "setbits", pysetbits, METH_VARARGS, pysetbits__doc__ },
  { "getbits", pygetbits, METH_VARARGS, pygetbits__doc__ }, 
  { NULL, NULL, 0, NULL } /* Sentinel */
};

/* PyMODINIT_FUNC */
void
initbits(void)
{
  PyObject *m;

  m = Py_InitModule("bits", G2BitsMethods);

  ErrorObject = PyErr_NewException("bits.error", NULL, NULL);
  Py_INCREF(ErrorObject);
  PyModule_AddObject(m, "error", ErrorObject);
}

