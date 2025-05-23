import numpy as np
from PySide6.QtGui import QImage

def to_QImage(ndarray: np.ndarray):
    if len(ndarray.shape) == 2:
        height, width = ndarray.shape
        channels = 1
    else:
        height, width, channels = ndarray.shape

    if channels == 1:
        qimage = QImage(ndarray.data, width, height, width, QImage.Format_Grayscale8)
    elif channels == 3:
        qimage = QImage(ndarray.data, width, height, 3 * width, QImage.Format_RGB888).rgbSwapped()
    elif channels == 4:
        qimage = QImage(ndarray.data, width, height, 4 * width, QImage.Format_RGBA8888).rgbSwapped()
    else:
        raise ValueError("Unsupported number of channels")

    return qimage

def cn_to_format(cn):
    if cn == 1:
        return QImage.Format_Grayscale8
    elif cn == 3:
        return QImage.Format_BGR888
    elif cn == 4:
        return QImage.Format_BGRA8888
    else:
        raise ValueError("Unsupported number of channels")