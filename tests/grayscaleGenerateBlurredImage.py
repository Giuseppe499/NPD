"""
NPD implementation

Copyright (C) 2023 Giuseppe Scarlato

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PIL import Image
import numpy as np
from numpy.linalg import norm
from mathExtras import fftConvolve2D, generatePsfMatrix

IMGPATH = "cameraman.tif"

if __name__ == '__main__':
    image = Image.open(IMGPATH)
    image = np.asarray(image) / 255
    image = image[::2, ::2]
    n = image.shape[0]
    print(image.shape)

    # Generate PSF
    psf = generatePsfMatrix(n, 4)
    # Center PSF
    psf = np.roll(psf, (-psf.shape[0] // 2, -psf.shape[0] // 2), axis=(0, 1))
    # Generate noise
    noise = np.random.normal(size=image.shape)
    noise *= 0.01 * norm(image) / norm(noise)
    # Generate blurred image
    conv = fftConvolve2D(image, psf)

    # Add noise to blurred image
    b = np.clip(conv + noise, 0, 1)

    np.savez('./grayscaleBlurred.npz', b=b, psf=psf, image=image)