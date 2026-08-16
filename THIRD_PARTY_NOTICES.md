# Third-party notices and data provenance

このリポジトリは再現性固定用のRCSB PDB構造data snapshotを収録しています。第三者ソフトウェアの実行バイナリは収録していません。各配布元の条件と引用方針に従ってください。

## Structural data

- **RCSB Protein Data Bank**
  - PDB ID: `4DFR`
  - PDB ID: `1U72`
  - Ligand: methotrexate (`MTX`)
  - Structure pages: https://www.rcsb.org/structure/4DFR and https://www.rcsb.org/structure/1U72
  - Citation and usage policy: https://www.rcsb.org/pages/policies
  - Data usage policy: https://www.rcsb.org/pages/usage-policy
  - License for PDB archive files and RCSB programmatic API data: CC0 1.0 Universal
  - Structure DOI: https://doi.org/10.2210/pdb4DFR/pdb and https://doi.org/10.2210/pdb1U72/pdb

`data/reference/`と`data/raw/gnina_poc/input/`のPDB/SDFは、公表値を入力から再計算できるように固定したRCSB由来dataおよびその変換物です。RCSB PDBはPDB archive filesとprogrammatic API dataをCC0 1.0で提供し、可能な場合は構造原著者とRCSB PDBへの帰属を推奨しています。構造ページとDOIを上記に記載しています。`results/poses/`と`data/raw/`のその他SDFは、本実習で生成した計算出力です。

## Software

- **SMINA**: https://github.com/mwojcikowski/smina
  - SMINA is derived from AutoDock Vina and ships with upstream licensing and citation requirements.
  - Paper: https://doi.org/10.1021/ci300604z
- **GNINA**: https://github.com/gnina/gnina
  - GNINA is a deep-learning-enabled docking and rescoring framework derived from SMINA/Vina.
  - v1.3.3 release: https://github.com/gnina/gnina/releases/tag/v1.3.3
  - GNINA 1.3 paper: https://doi.org/10.1186/s13321-025-00973-x
- **RDKit**: https://www.rdkit.org/
  - `CalcRMS` documentation: https://www.rdkit.org/docs/source/rdkit.Chem.rdMolAlign.html
- **Open Babel**: https://openbabel.org/
  - Command-line documentation: https://openbabel.org/docs/Command-line_tools/babel.html
- **PyMOL Open Source**: https://github.com/schrodinger/pymol-open-source
- **Conda-forge / Miniforge**: https://conda-forge.org/ and https://github.com/conda-forge/miniforge

No SMINA, GNINA, RDKit, Open Babel, PyMOL, or Conda binary is bundled in this repository.
