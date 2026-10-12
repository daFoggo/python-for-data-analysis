from nbkit import md, code, ex, details

FILENAME = "session_03_numpy_filtering.ipynb"

CELLS = [
    md(r"""
# Session 03 · Boolean Masks, Views and Copies
*Python for Data Analysis, learning through building data*

[<< Roadmap](./00_roadmap_and_orientation.ipynb) | [<< Session 02](./session_02_numpy_arrays.ipynb) | **Session 03** | [Session 04 >>](./session_04_pandas_series_dataframe.ipynb)

**Time:** 75-90 minutes · **Optional reading in McKinney 3E:** Ch. 4, section 4.1 (Boolean indexing, slicing), section 4.3 (universal functions), section 4.4 (conditional logic with arrays, methods for Boolean arrays)

**By the end you will be able to:**
1. Filter sensor data with **Boolean masks**, and count and combine conditions correctly.
2. Tell a **view** from a **copy**, and know when "editing a sub-array" will damage the original.
3. Replace bad values with `np.where` and clamp impossible values with `np.clip`.

---

## Warm-up: recall Session 02 (~3 min)

Answer in the blank cell first, then open the answers.

1. A matrix `m` has shape `(8760, 10)` (hours x buildings). Write the expression for the average power of **each building**.
2. Why does `matrix(5, 3) + vector(5,)` raise an error, and how do you fix it?
3. Write code that converts a `float64` array to `float32` and gets its size in bytes.
"""),
    ex(skeleton="# Write your answers here\n", solution="pass"),
    details("Show the answers", r"""
1. `m.mean(axis=0)`
2. Compared from the right, `3` and `5` differ and neither is 1. Fix it with `vector[:, np.newaxis]` so the shape becomes `(5, 1)`.
3. `arr.astype(np.float32).nbytes`
"""),
    md(r"""
## The whole game: cleaning a faulty chilled-water stream

Field sensors tend to fail in two ways: **lost connection** (an error code of `-99`) and **spikes** (a jump to 120 °C, impossible for chilled water). The cell below **generates** a chilled-water temperature stream with both kinds of faults mixed in (simulated data), then cleans it in a few lines. Run it first; the explanation follows.
"""),
    code(r"""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(seed=42)
clean = rng.normal(loc=7.0, scale=1.2, size=1000)        # true chilled-water temperature, °C
faulty = clean.copy()
faulty[rng.choice(1000, size=20, replace=False)] = -99.0   # lost connection
faulty[rng.choice(1000, size=15, replace=False)] = 120.0   # spikes

valid = (faulty >= 4.0) & (faulty <= 18.0)               # mask: plausible operating range
median_good = np.median(faulty[valid])                   # median of the good data
repaired = np.where(valid, faulty, median_good)          # replace bad samples with that median

print(f"Total samples        : {len(faulty)}")
print(f"Bad samples          : {(~valid).sum()}")
print(f"Range before cleaning: [{faulty.min():.1f}, {faulty.max():.1f}] °C")
print(f"Range after cleaning : [{repaired.min():.1f}, {repaired.max():.1f}] °C")
"""),
    md(r"""
The three tools we just used are today's topic: a **Boolean mask** (`valid`), combining conditions (`&`, `~`), and `np.where`. Let's take them one at a time.

---

## 1. Boolean masks: asking an array a question

When you compare an array with a number (`>`, `<`, `==`, ...), NumPy compares **element by element** and returns an array of `True/False` with the same shape, called a **mask**. Put the mask in square brackets, `arr[mask]`, to pick out the elements where it is `True`.

### Predict
For `temps` below, what does `temps > 24.0` give? What does `temps[temps > 24.0]` give?
"""),
    code(r"""
temps = np.array([21.5, 25.1, 23.8, 26.4, 22.0])

mask = temps > 24.0
print("Mask    :", mask)
print("Filtered:", temps[mask])
"""),
    details("Show the answer", r"""
Mask: `[False  True False  True False]`. Filtered: `[25.1 26.4]`.
"""),
    md(r"""
### Change it
A zone counts as *overcooled* if it is below 22.0 °C. Change the condition below to find values `< 22.0` (it is `> 24.0` now). Expected result: `[21.5]`.
"""),
    ex(
        skeleton=r"""
overcooled = temps[temps > 24.0]      # <- change the condition
print(overcooled)
""",
        solution=r"""
overcooled = temps[temps < 22.0]
print(overcooled)
""",
    ),
    md(r"""
### Combining conditions
Use `&` (and), `|` (or), `~` (not). **Put each condition in parentheses**, because `&` and `|` bind tighter than comparisons. Do not use Python's `and`, `or`, `not` on arrays (the bug clinic shows why).

Masks also **count**: `True` is 1, so `mask.sum()` is the number of elements meeting the condition. `mask.any()` asks "is any of them true?" and `mask.all()` asks "are all of them true?".
"""),
    code(r"""
temps_c = np.array([19.5, 21.5, 22.8, 23.9, 25.4, 27.1])

comfortable = (temps_c >= 21.0) & (temps_c <= 24.0)
print("Comfort mask   :", comfortable)
print("Comfortable hrs:", comfortable.sum())
print("Any hour > 27? :", (temps_c > 27.0).any())
"""),
    md(r"""
### Fill in the blanks
A reading is "uncomfortable" if it is **outside** 21.0 to 24.0. Complete the mask `uncomfortable` (use `|`), then count.
"""),
    ex(
        skeleton=r"""
uncomfortable = (temps_c ___ 21.0) | (temps_c ___ 24.0)
print("Mask:", uncomfortable)
print("Uncomfortable samples:", uncomfortable.___())
""",
        solution=r"""
uncomfortable = (temps_c < 21.0) | (temps_c > 24.0)
print("Mask:", uncomfortable)
print("Uncomfortable samples:", uncomfortable.sum())
""",
    ),
    md(r"""
### Worked example: percentiles for thresholds
`np.percentile(arr, 90)` returns the value that 90% of elements are at or below. It is handy for defining "the top 10% of hours":
"""),
    code(r"""
load = np.array([10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0])
threshold = np.percentile(load, 90)
print("90th percentile:", threshold)
print("Peak hours:", load[load >= threshold])
"""),
    md(r"""
### Solve it yourself, with an auto-check
A supply fan logs 50,000 speed samples (RPM). Normal operation is 500-1800 RPM. **Below 100 RPM means the fan is stalled; above 2200 RPM is dangerous overspeed.** Create:
- `hazard_mask`: a mask of samples that are stalled **or** overspeed.
- `hazard_count`: the number of hazardous samples.
- `hazard_pct`: hazardous samples as a percentage of all samples.
"""),
    code(r"""
rng = np.random.default_rng(seed=101)
fan_rpm = rng.normal(loc=1200, scale=350, size=50_000)
fan_rpm[rng.choice(50_000, size=120, replace=False)] = 50.0     # stalled
fan_rpm[rng.choice(50_000, size=80, replace=False)] = 2450.0    # overspeed
"""),
    ex(
        skeleton="# Write your solution here\n",
        solution=r"""
hazard_mask = (fan_rpm < 100) | (fan_rpm > 2200)
hazard_count = hazard_mask.sum()
hazard_pct = hazard_count / len(fan_rpm) * 100
""",
    ),
    code(r"""
# --- Automatic check ---
assert hazard_mask.dtype == bool and hazard_mask.shape == fan_rpm.shape, "The mask must be a bool array with the same shape as fan_rpm"
expected_count = sum(1 for v in fan_rpm if v < 100 or v > 2200)
assert hazard_count == expected_count, f"Wrong count: {hazard_count} vs {expected_count}"
assert hazard_count >= 200, "At least 200 samples were injected as faults (120 stalls + 80 overspeeds)"
assert np.isclose(hazard_pct, expected_count / 50_000 * 100), "hazard_pct must be a percentage"
print(f"[PASS] {hazard_count} hazardous samples ({hazard_pct:.2f}%)")
"""),
    md(r"""
---

## 2. Views and copies: the "my edit changed the original" problem

According to the NumPy docs, an array has a data block and a description. Two cases follow:
- **View**: a new array with its own description that **shares the data block** with the original. Writing through a view writes to the original.
- **Copy**: a new array with its **own data block**. Editing a copy leaves the original alone.

| Operation | Result |
|---|---|
| Slicing `arr[1:3]`, integer index, `np.newaxis` | **view** |
| Boolean mask `arr[mask]`, integer-list index `arr[[1, 2]]` | **copy** |
| `.copy()` | **copy** |
| `reshape` | view when possible, otherwise copy |

To check: `np.shares_memory(a, b)`, or look at `.base` (a view's `.base` points to the original array; a copy's is `None`).

### Predict
We slice the first 3 elements, then set the first element of the slice to `999.0`. Afterwards, is `original[0]` still `10.0` or is it `999.0`?
"""),
    code(r"""
original = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
piece = original[:3]
piece[0] = 999.0

print("piece   :", piece)
print("original:", original)
print("Share memory?", np.shares_memory(piece, original))
"""),
    details("Show the answer", r"""
`original[0]` becomes **999.0**. Slicing creates a **view**, so writing into the slice writes into the original's data block.
"""),
    md(r"""
### Change it: take a safe copy
`safe` below is a view, so editing it changes `temps_orig`. **Add `.copy()`** to the end of the first line and rerun; `temps_orig` should stay unchanged.
"""),
    ex(
        skeleton=r"""
temps_orig = np.array([18.0, 19.5, 21.0, 22.5])

safe = temps_orig[:2]          # <- add .copy() here
safe[0] = -50.0

print("safe      :", safe)
print("temps_orig:", temps_orig)
""",
        solution=r"""
temps_orig = np.array([18.0, 19.5, 21.0, 22.5])

safe = temps_orig[:2].copy()
safe[0] = -50.0

print("safe      :", safe)
print("temps_orig:", temps_orig)
""",
    ),
    md(r"""
### Fill in the blanks: masks give copies
Boolean indexing always returns a **copy**. Complete the cell to confirm it:
"""),
    ex(
        skeleton=r"""
power = np.array([45.2, -99.0, 52.1, -99.0, 48.7])

valid = power > 0
only_valid = power[___]

print("Valid values:", only_valid)
print("Share memory?", np.___(only_valid, power))
""",
        solution=r"""
power = np.array([45.2, -99.0, 52.1, -99.0, 48.7])

valid = power > 0
only_valid = power[valid]

print("Valid values:", only_valid)
print("Share memory?", np.shares_memory(only_valid, power))
""",
    ),
    md(r"""
### A note on arrays that come from pandas
In pandas 3 (Copy-on-Write is the default), an array from `.to_numpy()` on a column can be **read-only** when pandas shares its memory. That is why the `load_kw` helper in earlier sessions wraps its result in `np.array(...)`, which makes a writable copy. See what happens on the pandas version you have:
"""),
    code(r"""
DATA_DIR = next(p for p in (Path("data"), Path("../data")) if p.exists())
telemetry = pd.read_parquet(DATA_DIR / "building_telemetry.parquet")

def load_kw(building_id):
    rows = telemetry["building_id"] == building_id
    return np.array(telemetry.loc[rows, "reading_kw"])

direct = telemetry.loc[telemetry["building_id"] == "Office_Alicia", "reading_kw"].to_numpy()
print("pandas", pd.__version__, "| to_numpy() writable?", direct.flags.writeable)
print("load_kw() writable?", load_kw("Office_Alicia").flags.writeable)
"""),
    md(r"""
### Solve it yourself, with an auto-check
`master` holds baseline calibration data that **must not be modified**. Do this:
1. Create `window`: an **independent copy** of the first 50 rows of `master`.
2. Set every value in `window` to `0.0`.
"""),
    code(r"""
master = np.random.default_rng(42).uniform(20.0, 80.0, size=(100, 3))
first_value = master[0, 0]
"""),
    ex(
        skeleton="# Write your solution here\n",
        solution=r"""
window = master[:50].copy()
window[:] = 0.0
""",
    ),
    code(r"""
# --- Automatic check ---
assert window.shape == (50, 3), "window should have 50 rows and 3 columns"
assert not np.shares_memory(window, master), "window shares memory with master. Did you forget .copy()?"
assert master[0, 0] == first_value and (master != 0.0).all(), "master has been modified!"
assert (window == 0.0).all(), "Every value in window must be 0.0"
print("[PASS] master is intact, window is an independent copy.")
"""),
    md(r"""
---

## 3. Repairing signals with `np.where` and `np.clip`

- **`np.where(condition, a, b)`**: at each position, take `a` if the condition is true, otherwise `b`. Like `a if condition else b`, but for a whole array, and it **returns a new array** so the original is untouched.
- **`np.clip(arr, low, high)`**: force every value outside `[low, high]` to the nearest limit.

### Predict
A battery voltage log contains negative error codes. What does `np.where(raw >= 0.0, raw, 0.0)` give?
"""),
    code(r"""
raw = np.array([3.7, -99.0, 4.1, 3.9, -1.0])
print(np.where(raw >= 0.0, raw, 0.0))
"""),
    details("Show the answer", r"""
`[3.7 0.  4.1 3.9 0. ]`. The two negative values become 0 and the rest are unchanged.
"""),
    md(r"""
### Change it: a fallback value
Instead of 0, we usually replace bad values with a **fallback temperature** (here 22.0 °C). Change the third argument of `np.where` so the `-999.0` codes become `22.0`.
"""),
    ex(
        skeleton=r"""
probe = np.array([21.4, -999.0, 23.1, -999.0, 22.8])

repaired_probe = np.where(probe >= 0.0, probe, 0.0)    # <- change 0.0 to 22.0
print(repaired_probe)
""",
        solution=r"""
probe = np.array([21.4, -999.0, 23.1, -999.0, 22.8])

repaired_probe = np.where(probe >= 0.0, probe, 22.0)
print(repaired_probe)
""",
    ),
    md(r"""
### Fill in the blanks: clamping impossible values
HVAC supply air can only be between 10 and 30 °C. Complete the clamp:
"""),
    ex(
        skeleton=r"""
supply = np.array([8.5, 12.0, 24.5, 32.8, 19.0])

clamped = np.___(supply, ___, ___)
print("Before:", supply)
print("After :", clamped)
""",
        solution=r"""
supply = np.array([8.5, 12.0, 24.5, 32.8, 19.0])

clamped = np.clip(supply, 10.0, 30.0)
print("Before:", supply)
print("After :", clamped)
""",
    ),
    md(r"""
> **Two ways to replace values.** Besides `np.where` (builds a new array), you can assign through a mask: `arr[arr < 0] = 0.0`. That **edits the original array in place** and makes no copy. Choose on purpose: to keep the raw data intact use `np.where`, or copy first and then assign.

### Solve it yourself, with an auto-check
The power stream `raw_kw` from a building has two kinds of faults: lost connection (`-99.0`) and lightning surges (`850.0`). Do this:
1. `fill`: the **median of the non-negative values** in `raw_kw`.
2. `kw_positive`: `raw_kw` with every negative value replaced by `fill` (use `np.where`).
3. `kw_final`: `kw_positive` clamped between `0.0` and `250.0` kW (the main breaker's limit).
"""),
    code(r"""
rng = np.random.default_rng(seed=42)
raw_kw = np.clip(rng.normal(loc=110.0, scale=35.0, size=10_000), 20.0, None)   # real load is never negative
raw_kw[rng.choice(10_000, size=50, replace=False)] = -99.0     # lost connection
raw_kw[rng.choice(10_000, size=20, replace=False)] = 850.0     # lightning surge
raw_kw_orig = raw_kw.copy()
"""),
    ex(
        skeleton="# Write your solution here\n",
        solution=r"""
fill = np.median(raw_kw[raw_kw >= 0.0])
kw_positive = np.where(raw_kw >= 0.0, raw_kw, fill)
kw_final = np.clip(kw_positive, 0.0, 250.0)
""",
    ),
    code(r"""
# --- Automatic check ---
assert np.isclose(fill, np.median(raw_kw_orig[raw_kw_orig >= 0.0])), "fill must be the median of the non-negative values"
assert (kw_positive >= 0).all(), "kw_positive still contains negative values"
assert (kw_final >= 0.0).all() and (kw_final <= 250.0).all(), "kw_final must be within [0, 250]"
assert kw_final.max() == 250.0, "The 850 kW surges must be clamped to exactly 250"
assert np.array_equal(raw_kw, raw_kw_orig), "The original raw_kw must not be modified"
print(f"[PASS] Range after cleaning: [{kw_final.min():.1f}, {kw_final.max():.1f}] kW")
"""),
    md(r"""
---

## 4. Bug clinic

### Case 1: "The truth value of an array ... is ambiguous"
Writing `(arr > 5) and (arr < 10)` with Python's `and` is the classic mistake. `and` needs **one** true/false value, but an array has many elements, so Python cannot tell whether the whole array counts as true or false.
"""),
    code(r"""
arr = np.array([2, 6, 8, 12])

try:
    (arr > 5) and (arr < 10)
except ValueError as err:
    print("ValueError:", err)

print("Correct way:", (arr > 5) & (arr < 10))
"""),
    md(r"""
### Case 2: forgetting the parentheses
We drop the parentheses around the conditions. Because `&` binds tighter than `>` and `<`, Python reads the expression in a different order and still raises the ambiguous-truth error:
"""),
    code(r"""
try:
    arr > 5 & arr < 10
except ValueError as err:
    print("ValueError:", err)

print("With parentheses:", (arr > 5) & (arr < 10))
"""),
    md(r"""
**How to read it:** when the message mentions the "truth value", you are almost certainly using `and`/`or`/`not`, or you left out the parentheses around the conditions.

### Case 3: the history log got overwritten
You normalize a baseline slice of your data, and the original log changes with it:
"""),
    code(r"""
log = np.array([100.0, 200.0, 300.0, 400.0])

baseline = log[:2]          # a view
baseline /= 10.0            # in-place division writes straight into the shared memory
print("log after 'only' changing baseline:", log)
"""),
    md(r"""
**The fix:** make an explicit copy before transforming part of your data: `baseline = log[:2].copy()`. When in doubt, check with `np.shares_memory`.

---

## 5. Blank-page challenge (~25 min)

**No AI writing code in this part.**

**Scenario:** The utility has invited **Office_Alicia** to a *demand response* program: during the **10% of hours with the highest load** each year, the building cuts power by **20%**. You need to estimate the energy saved, **without changing the original data**.

`alicia = load_kw("Office_Alicia")` (8,760 hourly samples) is loaded in the next cell. Create:
1. `peak_threshold`: the 90th percentile of `alicia`.
2. `peak_mask`: a mask of hours with load `>= peak_threshold`.
3. `mean_peak`, `mean_offpeak`: the average power during peak hours and outside them.
4. `curtailed`: a **new** array equal to `alicia`, except peak hours are multiplied by `0.8` (use `np.where`). `alicia` must stay unchanged.
5. `savings_pct`: the percentage of annual energy saved = `(1 - sum of curtailed / sum of alicia) x 100`.
6. `near_peak_hours`: the number of hours with load above **90% of the annual peak** (`alicia.max()`).
"""),
    code(r"""
alicia = load_kw("Office_Alicia")
print(alicia.shape, alicia.dtype, f"| peak {alicia.max():.1f} kW | mean {alicia.mean():.1f} kW")
"""),
    ex(
        skeleton="# Write your solution here\n",
        solution=r"""
peak_threshold = np.percentile(alicia, 90)
peak_mask = alicia >= peak_threshold
mean_peak = alicia[peak_mask].mean()
mean_offpeak = alicia[~peak_mask].mean()
curtailed = np.where(peak_mask, alicia * 0.8, alicia)
savings_pct = (1 - curtailed.sum() / alicia.sum()) * 100
near_peak_hours = (alicia > 0.9 * alicia.max()).sum()
""",
    ),
    code(r"""
# --- Automatic check ---
assert peak_mask.dtype == bool and peak_mask.shape == alicia.shape, "peak_mask must be a bool array of 8760 values"
assert abs(peak_mask.sum() - 0.1 * len(alicia)) <= 3, "The mask should select about 10% of the hours"
assert mean_peak > mean_offpeak, "Average peak-hour load must exceed the off-peak average"
assert np.array_equal(alicia, load_kw("Office_Alicia")), "The original alicia was modified!"
assert not np.shares_memory(curtailed, alicia), "curtailed must be a new array that does not share memory with alicia"
assert np.allclose(curtailed[peak_mask], alicia[peak_mask] * 0.8), "Peak hours must be reduced by 20%"
assert np.allclose(curtailed[~peak_mask], alicia[~peak_mask]), "Off-peak hours must be unchanged"
expected = 0.2 * alicia[peak_mask].astype(np.float64).sum() / alicia.astype(np.float64).sum() * 100
assert np.isclose(savings_pct, expected, rtol=1e-3), f"savings_pct is wrong: {savings_pct:.3f} vs {expected:.3f}"
assert near_peak_hours == int((alicia > 0.9 * alicia.max()).sum()), "near_peak_hours is wrong"
print(f"[PASS] Peak mean {mean_peak:.1f} kW, off-peak {mean_offpeak:.1f} kW | Saves {savings_pct:.2f}% of energy | {near_peak_hours} near-peak hours")
"""),
    md(r"""
---

## 6. Wrap-up

**Three things to carry forward**
1. Comparisons on arrays produce **masks**; combine them with `&`, `|`, `~` **and parentheses**; `mask.sum()` counts.
2. **Slicing gives a view** (shared memory), **masks and index lists give copies**. To edit part of your data safely, `.copy()` first.
3. `np.where` replaces values by condition (making a new array); `np.clip` clamps values to an allowed range.

### Three flashcards (write the code first, then check)

**Card 1.** Select the values of `arr` between 10 and 50 (inclusive).
"""),
    details("Card 1 answer", r"""
```python
arr[(arr >= 10) & (arr <= 50)]
```
"""),
    md(r"""
**Card 2.** Check whether `a` and `b` share memory.
"""),
    details("Card 2 answer", r"""
```python
np.shares_memory(a, b)
```
"""),
    md(r"""
**Card 3.** Replace every negative number in `signals` with `0.0`, keep the non-negative ones, and **do not modify the original array**.
"""),
    details("Card 3 answer", r"""
```python
np.where(signals >= 0, signals, 0.0)
```
"""),
    md(r"""
**Review schedule:** day 1, 3, 7, 14 and 30 from today.

**Weekend mixed practice (30 min):** take problems from Sessions 01-03, hide their titles, and decide yourself which tool each one needs.

👉 Next (Session 04): **pandas Series and DataFrame**, tables with labels. That notebook will be added when you reach it.
"""),
]
