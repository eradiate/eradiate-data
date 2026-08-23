# Particle field tutorial data

Example datasets for `docs/tutorials/advanced/particle_field/particle_field.ipynb`.

- `shallow_convection-ppr_v1.nc`: one time step of a UCLA-LES large-eddy
  simulation of shallow cumulus convection (25 m horizontal grid spacing,
  256x256 points, 120 stretched vertical layers, 10 s output interval),
  thresholded on liquid water content and reformatted to the Ppr v1
  particle profile format.
  Source: Jakub, F. and Gregor, P. (2022): *UCLA-LES shallow cumulus
  dataset with 3D cloud output data*. LMU Munich, Faculty of Physics
  (Dataset). doi:10.57970/5d0k9-q2n86,
  https://opendata.physik.lmu.de/5d0k9-q2n86/
- `watercloud_670-prt_v1.nc`: water cloud droplet optical properties at
  670 nm (gamma size distribution, 25 `reff` values), from the IPRT
  (International Polarized Radiative Transfer model intercomparison
  project) Case C3 "Cumulus cloud" (Phase C):
  https://www.libradtran.org/iprt/doku.php?id=intercomparisons:c3_cumulus
  (original file: `watercloud_670.mie.cdf`). The IPRT project is described
  in Emde et al. 2015, J. Quant. Spectrosc. Radiat. Transfer, 164, 8-36
  (Phase A) and Emde et al. 2018, J. Quant. Spectrosc. Radiat. Transfer,
  209, 19-44 (Phase B). Reformatted to the Prt v1 particle properties
  format.

See each file's `source` attribute for the same information.
