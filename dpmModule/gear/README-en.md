# maplegear_python
for maplestory_dpm_calc

## Example:
### Retrieve equipment ID from resource. 
```
Gear.searchIDsByName(name="앱솔랩스 아처후드")  # exact=True
```
Returns a list of all device IDs that match exactly. 
```
Gear.searchIDsByName(name="응축", exact=False)
```
Returns a list of all device IDs including search terms. 
### Load equipment from resource
```
Gear.createGearFromID(gearID=1004424)
```
If there is a device ID in the resource, the corresponding device is returned, if not, the basic device is returned. 
### Enhancing Equipment (GearBuilder). 장비 강화하기 (GearBuilder).
You can apply values directly to Gear, but with GearBuilder, you can easily enhance it in an in-game manner. 
```
gb = GearBuilder(gear)
```
or
```
gb.setGear(gear)
```
Initialize with
```
gb.applyAdditionalStat(propType: GearPropType, grade: int, isDoubleAdd: bool = False) -> bool
```
Apply additional options to `gear.additionalStat`.
When `GearPropType.allstat` is delivered, all stat% is applied, in fact, it is replaced by STRr, DEXr, INTr, LUKr.
propType: incSTR, incDEX, incINT, incLUK, incMHP, incMMP, incPAD, incMAD, incPDD, incSpeed, incJump, imdR, damR, bdR, incAllStat (all stat%), reduceReq only
grade: 1 to 7, 7 is the highest and 1 is the lowest. In the case of boss drop items, grades 3 to 6 for strong refunds, grades 4 to 7 for zero refunds, and grades 1 to 4 for strong refunds, and 2 to 5 grades for zero refunds. 1 Papnyr weapon = 7 grade
isDoubleAdd: Double Chuop
Returns True when application is successful, False when there is no change

```
gb.scrollAvailable() -> int
```
Return the number of upgrades available. 
```
scroll = Scroll("방어구 공격력 주문서", defaultdict(int, {GearPropType.incPAD: 2}))
gb.applyScroll(scroll: Scroll, count: int = 1) -> bool
```
Apply order form to `gear.scrollStat`
scroll: Create and deliver order form with `Scroll(name: str = None, stat: DefaultDict[GearPropType, int] = defaultdict(int)`
count: The number of times the order is applied, and if it is greater than the number of upgrades available, it is applied only until the number of available upgrades is exhausted.
Return True if more than one application is successful, False if no change
```
gb.applySpellTraceScroll(probability: int, propType: GearPropType, count: int = 1) -> bool
```
Spell trace enhancement applied to `gear.scrollStat`
probability: The probability of the trace of the spell. 100, 70, 30, 15 only
propType: The type of trace of the order. incSTR, incDEX, incINT, incLUK, incMHP only
count: The number of times the order is applied, and if it is greater than the number of upgrades available, it is applied only until the number of available upgrades is exhausted.
Return True if more than one application is successful, False if no change
```
gb.applyHammer() -> bool
```
Apply Golden Hammer enhancement
Returns True when application is successful, False when there is no change 
```
gb.applyStar(amazingScroll: bool = False, bonus: bool = False) -> bool
```
Star Force, Noljang reinforcement applied to `gear.starStat`
amazingScroll: if true, no surprise, if false, star force
bonus: Whether or not to apply the game bonus stat
Returns True when application is successful, False when there is no change
```
gb.applyStars(count: int, amazingScroll: bool = False, bonus: bool = False) -> int
```
Star Force, Noljang reinforcement applied to `gear.starStat`
count: Number of Star Force enhancements. (Not a target number!)
amazingScroll: if true, no surprise, if false, star force
bonus: Whether or not to apply the game bonus stat
Return the number of successful application
### Checking the applied set effect
```
SetItem.evalSetItemEffect(equippedGears: List[Gear]) -> DefaultDict[GearPropType, int]
```
Passing the list of equipment currently worn will return the set effect option in effect. Wearable/duplicated is not tested unless the equipment ID is the same.
equippedGears: List of equipment you are wearing
Same as in-game logic, if there are multiple lucky items, the equipment with the lowest equipment ID is applied first among the lucky items included in the set effect.
The ERA Ignore option (GearPropType.imdR) has a float value
## Etc 
### Among the GearPropTypes attached to Gear, those that affect dpm: 
STR  
STR_rate  
DEX  
DEX_rate  
INT  
INT_rate  
LUK  
LUK_rate  
MHP  
MHP_rate  
MMP  
MMP_rate  
att  
att_rate  
matt  
matt_rate  
pdamage  
boss_pdamage  
armor_ignore  
crit  
crit_damage  
