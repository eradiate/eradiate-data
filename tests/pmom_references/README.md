# Legendre coefficient references

This file contains Legendre coefficient reference values used to test the Python
reimplementation of libRadtran's `pmom` tool. They are computed using `pmom`
(in C, built on a Linux machine). Three phase functions are considered for this
dataset:

- The Rayleigh phase function
- The Henyey-Greenstein phase function with an asymmetry parameter of 0.5
- The Henyey-Greenstein phase function with an asymmetry parameter of 0.85

These files can be read with Numpy's `loadtxt()` function.
