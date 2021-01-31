# maplegear_python
for maplestory_dpm_calc

## Example:
### Retrieve equipment ID from resource. 리소스에서 장비 ID 검색.
```
Gear.searchIDsByName(name="앱솔랩스 아처후드")  # exact=True
```
Returns a list of all device IDs that match exactly. 정확히 일치하는 모든 장비 ID list 반환.
```
Gear.searchIDsByName(name="응축", exact=False)
```
Returns a list of all device IDs including search terms. 검색어를 포함하는 모든 장비 ID list 반환.
### Load equipment from resource | 리소스에서 장비 불러오기
```
Gear.createGearFromID(gearID=1004424)
```
If there is a device ID in the resource, the corresponding device is returned, if not, the basic device is returned. 리소스에 장비 ID가 존재할 경우 해당 장비 반환, 없을 경우 기본 장비 반환.
### Enhancing Equipment (GearBuilder). 장비 강화하기 (GearBuilder).
You can apply values directly to Gear, but with GearBuilder, you can easily enhance it in an in-game manner. Gear에 직접 수치를 적용할 수도 있지만 GearBuilder를 사용하면 인게임 방식대로 간단하게 강화가 가능합니다.
```
gb = GearBuilder(gear)
```
or | 또는
```
gb.setGear(gear)
```
Initialize with | 로 초기화
```
gb.applyAdditionalStat(propType: GearPropType, grade: int, isDoubleAdd: bool = False) -> bool
```
Apply additional options to `gear.additionalStat`.
When `GearPropType.allstat` is delivered, all stat% is applied, in fact, it is replaced by STRr, DEXr, INTr, LUKr.
propType: incSTR, incDEX, incINT, incLUK, incMHP, incMMP, incPAD, incMAD, incPDD, incSpeed, incJump, imdR, damR, bdR, incAllStat (all stat%), reduceReq only
grade: 1 to 7, 7 is the highest and 1 is the lowest. In the case of boss drop items, grades 3 to 6 for strong refunds, grades 4 to 7 for zero refunds, and grades 1 to 4 for strong refunds, and 2 to 5 grades for zero refunds. 1 Papnyr weapon = 7 grade
isDoubleAdd: Double Chuop
Returns True when application is successful, False when there is no change

`gear.additionalStat`에 추가옵션 적용.
`GearPropType.allstat` 전달 시 올스탯% 추옵 적용, 실제로는 STRr, DEXr, INTr, LUKr로 대체됨
propType: incSTR, incDEX, incINT, incLUK, incMHP, incMMP, incPAD, incMAD, incPDD, incSpeed, incJump, imdR, damR, bdR, incAllStat(올스탯%), reduceReq만 가능  
grade: 1 ~ 7, 7이 가장 높고 1이 가장 낮은 옵션. 보스 드랍템의 경우 강환불로 3 ~ 6등급, 영환불로 4 ~ 7등급이 붙고 일반 드랍템의 경우 강환불로 1 ~ 4등급, 영환불로 2 ~ 5등급이 붙음. 파프니르 무기 1추=7등급  
isDoubleAdd: 이중추옵  
적용 성공시 True 반환, 변화 없을 시 False 반환  
```
gb.scrollAvailable() -> int
```
Return the number of upgrades available. 업그레이드 가능 횟수 반환.
```
scroll = Scroll("방어구 공격력 주문서", defaultdict(int, {GearPropType.incPAD: 2}))
gb.applyScroll(scroll: Scroll, count: int = 1) -> bool
```
Apply order form to `gear.scrollStat`
scroll: Create and deliver order form with `Scroll(name: str = None, stat: DefaultDict[GearPropType, int] = defaultdict(int)`
count: The number of times the order is applied, and if it is greater than the number of upgrades available, it is applied only until the number of available upgrades is exhausted.
Return True if more than one application is successful, False if no change

