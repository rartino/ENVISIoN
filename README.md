ENVISIoN (ElectroN VISualization for INviwo) is an open source tool/toolkit for electron visualization.

ENVISIoN is implemented using (a modified version of) the Inviwo visualization framework, developed at the Scientific Visualization Group at Linköping University (LiU).

The initial version was developed as part of the course TFYA75: Applied Physics - Bachelor Project, given at Linköping University, Sweden (LiU) spring term 2017. The title of the final report was: "Design och implementing av en interakiv visualisering av elektronstrukturdata". Authors: Josef Adamsson, Robert Cranston, David Hartman, Denise Härnström, Fredrik Segerhammar. The project was supervised by Johan Jönsson (main supervisor), Rickard Armiento (expert and client), and Peter Steneteg (expert). The course examinator was Per Sandström.

ENVISoN is build on the support for Python scripting in Inviwo. It provides a set of python routines that allows a user with just a few simple commands to:
  - Read and parse output from electronic structure codes (presently VASP, and some support for Elk is implemented)
  - Put together interactive Inviwo visualization networks for
    visualization tasks common in electronic structure. Presently there
    is (to varying degree) some support for crystal structures, ab-inito
    molecular dynamics, ELF, DOS/pDOS and band structure plots.
