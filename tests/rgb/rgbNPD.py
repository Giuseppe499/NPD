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

import numpy as np
from numpy.linalg import norm
from numpy.fft import fft2
from mathExtras import (sInner, gradLeastSquaresRGB, grad2Drgb, div2Drgb, proxhsTVrgb,
                        fftConvolve2Drgb)
from solvers import NPD

if __name__ == '__main__':
    with np.load('rgbBlurred.npz') as data:
        b = data['b']
        psf = data['psf']
        image = data['image']
        noiseNormSqd = data['noiseNormSqd']

    maxIt = 200 # Maximum number of iterations
    tol = noiseNormSqd  # Tolerance
    lam = 1e-3  # TV regularization parameter
    pStep = 1  # Primal step length
    dStep = 1 / 8  # Dual step length

    # Compute FFT of b and psf
    bFFT = np.zeros(b.shape, dtype=complex)
    for i in range(3):
        bFFT[:, :, i] = fft2(b[:, :, i])
    psfFFT = fft2(psf)
    psfFFTC=np.conjugate(psfFFT)
    
    imRec, rreList = NPD(x0=b,
                         gradf=lambda x: gradLeastSquaresRGB(x, bFFT,
                                                          psfFFT,
                                                          psfFFTC),
                         proxhs=lambda alpha, x: proxhsTVrgb(lam, x),
                         mulW=grad2Drgb,
                         mulWT=div2Drgb,
                         f=lambda x: sInner(
                             (fftConvolve2Drgb(x, psf) - b).ravel()),
                         h=lambda y: lam * norm(y.ravel(), 1),
                         pStep=pStep, dStep=dStep, maxit=maxIt, tol=tol, dp = 1.01,
                         xOrig=image)

    np.savez("./rgbNPD.npz", imRec=imRec, rreList=rreList)
