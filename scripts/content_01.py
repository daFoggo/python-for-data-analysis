from nbkit import md, code, ex, details

FILENAME = "session_01_environment_ipython.ipynb"

CELLS = [
    md(r"""
# Session 01 · Your Environment, and Why NumPy Is Fast
*Python for Data Analysis, learning through building data*

[<< Roadmap](./00_roadmap_and_orientation.ipynb) | **Session 01** | [Session 02 >>](./session_02_numpy_arrays.ipynb)

**Time:** 75-90 minutes · **Optional reading in McKinney 3E:** Ch. 1 (Preliminaries), Ch. 2 (IPython and Jupyter), Appendix B (the IPython system)

**By the end you will be able to:**
1. Check your Python environment and find the data files.
2. Explain why a NumPy array uses less memory and runs faster than a Python list.
3. Write a vectorized expression instead of a `for` loop.
4. Use IPython commands to look things up and time code.

---

## Warm-up: check your environment

Before learning anything, make sure your machine runs the right versions and can find the data. Run the cell below (`Shift + Enter`).
"""),
    code(r"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

print(f"Python {sys.version.split()[0]} | NumPy {np.__version__} | pandas {pd.__version__}")

# Jupyter runs with the notebook's own folder (notebooks/) as the working directory,
# while the data lives in data/ one level up. Try both so this works however you open it.
DATA_DIR = next(p for p in (Path("data"), Path("../data")) if p.exists())
print("Data folder:", DATA_DIR.resolve())
print("Files:", sorted(p.name for p in DATA_DIR.iterdir()))
"""),
    md(r"""
> If this cell raises `StopIteration` or lists no files, the notebook cannot find `data/`. Open the project from its root folder `python-for-data-science`. We will meet this kind of path error again in the bug clinic.

## The whole game first: a complete pipeline in 10 lines

A good way to learn is to run something complete first, then take it apart (the "top-down" approach fast.ai uses). The cell below reads a full year of electricity data for 10 buildings and finds which building has the highest peak load. **You do not need to understand every line yet.** `groupby` and `agg` come in later sessions. Just run it and look at the result.
"""),
    code(r"""
telemetry = pd.read_parquet(DATA_DIR / "building_telemetry.parquet")
metadata = pd.read_csv(DATA_DIR / "building_metadata.csv")

print(f"{len(telemetry):,} readings, {telemetry['building_id'].nunique()} buildings")

summary = (
    telemetry.groupby("building_id")["reading_kw"]
    .agg(mean_kw="mean", peak_kw="max")
    .round(1)
    .sort_values("peak_kw", ascending=False)
)
summary
"""),
    md(r"""
You just read 87,600 measurements and ranked buildings by peak demand in a few lines. The rest of the course is about understanding each piece well enough to do this yourself, and much more.

To keep the first sessions focused on NumPy, we use a helper that pulls one building's power readings out as a **NumPy array**. (It uses pandas, which sessions 04-05 explain.)
"""),
    code(r"""
def load_kw(building_id):
    # Return one building's hourly power readings (kW) as a NumPy array.
    # np.array(...) makes a writable copy; Session 03 explains why that matters.
    rows = telemetry["building_id"] == building_id
    return np.array(telemetry.loc[rows, "reading_kw"])

alicia = load_kw("Office_Alicia")
print(type(alicia), alicia.shape, alicia.dtype)
print("First 5 hours (kW):", alicia[:5])
"""),
    md(r"""
---

## 1. Why not just use a Python list?

A Python list stores **pointers** to number objects scattered around memory, and each float is a full Python object. A NumPy array stores the numbers **packed side by side in one block**, each taking exactly 8 bytes (for `float64`). Packed data is quick for the CPU to read, and NumPy runs its loops in compiled C instead of making the Python interpreter step through each element.

### Predict first
The cell below builds 200,000 floats both ways. **Before you run it**, write down a guess for each:
- How many MB does the NumPy array take? (hint: 200,000 x 8 bytes)
- Roughly how many times bigger will the Python list be?
"""),
    code(r"""
n = 200_000
py_list = [float(x) for x in range(n)]
np_arr = np.arange(n, dtype=np.float64)

# list: the list itself (the pointers) plus every float object
list_bytes = sys.getsizeof(py_list) + sum(sys.getsizeof(x) for x in py_list)

print(f"NumPy array : {np_arr.nbytes / 1024**2:.2f} MB")
print(f"Python list : {list_bytes / 1024**2:.2f} MB")
print(f"Ratio       : {list_bytes / np_arr.nbytes:.1f}x")
"""),
    details("Show the explanation", r"""
NumPy: 200,000 x 8 bytes = 1.6 million bytes, about **1.53 MB**. List: each element is an 8-byte pointer plus a `float` object of about 24 bytes, so the total is around **5-6 MB**, roughly 4 times larger. The exact numbers depend on your Python version and OS, but the pattern does not change.
"""),
    md(r"""
### Vectorization: write the math once, for the whole array
To convert temperatures from °C to °F, use `F = C x 1.8 + 32`. With a list you need a loop. With a NumPy array you write the formula once and NumPy applies it to **every element**. This style is called **vectorization**.
"""),
    code(r"""
import timeit

t_list = timeit.timeit("[c * 1.8 + 32 for c in py_list]", globals=globals(), number=20)
t_numpy = timeit.timeit("np_arr * 1.8 + 32", globals=globals(), number=20)

print(f"List loop       : {t_list:.4f} s")
print(f"NumPy vectorized: {t_numpy:.4f} s")
print(f"NumPy is about {t_list / t_numpy:.0f}x faster on your machine")
"""),
    md(r"""
The exact speedup depends on your machine. Further down, IPython gives us a tidier way to time things.

### A small conversion to predict
A TMP36 analog temperature sensor outputs 0.5 V at 0 °C, and every 10 mV is 1 °C. So `temp_c = (volts - 0.5) * 100`.

**Predict:** for `volts = [0.5, 0.75, 1.0]`, what is the result?
"""),
    code(r"""
volts = np.array([0.5, 0.75, 1.0])
celsius = (volts - 0.5) * 100
print(celsius)
"""),
    details("Show the answer", r"""
`[ 0. 25. 50.]`. The subtraction and multiplication are applied element by element, with no loop.
"""),
    md(r"""
### Change it: to Fahrenheit
The cell below already has the Celsius formula. **Fill in one expression** that computes `fahrenheit` from `celsius` (`F = C x 1.8 + 32`) and run it. The benchmark cell above shows the form.
"""),
    ex(
        skeleton=r"""
volts = np.array([0.5, 0.75, 1.0])
celsius = (volts - 0.5) * 100

fahrenheit = ___      # fill in the expression
print(fahrenheit)
""",
        solution=r"""
volts = np.array([0.5, 0.75, 1.0])
celsius = (volts - 0.5) * 100

fahrenheit = celsius * 1.8 + 32
print(fahrenheit)
""",
    ),
    md(r"""
### Worked example: quick statistics on an array
NumPy arrays have summary methods: `.min()`, `.max()`, `.mean()`, `.sum()`. Here they are on Office_Alicia's readings:
"""),
    code(r"""
print(f"Peak load   : {alicia.max():.1f} kW")
print(f"Lowest load : {alicia.min():.1f} kW")
print(f"Average load: {alicia.mean():.1f} kW")
"""),
    md(r"""
### Fill in the blanks
These readings are hourly power in kW. Since each sample represents one hour, **the sum of the kW values is the total energy in kWh**. Complete the cell and run it.
"""),
    ex(
        skeleton=r"""
alicia = load_kw("Office_Alicia")

total_kwh = alicia.___()          # total energy over the year (kWh)
total_mwh = total_kwh / ___       # convert to MWh

print(f"Office_Alicia used {total_mwh:,.0f} MWh this year")
""",
        solution=r"""
alicia = load_kw("Office_Alicia")

total_kwh = alicia.sum()
total_mwh = total_kwh / 1000

print(f"Office_Alicia used {total_mwh:,.0f} MWh this year")
""",
    ),
    md(r"""
### Solve it yourself, with an auto-check
For **Education_Claire**, compute:
- `claire`: the building's power array (use `load_kw`)
- `load_factor`: average power divided by peak power. It tells you whether a building draws power steadily or in a few peak hours.
- `memory_kb`: the array's size in KB (use `.nbytes`; 1 KB = 1024 bytes)

Run the check cell when you are done.
"""),
    ex(
        skeleton=r"""
# Write your solution here
""",
        solution=r"""
claire = load_kw("Education_Claire")
load_factor = claire.mean() / claire.max()
memory_kb = claire.nbytes / 1024
""",
    ),
    code(r"""
# --- Automatic check ---
assert claire.shape == (8760,), "claire should have 8760 samples (365 days x 24 hours)"
assert 0 < load_factor < 1, "Load factor must be between 0 and 1"
assert abs(load_factor - claire.mean() / claire.max()) < 1e-9, "load_factor should be mean / max"
assert abs(memory_kb - 8760 * 4 / 1024) < 1e-6, "A float32 array of 8760 elements takes 8760 * 4 bytes"
print(f"[PASS] Education_Claire load factor: {load_factor:.2f} | Memory: {memory_kb:.1f} KB")
"""),
    md(r"""
> Did you notice the dtype is `float32` (4 bytes), not `float64`? The Parquet file stores readings as `float32`. Session 02 covers dtypes properly.

---

## 2. Working in IPython and Jupyter

Notebooks run on **IPython**, an interactive Python shell with extra conveniences. Four things worth knowing from day one:

| Feature | How | What for |
|---|---|---|
| Tab completion | type `np.` then press `Tab` | see what names are available |
| `?` | `np.clip?` | read a function's documentation inside the notebook |
| `%timeit` | `%timeit expression` | time one line (it repeats the run for a stable number) |
| `%%time` | first line of a cell | time the whole cell |

> The cells below use IPython syntax (`?`, `%`), so they only run in Jupyter or VS Code notebooks, not in plain Python.

### Predict
For the next cell, would `%timeit` show the `alicia * 1.8 + 32` operation on 8,760 elements taking microseconds or milliseconds?
"""),
    code(r"""
%timeit alicia * 1.8 + 32
""", skip=True),
    details("Show the hint", r"""
Around **tens of microseconds** on a modern machine, since 8,760 elements is tiny for NumPy. `%timeit` repeats the run many times and reports the mean and spread.
"""),
    md(r"""
### Look things up with `?`
Run the cell below and read the top of the documentation. Look at the **signature** on the first line and the `Parameters` section.
"""),
    code(r"""
np.clip?
""", skip=True),
    md(r"""
### Try it yourself
Uncomment one line below (remove the `#`) and run it:
1. `pd.*read*?` lists every pandas name with `read` in it.
2. `pd.read_parquet?` shows which arguments the Parquet reader takes.

Write down: **which function reads a CSV file?** **Which argument of `read_parquet` lets you load only some columns?**
"""),
    code(r"""
# pd.*read*?
# pd.read_parquet?
""", skip=True),
    md(r"""
### Where `%%time` must go
A `%%` magic (which applies to the whole cell) **must be on the very first line of the cell**, with no comment or blank line above it. This one is correct:
"""),
    code(r"""
%%time
total = 0
for value in alicia:
    total += value
print(f"Total from a loop: {total:,.0f} kWh")
""", skip=True),
    md(r"""
If you put a comment on line 1 and `%%time` on line 2, IPython fails with an error like `UsageError: Line magic function '%%time' not found`. Remember this one; it is easy to hit.

---

## 3. Bug clinic

You will see errors every day. Reading a **traceback** well matters more than avoiding errors: read the **last line first** (error type and message), then work upward to find which of your lines caused it.

### Case 1: `FileNotFoundError` from a wrong path
We read a file that does not exist on purpose, and print the error instead of letting the notebook stop.
"""),
    code(r"""
try:
    pd.read_parquet("data/does_not_exist.parquet")
except FileNotFoundError as err:
    print("Error type:", type(err).__name__)
    print("Message   :", err)
    print("Current working directory:", Path.cwd())
"""),
    md(r"""
**What to do:** compare the path in the message with `Path.cwd()`. A relative path like `"data/..."` is resolved from the working directory, which **depends on how you launched Jupyter**. That is why this notebook starts with `DATA_DIR`.

### Case 2: why you should not write `from numpy import *`
Some older tutorials use `from numpy import *` to save typing. It dumps every NumPy name into your namespace and **overwrites Python built-ins**, `sum` for example. We try it in an isolated namespace so it does not break this notebook:
"""),
    code(r"""
# Python's built-in sum accepts a start argument
print("Built-in sum:", sum([10, 20, 30], start=5))

# Simulate 'from numpy import *' in a separate namespace
sandbox = {}
exec("from numpy import *", sandbox)
try:
    eval("sum([10, 20, 30], start=5)", sandbox)
except TypeError as err:
    print("After import *, the same call fails:", err)
"""),
    md(r"""
**The community convention:** always `import numpy as np` and `import pandas as pd`, then call `np.sum`, `pd.read_csv`. You can see where every function comes from.

---

## 4. Blank-page challenge (~25 min)

**No AI writing code in this part.** (Anthropic's study found people who delegated code writing to AI scored lower afterwards. If you are stuck, ask AI about a *concept*, or ask it to explain code **you wrote**.)

**Scenario:** You are an energy engineer asked: *of Office_Bob and Lodging_Ivy, which building has the steadier electrical load, and how many MWh does each use per year?*

Create these variables (one line or several, your choice):
1. `bob`, `ivy`: the power arrays of the two buildings (use `load_kw`).
2. `mwh_bob`, `mwh_ivy`: annual energy of each building in **MWh**.
3. `load_factor_bob`, `load_factor_ivy`: each building's load factor (mean / peak).
4. `steadier`: the string `"Office_Bob"` or `"Lodging_Ivy"`, whichever has the **higher** load factor (use a normal `if`).
5. `bob_mw`: Office_Bob's power array converted to **MW** (divide by 1000), as one vectorized operation.

You only need what you saw in this session.
"""),
    ex(
        skeleton=r"""
# Write your solution here
""",
        solution=r"""
bob = load_kw("Office_Bob")
ivy = load_kw("Lodging_Ivy")

mwh_bob = bob.sum() / 1000
mwh_ivy = ivy.sum() / 1000

load_factor_bob = bob.mean() / bob.max()
load_factor_ivy = ivy.mean() / ivy.max()

if load_factor_bob > load_factor_ivy:
    steadier = "Office_Bob"
else:
    steadier = "Lodging_Ivy"

bob_mw = bob / 1000
""",
    ),
    code(r"""
# --- Automatic check ---
assert bob.shape == ivy.shape == (8760,), "bob and ivy must be arrays of 8760 samples"
assert abs(mwh_bob - telemetry.loc[telemetry["building_id"] == "Office_Bob", "reading_kw"].sum() / 1000) < 1e-3, "mwh_bob is wrong"
assert abs(mwh_ivy - ivy.sum() / 1000) < 1e-3, "mwh_ivy is wrong"
assert mwh_bob > mwh_ivy, "Office_Bob is larger, so it should use more energy"
assert 0 < load_factor_bob < 1 and 0 < load_factor_ivy < 1, "load factors must be in (0, 1)"
expected = "Office_Bob" if bob.mean() / bob.max() > ivy.mean() / ivy.max() else "Lodging_Ivy"
assert steadier == expected, "steadier does not match the load factors you computed"
assert np.isclose(bob_mw.max(), bob.max() / 1000), "bob_mw has not been divided by 1000"
print(f"[PASS] Office_Bob {mwh_bob:,.0f} MWh (load factor {load_factor_bob:.2f}) | Lodging_Ivy {mwh_ivy:,.0f} MWh ({load_factor_ivy:.2f}) | Steadier: {steadier}")
"""),
    md(r"""
---

## 5. Wrap-up

**Three things to carry forward**
1. A NumPy array stores numbers of one fixed type side by side, so it is smaller and faster than a list.
2. **Vectorization**: write the operation for the whole array and skip the `for` loop.
3. In IPython, `?` looks up docs and `%timeit` measures time; `%%time` must be on the first line of a cell.

### Three flashcards (write the code first, then check)

**Card 1.** Given an array `kw` of hourly power over a year, compute total energy in MWh.
"""),
    details("Card 1 answer", r"""
```python
kw.sum() / 1000
```
"""),
    md(r"""
**Card 2.** Given an array `celsius`, create the °F array without a loop.
"""),
    details("Card 2 answer", r"""
```python
celsius * 1.8 + 32
```
"""),
    md(r"""
**Card 3.** You want to read the documentation of `pd.read_parquet` inside the notebook. What do you type?
"""),
    details("Card 3 answer", r"""
```python
pd.read_parquet?
```
"""),
    md(r"""
**Review schedule for these cards:** day 1, 3, 7, 14 and 30 from today. Each time, write the code first, then compare.

👉 Next: **[Session 02 · Multi-dimensional arrays and broadcasting](./session_02_numpy_arrays.ipynb)**, working with all 10 buildings at once.
"""),
]
