""" ChatGPT generated header
Script Header:
This script demonstrates the computation of a coupling matrix for pseudo-Cl power spectrum estimation
using the Namaster library.

Author: Sylvain Gouyou Beauchamps

Date: 02/29/2024

Description:
This script reads a binary mask file defining the regions of the sky, generates a binning
scheme with a minimum multipole of 10 and a bin width of 5, computes the coupling matrix using
Namaster's NmtField and NmtWorkspace objects, and writes the workspace to a file.

Dependencies:
- Python 3.x
- healpy
- Namaster library
- utils.py module (located in the '../lib' directory)

Usage:
python workspace_from_mask.py

Inputs:
- '../input/fullsky_mask_binary_NS32.fits': Input binary mask file.
- '../input/fullsky_NmtWorkspace_NS32_LMIN10_BW5.fits': Output file for the computed coupling matrix.

Outputs:
- The computed coupling matrix is saved in the specified output file.

"""
import healpy as hp
import pymaster as nmt
import numpy as np

import os
import time

def coupling_matrix(bin_scheme, mask, wkspce_name, spin1, spin2):
    """
    Compute the coupling matrix for spherical harmonic modes using a binning scheme and mask.

    Parameters
    ----------
    bin_scheme : nmt_bins
        A binning scheme object defining the bins for the coupling matrix.
    mask : nmt_field
        A mask object defining the regions of the sky to include in the computation.
    wkspce_name : str
        The filename for storing or retrieving the computed workspace.
    spin1 : int
        Spin of the first field.
    spin2 : int
        Spin of the second field.

    Returns
    -------
    nmt_workspace
        Workspace object containing the computed coupling matrix.
    """
    print('Compute the mixing matrix')
    start = time.time()
    fmask1 = nmt.NmtField(mask, None, lmax=bin_scheme.lmax, spin=spin1) # nmt field with only the mask
    fmask2 = nmt.NmtField(mask, None, lmax=bin_scheme.lmax, spin=spin2) # nmt field with only the mask
    w = nmt.NmtWorkspace()
    if os.path.isfile(wkspce_name):
        print('Mixing matrix has already been calculated and is in the workspace file : ', wkspce_name, '. Read it.')
        w.read_from(wkspce_name)
    else :
        print('The file : ', wkspce_name, ' does not exists. Calculating the mixing matrix and writing it.')
        w.compute_coupling_matrix(fmask1, fmask2, bin_scheme)
        w.write_to(wkspce_name)
    print('Done computing the mixing matrix. It took ', time.time()-start, 's.')
    return w

def linear_binning(lmax, lmin, bw):
    """
    Define a linear ell binning scheme.

    Parameters
    ----------
    lmax : int
        Maximum ell value for the binning.
    lmin : int
        Minimum ell value for the binning.
    bw : int
        Bin width for the ell values.

    Returns
    -------
    b : nmt.NmtBin
        NaMaster binning object with linear bins.
    """
    nbl = (lmax - lmin) // bw + 1
    elli = np.arange(lmin, lmin + nbl * bw, bw)
    elle = elli + bw
    b = nmt.NmtBin.from_edges(elli, elle)
    return b

def log_binning(lmax, lmin, nbl, w=None):
    """
    Define a logarithmic ell binning scheme with optional weights.

    Parameters
    ----------
    lmax : int
        Maximum ell value for the binning.
    lmin : int
        Minimum ell value for the binning.
    nbl : int
        Number of bins.
    w : array-like, optional
        Weights for the ell values.

    Returns
    -------
    b : nmt.NmtBin
        NaMaster binning object with logarithmic bins.
    """
    op = np.log10
    inv = lambda x: 10**x
    bins = inv(np.linspace(op(lmin), op(lmax + 1), nbl + 1))
    ell = np.arange(lmin, lmax + 1)
    i = np.digitize(ell, bins) - 1
    if w is None:
        w = np.ones(ell.size)
    b = nmt.NmtBin(bpws=i, ells=ell, weights=w, lmax=lmax)
    return b

import argparse

parser = argparse.ArgumentParser(description='Generates a NaMaster workspace given a binning and a mask')
parser.add_argument('--mask', dest='mask', type=str, required=True,
                    help='Path to the mask')
parser.add_argument('--lmin', dest='lmin', type=float, required=True,
                    help='Minimum multipole')
parser.add_argument('--lmax', dest='lmax', type=float, required=True,
                    help='Maximum multipole')
parser.add_argument('--nell', dest='nell', type=int, required=True,
                    help='Number of ell bins for the log binning')
parser.add_argument('--bin-width', dest='bin_width', type=int, required=True,
                    help='Width of the bins for the linear binning')
parser.add_argument('--binning', dest='binning', type=str, required=True,
                    help='Type of binning : log or lin.', choices=['log', 'lin'])
parser.add_argument('--spin', dest='spin', type=str, required=True,
                    help='Spins of the fields. 0-0 is for position-position,\
                        0-2 is for position-shear and 2-2 is for shear-shear',
                        choices=['0-0', '0-2', '2-2'])

args = parser.parse_args()
dictargs = vars(args)

print("-----------------**  ARGUMENTS  **------------------------")
for keys in dictargs.keys():
    print(keys, " = ", dictargs[keys])

# Load mask file
mask = hp.read_map(dictargs['mask'])

# Compute NSIDE from mask
NSIDE = hp.npix2nside(mask.size)
print('NSIDE = ', NSIDE)

if dictargs['binning'] == 'lin':
    binning = linear_binning(dictargs['lmax'], dictargs['lmin'], dictargs['bin_width'])
elif dictargs['binning'] == 'log':
    binning = log_binning(dictargs['lmax'], dictargs['lmin'], dictargs['nell'])
else:
    raise KeyError('Binning should be lin or log.')

# Compute coupling matrix and save to file
if dictargs['spin'] == '0-0':
    w_fname = '../output/nmt_workspace_galaxy_cl.fits'
    w = coupling_matrix(binning, mask, w_fname, 0, 0)
elif dictargs['spin'] == '0-2':
    w_fname = '../output/nmt_workspace_galaxy_shear_cl.fits'
    w = coupling_matrix(binning, mask, w_fname, 0, 2)
elif dictargs['spin'] == '2-2':
    w_fname = '../output/nmt_workspace_shear_cl.fits'
    w = coupling_matrix(binning, mask, w_fname, 2, 2)
else:
    raise KeyError('Spins should be 0-0, 0-2 or 2-2.')

