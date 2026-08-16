# Run PyMOL from the directory containing 4DFR.pdb and MTX_redocked.sdf,
# or edit the file paths below.
load 4DFR.pdb, crystal
load MTX_redocked.sdf, redocked

hide everything
show cartoon, crystal and chain A and polymer
color gray70, crystal and chain A and polymer

select crystal_mtx_A, crystal and chain A and resn MTX
show sticks, crystal_mtx_A
color cyan, crystal_mtx_A

show sticks, redocked
color magenta, redocked

zoom crystal_mtx_A, 8
set state, 3

# Save a reproducible PyMOL session after visual checking.
# save 4DFR_redocking_analysis.pse
