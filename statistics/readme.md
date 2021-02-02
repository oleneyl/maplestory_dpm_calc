# Statistics module

`python3 -m statistics.saver --id archmage_fp`

## Example

Run following commands in root of `maplestory_dpm_calc` folder
```
python3 -m statistics.saver --id archmage_fp
python3 -m statistics.gini --id archmage_fp --interval 10000
```

`data/dpm_archmage_tc_8000_0.pkl`, `data/gini/dpm_archmage_tc_8000_0.png` will be created

## Basic arguments

* id
  * preset id to calculate
* ulevel
  * union level (4500, 6000, 7000, 8000, 8500)
  * default = 8000
* cdr
  * cooltime reduce hat (0~4)
  * default = 0
* task
  * dpm (default)
  * burst10
  * task type to calculate
* time
  * time to run simulation
  * ignored when loading data without --calc option
* calc
  * if True, use data from new simulation
  * if False, use saved data