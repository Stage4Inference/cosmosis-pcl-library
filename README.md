# cosmosis-pcl-library

This repository contains modules from the cosmosis-standard-library that were modified to run an analysis with Pseudo-Cl's.

To use this library you will need to install the [pymaster](https://namaster.readthedocs.io/en/latest/api/pymaster.workspaces.html) package.

## CosmoSIS modules
The modified CosmoSIS modules have a path similar to the one you can find in the cosmosis-standard-library so that in the path pointing to the modules in your ini file you only need to change cosmosis-standard-library to cosmosis-pcl-library.

The modules that were modified are :
 - structure/projection/project_2d.py : The ouput Cl's from this module can now be Pseudo-Cl's coupled thourgh a mixing matrix given as an input. See the project_2d.yaml for a description of the new parameters. All the other files in the structure directory haven't been changed.
 The Cl ingested by the coupling function is the regular output of project_2d.py, i.e it is computed at the ell's defined in the project_2d.py module. However to couple the Cl the full unbinned Cl (up to 2*NSIDE_mask) is needed. There is a function in this modified module which interpolates the regular output before coupling to have the Cl at all ell. ** So, remember that the ell binning defined in project_2d needs to be fine enough so that the interpolation is not too bad.** You can also compute the Cl's at all ell (using the linspaced binning) but it will take more time. This also means that the binning defined project_2d.py is not the binning you will have in output as the pseudo-Cl is binned with the NaMaster workspace.

 - likelihood/2pt/save_2pt.py : This module was modified to bin the Cl's and the covariance saved in the 2pt files using the binning object stored in the NaMaster workspace given as input. Note that the covariance computed in this module is not the partial-sky covariance accounting for mode coupling, it is still the simple full-sky divided by $f_\mathrm{sky}$ covariance (also called the Knox approximation). Only the binning is different. See the save_2pt.yaml for a description of the new parameters. All the other files in the likelihood directory haven't been changed.
 The only change made to this directory (apart from the modification to save_2pt.py) is the addition of the legendre.py module (which is normally located in cosmosis-standard-library/shear/cl_to_xi_fullsky) as it is used in spec_tools.py.

## Scripts
In the scripts directory you can find a script to generate and save a NaMaster workspace for a given binning and mask. This workspace contains the mixing matrix for a given combination of field of spin 0 or 2 (for example galaxy positions is a spin-0 field while shear is a spin-2 field). See the [NaMaster documentation](https://namaster.readthedocs.io/en/latest/api/pymaster.workspaces.html) for more details.


## Example
In the example directory you can find an example ini file simulating a set weak lensing pseudo-Cl's for 2 tomographic bins. To run it you first need to generate a NaMaster workspace fits file with the create_nmt_workspace.py, with an arbitrary mask as an input.