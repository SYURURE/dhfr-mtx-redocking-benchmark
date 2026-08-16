# Run PyMOL from a directory containing the downloaded 1U72 inputs and output.
load 1U72.pdb, human_dhfr
load 1U72_MTX_crystal.sdf, crystal_mtx
load 1U72_MTX_redocked.sdf, redocked

hide everything
show cartoon, human_dhfr and polymer
color gray70, human_dhfr and polymer

show sticks, human_dhfr and resn NDP
color yellow, human_dhfr and resn NDP

show sticks, crystal_mtx
color cyan, crystal_mtx

show sticks, redocked
color magenta, redocked

set state, 1
zoom crystal_mtx, 8

# Save manually after visual inspection if desired:
# save 1U72_redocking_analysis.pse
