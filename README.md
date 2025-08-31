# Skoomtown Archive — README

A tiny terminal game shell with three mini-games. When all three are completed, a fourth option unlocks and displays secret text from a file. Access to the menu is protected by a password loaded from a file.

This guide covers running with Python, making the script executable on Linux, and building a standalone binary with PyInstaller on **Windows** and **Linux**. It also explains how to change the password and the unlocked data.

---

## Project layout

```
main repo/
├─ scripts/
│  └─ main.py
├─ games/
│  ├─ data_stream_decrypt.py
│  ├─ circuit_override.py
│  └─ firewall_matrix_breach.py
├─ utility/
│  ├─ access.py          # password loader/auth (reads from ./data/password.txt)
│  └─ open_file.py       # unlocked text loader (reads from ./data/vault.txt)
├─ data/
│  ├─ password.txt       # the password (single line)
│  └─ vault.txt          # the unlocked text shown by option 4
└─ environment.yml       # conda environment specification
```
> By default, the password and unlocked data are read from `./data/password.txt` and `./data/vault.txt` relative to the **main repository root** (or next to the frozen executable).

---

## Requirements

- Python 3.9+ recommended  
- A working Conda distribution (Anaconda or Miniconda).
- The `environment.yml` defines all dependencies (e.g., `rich`, `blessed`).

Create and activate the environment.

### Linux / macOS (bash/zsh)

```bash
conda env create -f environment.yml
conda activate skoomtown_archive
```

### Windows (PowerShell)

```powershell
conda env create -f environment.yml
conda activate skoomtown_archive
```


---

## Running with Python

From the repository root (with the Conda environment activated):

```bash
python main.py
```

Windows:

```powershell
py main.py
```

Ensure `data/password.txt` and `data/vault.txt` exist (see “Changing password and vault” below).

---

## Make the script directly executable (Linux)

Ensure this **shebang** is the first line of `main.py`:

```python
#!/usr/bin/env python3
```

Then:

```bash
chmod +x main.py
./main.py
```

> On Windows, the shebang does not make scripts directly executable. Use `py main.py` or build with PyInstaller (see below).

---

## Build a standalone binary with PyInstaller

Install PyInstaller **inside the Conda environment**:

### Linux / macOS

```bash
conda install -c conda-forge pyinstaller
# or: pip install pyinstaller
```

### Windows (PowerShell)

```powershell
conda install -c conda-forge pyinstaller
# or: pip install pyinstaller
```

### Important about data files

Keep `data/password.txt` and `data/vault.txt` **external** so you can change them without rebuilding. After building, ensure a `data/` folder sits **next to the built executable**.

### Linux build

```bash
pyinstaller --name skoomtown   --onefile --console   --add-data "data/password.txt:data"   --add-data "data/vault.txt:data"   main.py
```

This creates `dist/skoomtown`. Ensure `dist/data/` also exists:

```bash
mkdir -p dist/data
cp data/password.txt data/vault.txt dist/data/
```

Run it:

```bash
./dist/skoomtown
```

### Windows build (PowerShell)

```powershell
pyinstaller --name skoomtown `
  --onefile --console `
  --add-data "data\password.txt;data" `
  --add-data "data\vault.txt;data" `
  main.py
```

After build, copy the `data` folder next to the EXE:

```powershell
New-Item -ItemType Directory -Force dist\data | Out-Null
Copy-Item data\password.txt, data\vault.txt dist\data\
```

Run it:

```powershell
dist\skoomtown.exe
```

> Why both `--add-data` **and** copying the folder?  
> Your code looks for `./data/...` next to the executable so secrets stay editable post-build. `--add-data` keeps things working if you ever switch to a non-`--onefile` build or want the files bundled as defaults.

---

## Changing the password and the unlocked data

### Password — `data/password.txt`

- File must contain a **single line** with the password. Example:

  ```
  skoomtown-secret
  ```

- Leading/trailing whitespace is stripped.
- Keep this file **outside** the binary so you can change it any time:
  - Development: `main repo/data/password.txt`
  - Frozen (Linux): `dist/data/password.txt`
  - Frozen (Windows): `dist\skoomtown\data\password.txt`

### Unlocked data — `data/vault.txt`

- Arbitrary multi-line text. Displayed after completing all three mini-games and choosing option 4.
- Example:

  ```
  << SECURE NODE: SKOOMTOWN ARCHIVE >>
  Access Level: OMEGA
  Key Phrase: "THE JELLYFISH DREAMED IN COLOUR"
  ```

- Same placement rules as the password file.

---

## Usage notes

- **Option 4 visibility**: it appears only when all three sub-games are marked complete.
- **Screen clearing**: the menu clears before launching sub-games; the unlocked text view also clears before rendering.
- **Windows terminals**: if key handling feels odd, prefer Windows Terminal or run in PowerShell; `blessed` generally works well, and fallbacks are in place.

---

## Example `environment.yml`

Here is a minimal example you can adapt:

```yaml
name: skoomtown
channels:
  - conda-forge
dependencies:
  - python >=3.9
  - rich >=13.0
  - blessed >=1.20
  - pip
  # if you prefer installing pyinstaller in this env:
  - pyinstaller  # or install later via: conda install -c conda-forge pyinstaller
```

---

## Troubleshooting

- **“Access denied” immediately**  
  Check `data/password.txt` exists and isn’t empty.

- **Option 4 does nothing**  
  Ensure `data/vault.txt` exists and is readable; confirm all three segments show as completed.

- **Frozen build can’t find files**  
  Verify a `data/` folder is next to the executable with `password.txt` and `vault.txt` inside.

- **Unicode box-drawing looks wrong**  
  Switch to a UTF-8 capable font/terminal.
