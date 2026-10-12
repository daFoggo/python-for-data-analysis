from nbkit import md, code, ex, details

FILENAME = "session_02_numpy_arrays.ipynb"

CELLS = [
    md(r"""
# Session 02 · Multi-Dimensional Arrays and Broadcasting
*Python for Data Analysis, learning through building data*

[<< Roadmap](./00_roadmap_and_orientation.ipynb) | [<< Session 01](./session_01_environment_ipython.ipynb) | **Session 02** | [Session 03 >>](./session_03_numpy_filtering.ipynb)

**Time:** 75-90 minutes · **Optional reading in McKinney 3E:** Ch. 4, section 4.1 (ndarray, data types, arithmetic, indexing and slicing); Appendix A, section A.3 (Broadcasting)

**By the end you will be able to:**
1. Read an array's `shape`, `dtype` and `nbytes`, and pick a dtype that saves memory.
2. Select data from a matrix with indexing and slicing, and understand `axis` in sums, means and maxima.
3. Use **broadcasting** to normalize a whole 10-building matrix with one expression.

---

## Warm-up: recall Session 01 (~3 min)

**Answer in the blank cell first**, then open the answers. Trying to recall, even when you get it wrong, helps you remember longer than rereading does.

1. Why does a NumPy array use less memory than a Python list holding the same numbers?
2. Write an expression that converts an array `celsius` to °F without a loop.
3. How do you time one line of code in IPython?
"""),
    ex(skeleton="# Write your answers here\n", solution="pass"),
    details("Show the answers", r"""
1. NumPy stores the numbers side by side, each exactly the size of the dtype (8 bytes for `float64`), with no Python object attached to each number.
2. `celsius * 1.8 + 32`
3. `%timeit expression` (one line), or `%%time` on the first line of a cell (the whole cell).
"""),
    md(r"""
## The whole game: energy use intensity of 10 buildings

The data for all 10 buildings is **one matrix** with 8,760 rows (every hour of the year) and 10 columns (one per building). Dividing each building's annual energy by its floor area shows which one burns the most electricity per square meter, a number energy engineers call *EUI* (energy use intensity). Don't worry about every line yet; just run it:
"""),
    code(r"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = next(p for p in (Path("data"), Path("../data")) if p.exists())

telemetry = pd.read_parquet(DATA_DIR / "building_telemetry.parquet")
metadata = pd.read_csv(DATA_DIR / "building_metadata.csv")

# (8760 hours x 10 buildings) matrix, columns in the same order as the metadata table
building_ids = list(metadata["building_id"])
wide = telemetry.pivot(index="timestamp", columns="building_id", values="reading_kw")
kw = np.array(wide[building_ids])
sqm = np.array(metadata["sqm"], dtype=np.float64)   # floor area, 10 values

print("Power matrix:", kw.shape, kw.dtype)
print("Floor area  :", sqm.shape)

eui = kw.sum(axis=0) / sqm          # kWh per m2 over the year
for name, value in sorted(zip(building_ids, eui), key=lambda pair: -pair[1]):
    print(f"{name:18s} {value:6.1f} kWh/m2")
"""),
    md(r"""
One line, `kw.sum(axis=0) / sqm`, handled 87,600 numbers. In the next sections we unpack the pieces: what `axis=0` means, and why a 10-element array (`sqm`) can divide a 10-column matrix (that is **broadcasting**).

---

## 1. Shape, dtype and memory

Every NumPy array has two parts: a **data block** (the numbers, side by side) and a small **description** holding:
- `shape`: the size along each dimension. `(8760, 10)` means 8,760 rows and 10 columns.
- `dtype`: the type of each number, which sets the bytes per element.
- `strides`: how many bytes to jump to reach the next element along each dimension.

For sensor data, choosing the right dtype can save a lot of memory:

| dtype | Bytes each | Value range | Good for |
|---|---|---|---|
| `int16` | 2 | -32,768 to 32,767 | small counts, 12-16 bit ADC codes |
| `int32` | 4 | about +/-2.1 billion | large pulse counters |
| `float32` | 4 | about 7 reliable decimal digits | temperature, humidity, power |
| `float64` | 8 | about 15-16 digits | calculations needing high precision (NumPy's default) |

Convert with `.astype(...)`, and `.nbytes` tells you how many bytes an array uses.

### Predict
A `float64` array of shape `(100_000, 4)` takes how many bytes? How many after converting to `float32`? Write your guess, then run it.
"""),
    code(r"""
rng = np.random.default_rng(seed=1)
readings = rng.uniform(10.0, 100.0, size=(100_000, 4))

print("shape :", readings.shape)
print("dtype :", readings.dtype)
print("nbytes:", readings.nbytes, f"({readings.nbytes / 1024**2:.2f} MiB)")

readings32 = readings.astype(np.float32)
print("After astype(float32):", readings32.nbytes, "bytes")
"""),
    details("Show the answer", r"""
100,000 x 4 x 8 = **3,200,000 bytes** (about 3.05 MiB). As `float32` it is **1,600,000 bytes**, exactly half.
"""),
    md(r"""
### Change it: the smallest type that fits
A pulse counter logs pulses per hour and never exceeds 20,000. The cell below converts to `int32`. **Change it to `np.int16`** and rerun: how much memory do you save compared with `int64`?
"""),
    ex(
        skeleton=r"""
pulses = rng.integers(100, 20_000, size=(100_000, 4), dtype=np.int64)
print("int64:", pulses.nbytes / 1024**2, "MiB")

compact = pulses.astype(np.int32)     # <- change the type here
print(compact.dtype, ":", compact.nbytes / 1024**2, "MiB")
""",
        solution=r"""
pulses = rng.integers(100, 20_000, size=(100_000, 4), dtype=np.int64)
print("int64:", pulses.nbytes / 1024**2, "MiB")

compact = pulses.astype(np.int16)
print(compact.dtype, ":", compact.nbytes / 1024**2, "MiB")
""",
    ),
    md(r"""
### Worked example: creating arrays
The most common ways to create arrays:

```python
np.zeros((3, 4))              # all zeros, 3 rows x 4 columns
np.ones(5)                    # all ones, 5 elements
np.arange(12)                 # 0, 1, ..., 11
np.arange(12).reshape(3, 4)   # the same 12 numbers laid out as 3 rows x 4 columns
```

`reshape` changes the **shape** without changing the numbers, so the new dimensions must multiply to the total element count.
"""),
    code(r"""
demo = np.arange(12).reshape(3, 4)
print(demo)
print("shape:", demo.shape, "| size:", demo.size, "| ndim:", demo.ndim)
"""),
    md(r"""
### Fill in the blanks
A week is 7 days x 24 hours = 168 hours. Lay out the numbers `0, 1, ..., 167` as a matrix with 7 rows (days) and 24 columns (hours).
"""),
    ex(
        skeleton=r"""
week = np.arange(___).reshape(___, 24)
print(week.shape)
print("Hour 0 of the first 3 days:", week[:3, 0])
""",
        solution=r"""
week = np.arange(168).reshape(7, 24)
print(week.shape)
print("Hour 0 of the first 3 days:", week[:3, 0])
""",
    ),
    md(r"""
### Solve it yourself, with an auto-check
Create `portfolio`: an array of zeros with shape `(10, 168, 6)` (10 buildings, 168 hours in a week, 6 sub-meters) and dtype `float64`. Create `portfolio32`, its `float32` version, and `ratio = portfolio.nbytes / portfolio32.nbytes`.
"""),
    ex(
        skeleton="# Write your solution here\n",
        solution=r"""
portfolio = np.zeros((10, 168, 6))
portfolio32 = portfolio.astype(np.float32)
ratio = portfolio.nbytes / portfolio32.nbytes
""",
    ),
    code(r"""
# --- Automatic check ---
assert portfolio.shape == (10, 168, 6), f"Wrong shape: {portfolio.shape}"
assert portfolio.dtype == np.float64, "portfolio must be float64"
assert portfolio32.dtype == np.float32, "portfolio32 must be float32"
assert ratio == 2.0, f"Ratio should be 2.0, got {ratio}"
print(f"[PASS] {portfolio.nbytes:,} bytes -> {portfolio32.nbytes:,} bytes")
"""),
    md(r"""
---

## 2. Selecting data, and what `axis` means

Back to the matrix `kw` with shape `(8760, 10)`. **Axis 0 is time** (the rows) and **axis 1 is the building** (the columns).

| Expression | Meaning | Result shape |
|---|---|---|
| `kw[0]` | all 10 buildings at the first hour | `(10,)` |
| `kw[:, 0]` | the first building across the whole year | `(8760,)` |
| `kw[:24, :3]` | first 24 hours of the first 3 buildings | `(24, 3)` |

When you call a summary function with `axis=k`, axis `k` is **collapsed** (it disappears from the result):
- `kw.mean(axis=0)` collapses time and gives **one average per building** (10 values).
- `kw.mean(axis=1)` collapses buildings and gives **one average per hour** (8,760 values).

### Predict
What are the shapes of `kw.mean(axis=0)` and `kw.mean(axis=1)`?
"""),
    code(r"""
print("axis=0:", kw.mean(axis=0).shape)
print("axis=1:", kw.mean(axis=1).shape)
"""),
    details("Show the answer", r"""
`axis=0` gives `(10,)`; `axis=1` gives `(8760,)`. The axis you collapse disappears; the other one stays.
"""),
    md(r"""
### Change it
The cell below computes each building's maximum power (collapsing time). **Change `axis`** so that, **for every hour**, it gives the power of whichever building is highest at that hour. Notice how the result's shape changes.
"""),
    ex(
        skeleton=r"""
peak = kw.max(axis=0)       # <- change the axis here
print(peak.shape)
print(peak[:5])
""",
        solution=r"""
peak = kw.max(axis=1)
print(peak.shape)
print(peak[:5])
""",
    ),
    md(r"""
### Worked example: finding where the maximum is
`argmax` returns the **position** (index) of the maximum instead of the value itself. Combined with the list of names it tells us *which building*:
"""),
    code(r"""
mean_power = kw.mean(axis=0)
pos = mean_power.argmax()
print("Building with the highest average load:", building_ids[pos], f"({mean_power[pos]:.1f} kW)")

peak_hour = kw.argmax(axis=0)           # for each building: which hour is its peak
print("Peak hour index of each building:", peak_hour)
"""),
    md(r"""
### Fill in the blanks
The first week of the year is the first 168 rows. Compute each building's average power during that week:
"""),
    ex(
        skeleton=r"""
first_week = kw[___:___, :]                 # first 168 rows, all columns
first_week_mean = first_week.mean(axis=___) # average over time
print(first_week_mean.shape)
print(np.round(first_week_mean, 1))
""",
        solution=r"""
first_week = kw[0:168, :]
first_week_mean = first_week.mean(axis=0)
print(first_week_mean.shape)
print(np.round(first_week_mean, 1))
""",
    ),
    md(r"""
### Solve it yourself, with an auto-check
On the matrix `kw`, create:
- `building_peaks`: each building's peak power (shape `(10,)`).
- `top_peak_building`: the **name** (from `building_ids`) of the building with the highest peak.
- `january_mean`: each building's average power in **January** (the first 31 days x 24 hours of the year; shape `(10,)`).
"""),
    ex(
        skeleton="# Write your solution here\n",
        solution=r"""
building_peaks = kw.max(axis=0)
top_peak_building = building_ids[building_peaks.argmax()]
january_mean = kw[:31 * 24].mean(axis=0)
""",
    ),
    code(r"""
# --- Automatic check ---
assert building_peaks.shape == (10,), "building_peaks should have 10 values"
assert top_peak_building == "Office_Frank", f"Wrong building name: {top_peak_building}"
assert january_mean.shape == (10,), "january_mean should have 10 values"
assert np.allclose(january_mean, kw[:744].mean(axis=0)), "January is the first 744 hours"
print(f"[PASS] Highest peak: {top_peak_building} ({building_peaks.max():.1f} kW)")
"""),
    md(r"""
---

## 3. Broadcasting: arithmetic between arrays of different shapes

Say a technician tells you: *"Three sensors [temperature, humidity, CO2] are drifting: temperature by -0.3 °C, humidity by +1.2 %, CO2 by -15 ppm."* You have a matrix of 5 readings x 3 sensors and a drift vector of 3 numbers. How do you add the right drift to each column without a loop?

NumPy just lets you write `matrix + drift`. This mechanism is **broadcasting**. The rule (from the official NumPy docs): NumPy compares the two shapes **from the last dimension going left**. Two dimensions are compatible if they are **equal** or **one of them is 1**. Missing dimensions on the left count as 1. A dimension of size 1 is "stretched" to match, and no extra memory is used because NumPy does not copy the data.

```
matrix:  (5, 3)
vector:     (3,)   <- 3 matches 3, the missing dimension counts as 1  => valid, result (5, 3)
```
"""),
    code(r"""
sensors = np.array([
    [21.2, 45.0, 420.0],
    [21.5, 46.2, 435.0],
    [22.1, 44.8, 450.0],
    [21.9, 45.5, 428.0],
    [22.4, 46.0, 460.0],
])                                        # shape (5, 3): temperature, humidity, CO2
drift = np.array([-0.3, 1.2, -15.0])      # shape (3,)

print(sensors + drift)
"""),
    md(r"""
### Predict
A matrix `m` of shape `(3, 2)` (3 readings, 2 channels: voltage and current) is multiplied by the vector `[10.0, 2.0]` of shape `(2,)`. What shape and values come out?
"""),
    code(r"""
m = np.array([[1.0, 2.0],
              [3.0, 4.0],
              [5.0, 6.0]])
print(m * np.array([10.0, 2.0]))
"""),
    details("Show the answer", r"""
Shape `(3, 2)`. Column 0 is multiplied by 10 and column 1 by 2: `[[10, 4], [30, 8], [50, 12]]`.
"""),
    md(r"""
### Change it
Now the technician says only the **humidity column** is off, by **+5.0**, and the other two are fine. Fix `selective_drift`, run it, and check that only the middle column changes.
"""),
    ex(
        skeleton=r"""
selective_drift = np.array([-0.3, 1.2, -15.0])    # <- change these 3 numbers
print("Before:", sensors[0])
print("After :", (sensors + selective_drift)[0])
""",
        solution=r"""
selective_drift = np.array([0.0, 5.0, 0.0])
print("Before:", sensors[0])
print("After :", (sensors + selective_drift)[0])
""",
    ),
    md(r"""
### When the vector runs along time
If a vector has **5 values, one per row** (one per reading), its shape `(5,)` does not match `(5, 3)`, because comparing from the right gives 3 vs 5. We add a dimension to turn the vector into a column `(5, 1)` with `[:, np.newaxis]`:

```
matrix:  (5, 3)
column:  (5, 1)    <- the 1 is stretched to 3 => valid
```
"""),
    code(r"""
decay = np.array([1.0, 0.9, 0.8, 0.7, 0.6])   # shape (5,), one factor per reading
column = decay[:, np.newaxis]
print("column shape:", column.shape)
print((sensors * column)[[0, -1]])             # first row x 1.0, last row x 0.6
"""),
    md(r"""
### Fill in the blanks
You have 4 HVAC temperature channels (100 readings x 4 channels) and 4 calibration factors. Multiply each column by its own factor, then take each channel's mean.
"""),
    ex(
        skeleton=r"""
hvac = np.random.default_rng(42).uniform(15.0, 25.0, size=(100, 4))
factors = np.array([1.02, 0.98, 1.01, 0.99])

calibrated = hvac ___ factors                      # which operation?
channel_means = calibrated.mean(axis=___)
print(np.round(channel_means, 2))
""",
        solution=r"""
hvac = np.random.default_rng(42).uniform(15.0, 25.0, size=(100, 4))
factors = np.array([1.02, 0.98, 1.01, 0.99])

calibrated = hvac * factors
channel_means = calibrated.mean(axis=0)
print(np.round(channel_means, 2))
""",
    ),
    md(r"""
### Back to the opening question: why does `kw.sum(axis=0) / sqm` work?
`kw.sum(axis=0)` has shape `(10,)` and `sqm` has shape `(10,)`, so they divide pair by pair. But if we want to divide the **whole matrix** `kw` `(8760, 10)` by `sqm` `(10,)` to get power per square meter at *every hour*, broadcasting handles the rest.

One more tool: `keepdims=True` keeps the collapsed axis with size 1, which makes broadcasting back easy. The per-hour total over all buildings has shape `(8760,)` and does not divide into `kw` `(8760, 10)` directly, but `kw.sum(axis=1, keepdims=True)` has shape `(8760, 1)`, which does:
"""),
    code(r"""
hourly_total = kw.sum(axis=1, keepdims=True)
print("shape of the hourly total:", hourly_total.shape)

share_demo = kw / hourly_total          # (8760, 10) / (8760, 1) -> (8760, 10)
print("Share of each of the 10 buildings at the first hour:", np.round(share_demo[0], 3))
print("Shares add up to:", share_demo[0].sum().round(3))
"""),
    md(r"""
### Solve it yourself, with an auto-check
Using `kw` and `sqm`:
- `w_per_m2`: power per square meter at every hour, in **W/m²** (1 kW = 1000 W). Shape `(8760, 10)`.
- `mean_w_per_m2`: the time average of `w_per_m2`, shape `(10,)`.
"""),
    ex(
        skeleton="# Write your solution here\n",
        solution=r"""
w_per_m2 = kw * 1000 / sqm
mean_w_per_m2 = w_per_m2.mean(axis=0)
""",
    ),
    code(r"""
# --- Automatic check ---
assert w_per_m2.shape == (8760, 10), f"Wrong shape: {w_per_m2.shape}"
assert mean_w_per_m2.shape == (10,), "mean_w_per_m2 should have 10 values"
assert np.isclose(w_per_m2[100, 3], kw[100, 3] * 1000 / sqm[3]), "Column 3 was not divided by its own floor area"
assert np.allclose(mean_w_per_m2 * 8760 / 1000, eui, rtol=1e-4), "Mean W/m2 x 8760 h / 1000 should equal EUI (kWh/m2)"
print("[PASS] Mean W/m2 per building:", np.round(mean_w_per_m2, 2))
"""),
    md(r"""
---

## 4. Bug clinic

### Case 1: `ValueError` from mismatched shapes
We try to add 5 per-reading weights to a `(5, 3)` matrix and forget the extra axis:
"""),
    code(r"""
data = np.zeros((5, 3))
weights = np.array([1.0, 1.1, 1.2, 1.3, 1.4])      # shape (5,)

try:
    data + weights
except ValueError as err:
    print("ValueError:", err)
"""),
    md(r"""
**Reading it:** the message lists the shapes of both operands: `(5,3)` and `(5,)`. Compared from the right, 3 differs from 5 and neither is 1, so they cannot broadcast. **The fix:** turn `(5,)` into `(5, 1)`:
"""),
    code(r"""
result = data + weights[:, np.newaxis]
print("It works now, shape:", result.shape)
"""),
    md(r"""
### Case 2: integers that quietly wrap around
Many meters send data as `int16`, max 32,767. Adding two large values can **overflow** and go negative:
"""),
    code(r"""
import warnings

pulses = np.array([30_000, 5_000], dtype=np.int16)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")                    # NumPy warns about overflow on scalars
    print("Adding two int16 elements:", pulses[0] + pulses[1])   # overflow!

print("Adding two int16 arrays element by element:", pulses + pulses)   # 60000 and 10000 -> first one overflows
print(".sum() of an int16 array:", pulses.sum(), "| result dtype:", pulses.sum().dtype)

try:
    pulses + 40_000                                    # Python int too large for int16
except OverflowError as err:
    print("OverflowError:", err)
"""),
    md(r"""
**Lesson:** `+` between `int16` arrays or elements **keeps the type and can overflow silently**. `.sum()` accumulates in a wider integer by default, so it is safe in this case (the result above is `int64`). For a Python number that is too large for the array's dtype, NumPy 2 raises a clear `OverflowError`. When accumulating, convert to a wider type on purpose: `pulses.astype(np.int32)`.

---

## 5. Blank-page challenge (~25 min)

**No AI writing code in this part.** If you are stuck, look back at the examples above.

**Scenario:** The facilities team wants to know (a) which building uses the most electricity per m², (b) how far each building's load drifts from its own normal level, and (c) what share of the whole site's load each building has at every hour. You have `kw` `(8760, 10)`, `sqm` `(10,)` and the list `building_ids`.

Create these variables:
1. `eui_year`: each building's annual energy divided by floor area (kWh/m²), shape `(10,)`. (Write it again yourself, without looking at the opening cell.)
2. `most_intensive`: the **name** of the building with the highest `eui_year`.
3. `kw_centered`: `kw` after **subtracting each building's own mean**, shape `(8760, 10)`. Each column's mean should be about 0.
4. `share`: each building's share of the total site load at every hour, shape `(8760, 10)`. Each row should add up to 1.
5. `peak_site_hour`: the hour index (row) at which the **total site load** is highest.
"""),
    ex(
        skeleton="# Write your solution here\n",
        solution=r"""
eui_year = kw.sum(axis=0) / sqm
most_intensive = building_ids[eui_year.argmax()]
kw_centered = kw - kw.mean(axis=0)
share = kw / kw.sum(axis=1, keepdims=True)
peak_site_hour = kw.sum(axis=1).argmax()
""",
    ),
    code(r"""
# --- Automatic check ---
ref = kw.astype(np.float64)
assert eui_year.shape == (10,), "eui_year should have 10 values"
assert np.allclose(eui_year, ref.sum(axis=0) / sqm, rtol=1e-4), "eui_year is wrong"
assert most_intensive == building_ids[int((ref.sum(axis=0) / sqm).argmax())], "most_intensive is wrong"
assert kw_centered.shape == (8760, 10), "kw_centered must keep shape (8760, 10)"
assert np.abs(kw_centered.mean(axis=0)).max() < 1e-2, "Each column mean of kw_centered should be ~0"
assert share.shape == (8760, 10), "share must keep shape (8760, 10)"
assert np.allclose(share.sum(axis=1), 1.0, atol=1e-4), "Each row of share must add up to 1"
assert peak_site_hour == ref.sum(axis=1).argmax(), "peak_site_hour is wrong"
print(f"[PASS] Most intensive per m2: {most_intensive} | Site peak hour: row {peak_site_hour}")
"""),
    md(r"""
---

## 6. Wrap-up

**Three things to carry forward**
1. An array is a block of numbers plus a description (`shape`, `dtype`, `strides`). Pick the smallest dtype that is enough, but watch for overflow in small integer types.
2. `axis=k` means **axis k is collapsed**. On a (time x building) matrix, `axis=0` gives results per building and `axis=1` gives results per hour.
3. Broadcasting compares shapes **from the right to the left**; each pair of dimensions must be equal or one must be 1. To line something up as a column, use `[:, np.newaxis]` or `keepdims=True`.

### Three flashcards (write the code first, then check)

**Card 1.** Convert the array `arr` from `float64` to `float32`.
"""),
    details("Card 1 answer", r"""
```python
arr.astype(np.float32)
```
"""),
    md(r"""
**Card 2.** Given a matrix `m` of shape `(1000, 4)` (time x channel), compute the mean **of each channel**.
"""),
    details("Card 2 answer", r"""
```python
m.mean(axis=0)
```
"""),
    md(r"""
**Card 3.** A vector `v` of shape `(100,)` must multiply every row of a `(100, 5)` matrix. Reshape `v` so it broadcasts.
"""),
    details("Card 3 answer", r"""
```python
v[:, np.newaxis]      # or v.reshape(100, 1)
```
"""),
    md(r"""
**Review schedule:** day 1, 3, 7, 14 and 30 from today.

👉 Next: **[Session 03 · Boolean masks, views and copies](./session_03_numpy_filtering.ipynb)**: cleaning faulty sensor data and avoiding the "I changed the original data" bug.
"""),
]