`gear.scrollStat`에 주문서 적용  
scroll: `Scroll(name: str = None, stat: DefaultDict[GearPropType, int] = defaultdict(int)`으로 주문서 생성, 전달  
count: 주문서 적용 횟수, 업그레이드 가능 횟수보다 클 경우 업그레이드 가능 횟수를 모두 소진할 때까지만 적용  
1작 이상 적용 성공시 True 반환, 변화 없을 시 False 반환  
```
gb.applySpellTraceScroll(probability: int, propType: GearPropType, count: int = 1) -> bool
```
Spell trace enhancement applied to `gear.scrollStat`
probability: The probability of the trace of the spell. 100, 70, 30, 15 only
propType: The type of trace of the order. incSTR, incDEX, incINT, incLUK, incMHP only
count: The number of times the order is applied, and if it is greater than the number of upgrades available, it is applied only until the number of available upgrades is exhausted.
Return True if more than one application is successful, False if no change

`gear.scrollStat`에 주문의 흔적 강화 적용  
probability: 주문의 흔적 확률. 100, 70, 30, 15만 가능  
propType: 주문의 흔적 종류. incSTR, incDEX, incINT, incLUK, incMHP만 가능  
count: 주문서 적용 횟수, 업그레이드 가능 횟수보다 클 경우 업그레이드 가능 횟수를 모두 소진할 때까지만 적용  
1작 이상 적용 성공시 True 반환, 변화 없을 시 False 반환  
```
gb.applyHammer() -> bool
```
Apply Golden Hammer enhancement
Returns True when application is successful, False when there is no change

황금망치 강화 적용  
적용 성공시 True 반환, 변화 없을 시 False 반환  
```
gb.applyStar(amazingScroll: bool = False, bonus: bool = False) -> bool
```
Star Force, Noljang reinforcement applied to `gear.starStat`
amazingScroll: if true, no surprise, if false, star force
bonus: Whether or not to apply the game bonus stat
Returns True when application is successful, False when there is no change

`gear.starStat`에 스타포스, 놀장 강화 적용  
amazingScroll: True일 경우 놀장, False일 경우 스타포스  
bonus: 놀장 보너스 스탯 적용 여부  
적용 성공시 True 반환, 변화 없을 시 False 반환  
```
gb.applyStars(count: int, amazingScroll: bool = False, bonus: bool = False) -> int
```
Star Force, Noljang reinforcement applied to `gear.starStat`
count: Number of Star Force enhancements. (Not a target number!)
amazingScroll: if true, no surprise, if false, star force
bonus: Whether or not to apply the game bonus stat
Return the number of successful application

`gear.starStat`에 스타포스, 놀장 강화 적용  
count: 스타포스 강화 횟수. (목표 별 개수 아님!)  
amazingScroll: True일 경우 놀장, False일 경우 스타포스  
bonus: 놀장 보너스 스탯 적용 여부  
적용 성공한 횟수 반환  
### Checking the applied set effect | 적용 중인 세트효과 확인
```
SetItem.evalSetItemEffect(equippedGears: List[Gear]) -> DefaultDict[GearPropType, int]
```
Passing the list of equipment currently worn will return the set effect option in effect. Wearable/duplicated is not tested unless the equipment ID is the same.
equippedGears: List of equipment you are wearing
Same as in-game logic, if there are multiple lucky items, the equipment with the lowest equipment ID is applied first among the lucky items included in the set effect.
The ERA Ignore option (GearPropType.imdR) has a float value

현재 착용 중인 장비 목록을 전달하면 적용 중인 세트효과 옵션을 반환. 착용 가능/중복 여부는 장비 ID가 동일한 경우 외에는 검사하지 않음.  
equippedGears: 착용 중인 장비 목록  
인게임 로직과 동일하게 럭키 아이템이 여러 개 있을 경우 세트효과에 포함되는 럭키 아이템 중 장비 ID가 가장 낮은 장비부터 우선 적용  
방어율 무시 옵션(GearPropType.imdR)은 값이 float임  
## Etc | 기타
### Among the GearPropTypes attached to Gear, those that affect dpm: Gear에 붙는 GearPropType 중 dpm에 영향을 주는 것들:
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
