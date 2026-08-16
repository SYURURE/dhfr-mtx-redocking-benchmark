# Third-party notices and data provenance

このリポジトリは第三者ソフトウェアや構造データそのものを再配布することを目的としていません。実行時に各公式配布元から取得し、各配布元の条件と引用方針に従ってください。

## Structural data

- **RCSB Protein Data Bank**
  - PDB ID: `4DFR`
  - PDB ID: `1U72`
  - Ligand: methotrexate (`MTX`)
  - Structure pages: https://www.rcsb.org/structure/4DFR and https://www.rcsb.org/structure/1U72
  - Citation and usage policy: https://www.rcsb.org/pages/policies
  - Structure DOI: https://doi.org/10.2210/pdb4DFR/pdb and https://doi.org/10.2210/pdb1U72/pdb

Raw RCSB PDB coordinate files are intentionally not committed. The scripts download the required inputs from RCSB services. The SDF files under `results/poses/` are docking outputs produced during the exercise and are retained as evidence of the reported runs.

## Software

- **SMINA**: https://github.com/mwojcikowski/smina
  - SMINA is derived from AutoDock Vina and ships with upstream licensing and citation requirements.
  - Paper: https://doi.org/10.1021/ci300604z
- **GNINA**: https://github.com/gnina/gnina
  - GNINA is a deep-learning-enabled docking and rescoring framework derived from SMINA/Vina.
  - GNINA 1.3 paper: https://doi.org/10.1186/s13321-025-00973-x
- **RDKit**: https://www.rdkit.org/
  - `CalcRMS` documentation: https://www.rdkit.org/docs/source/rdkit.Chem.rdMolAlign.html
- **Open Babel**: https://openbabel.org/
  - Command-line documentation: https://openbabel.org/docs/Command-line_tools/babel.html
- **PyMOL Open Source**: https://github.com/schrodinger/pymol-open-source
- **Conda-forge / Miniforge**: https://conda-forge.org/ and https://github.com/conda-forge/miniforge

No SMINA, GNINA, RDKit, Open Babel, PyMOL, or Conda binary is bundled in this repository.
