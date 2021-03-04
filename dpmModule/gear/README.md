# maplegear_python
for maplestory_dpm_calc

## Example:
### 리소스에서 장비 ID 검색.
```
Gear.searchIDsByName(name="앱솔랩스 아처후드")  # exact=True
```
정확히 일치하는 모든 장비 ID list 반환.
```
Gear.searchIDsByName(name="응축", exact=False)
```
검색어를 포함하는 모든 장비 ID list 반환.
### 리소스에서 장비 불러오기
```
Gear.createGearFromID(gearID=1004424)
```
리소스에 장비 ID가 존재할 경우 해당 장비 반환, 없을 경우 기본 장비 반환.
### 장비 강화하기 (GearBuilder).
Gear에 직접 수치를 적용할 수도 있지만 GearBuilder를 사용하면 인게임 방식대로 간단하게 강화가 가능합니다.
```
gb = GearBuilder(gear)
```
또는
```
gb.setGear(gear)
```
로 초기화
```
gb.applyAdditionalStat(propType: GearPropType, grade: int, isDoubleAdd: bool = False) -> bool
```
`gear.additionalStat`에 추가옵션 적용.
`GearPropType.allstat` 전달 시 올스탯% 추옵 적용, 실제로는 STRr, DEXr, INTr, LUKr로 대체됨
propType: incSTR, incDEX, incINT, incLUK, incMHP, incMMP, incPAD, incMAD, incPDD, incSpeed, incJump, imdR, damR, bdR, incAllStat(올스탯%), reduceReq만 가능  
grade: 1 ~ 7, 7이 가장 높고 1이 가장 낮은 옵션. 보스 드랍템의 경우 강환불로 3 ~ 6등급, 영환불로 4 ~ 7등급이 붙고 일반 드랍템의 경우 강환불로 1 ~ 4등급, 영환불로 2 ~ 5등급이 붙음. 파프니르 무기 1추=7등급  
isDoubleAdd: 이중추옵  
적용 성공시 True 반환, 변화 없을 시 False 반환  
```
gb.scrollAvailable() -> int
```
업그레이드 가능 횟수 반환.
```
scroll = Scroll("방어구 공격력 주문서", defaultdict(int, {GearPropType.incPAD: 2}))
gb.applyScroll(scroll: Scroll, count: int = 1) -> bool
```
`gear.scrollStat`에 주문서 적용  
scroll: `Scroll(name: str = None, stat: DefaultDict[GearPropType, int] = defaultdict(int)`으로 주문서 생성, 전달  
count: 주문서 적용 횟수, 업그레이드 가능 횟수보다 클 경우 업그레이드 가능 횟수를 모두 소진할 때까지만 적용  
1작 이상 적용 성공시 True 반환, 변화 없을 시 False 반환  
```
gb.applySpellTraceScroll(probability: int, propType: GearPropType, count: int = 1) -> bool
```
`gear.scrollStat`에 주문의 흔적 강화 적용  
probability: 주문의 흔적 확률. 100, 70, 30, 15만 가능  
propType: 주문의 흔적 종류. incSTR, incDEX, incINT, incLUK, incMHP만 가능  
count: 주문서 적용 횟수, 업그레이드 가능 횟수보다 클 경우 업그레이드 가능 횟수를 모두 소진할 때까지만 적용  
1작 이상 적용 성공시 True 반환, 변화 없을 시 False 반환  
```
gb.applyHammer() -> bool
```
황금망치 강화 적용  
적용 성공시 True 반환, 변화 없을 시 False 반환  
```
gb.applyStar(amazingScroll: bool = False, bonus: bool = False) -> bool
```
`gear.starStat`에 스타포스, 놀장 강화 적용  
amazingScroll: True일 경우 놀장, False일 경우 스타포스  
bonus: 놀장 보너스 스탯 적용 여부  
적용 성공시 True 반환, 변화 없을 시 False 반환  
```
gb.applyStars(count: int, amazingScroll: bool = False, bonus: bool = False) -> int
```
`gear.starStat`에 스타포스, 놀장 강화 적용  
count: 스타포스 강화 횟수. (목표 별 개수 아님!)  
amazingScroll: True일 경우 놀장, False일 경우 스타포스  
bonus: 놀장 보너스 스탯 적용 여부  
적용 성공한 횟수 반환  
### 적용 중인 세트효과 확인
```
SetItem.evalSetItemEffect(equippedGears: List[Gear]) -> DefaultDict[GearPropType, int]
```
현재 착용 중인 장비 목록을 전달하면 적용 중인 세트효과 옵션을 반환. 착용 가능/중복 여부는 장비 ID가 동일한 경우 외에는 검사하지 않음.  
equippedGears: 착용 중인 장비 목록  
인게임 로직과 동일하게 럭키 아이템이 여러 개 있을 경우 세트효과에 포함되는 럭키 아이템 중 장비 ID가 가장 낮은 장비부터 우선 적용  
방어율 무시 옵션(GearPropType.imdR)은 값이 float임  
## 기타
### Gear에 붙는 GearPropType 중 dpm에 영향을 주는 것들:
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
