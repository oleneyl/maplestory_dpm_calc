
JobGenerator
==============================

- 직업을 시뮬레이션하기 위해서 우리는 JobGenerator class를 활용합니다. 
- Jobgenerator는 다음과 같은 과정을 통해 직업의 스킬 사용방식이 정의된 SimluationGraph를 리턴하는것이 목적입니다.
- graph를 생성하는 방법은 두 가지를 제공압니다.
  - JobGenerator.package (chtr : ck.Character, vEhc : jt.VEnhancer, kwargs)
    
    * package는 직업 시뮬레이션에 관련된 정보를 연산하기 위해서 호출되는 함수입니다. 
    * package는 직업 그래프를 생성하고, 직업이 기본적으로 가지고 있는 성능을 적용하고, 하이퍼/유니온 스펙을 최적화하는 등
      부차적인 모든 작업을 자동으로 수행합니다.

  - JobGenerator.package_bare (chtr : ck.Character, vEhc : jt.VEnhancer, kwargs)

    * package_bare는 제공된 character에는 어떠한 병경도 하지 않고, 오직 설정되어 있는 직업 그래프만을 생성합니다.

  - 내부적으로는 아래와 같은 절차를 거치도록 되어있습니다.
    ```
    <-- Jobgenerator.package()
    직업의 패시브를 적용하고, 최적의 무기스텟, 링크 등을 계산하여 적용합니다.
    <-- JobGenerator.package_bare()
    -------|
           JobGenerator.build( chtr )
           * build 함수는 오로지 그래프만을 생성하는것이 목적입니다.
           * build 함수는 내부적으로는 generate()를 호출하는것과 큰 차이가 없습니다.
           -------|
                  JobGenerator.generate(chtr, vEhc, kwargs)
                  * generate에서는 실제로 jt.ScheduleGraph()를 생성하고, 내부 함수를 이용하여 Graph를 빌드하여 리턴합니다.
           |------|
           |
    |------|
     ```

- 새로운 직업의 JobGenerator를 정의하고 싶다면 다음 함수들을 override하면 됩니다.

  - __init__(self, vEhc = None)

    아래 값들을 올바른 값으로 다시 초기화 합니다.
    
    - self.buffrem : 버프 지속시간이 중요한 직업인지 표시합니다.
    - self.vEnhanceNum : 5차 코어를 통해 강화되는 스킬의 수입니다.
    - self.vSkillNum : 사용하는 5차 스킬의 개수입니다. 베놈 버스트와 같은 것을 제외하면됩니다.
    - self.jobtype : 주스텟입니다. "str", "int", "luk", "dex" 중 하나.
    - self.ability_list : 사용 어빌리티입니다. Ability_tool.get_ability_set 함수를 사용합니다.
    - self._use_critical_reinforce : 크리티컬 리인포스 보유 여부입니다.

  - apply_complex_options(self, chtr)

    일반적인 스텟이 아닌 변경사항을 입력합니다.
    - Example
      
      ```python
      chtr.buff_rem += 50 : 추가적인 버프 지속시간 증가스킬을 가지고 있는 경우
      chtr.add_property_ignorance(10) : 추가적인 속성무시 능력을 가지고 있는 경우
      ```

  - get_ruleset(self)

    본인이 생각하는 최적 딜사이클을 위한 Rule을 정의합니다. 필수적이지는 않습니다.

  - get_passive_skill_list(self)

    패시브 스킬을 정의합니다. dpmModule.kernel.core.InformedCharacterModifier를 사용합니다.

    `self.combat`은 컴뱃 오더스의 레벨입니다.

    `passive_level`은 패시브 스킬 레벨 증가 어빌리티와 컴뱃 오더스를 합친 수치입니다.

    - Example
      
      ```python
      passive_level = chtr.get_base_modifier().passive_level + self.combat
        
      HighWisdom = core.InformedCharacterModifier("하이 위즈덤", stat_main = 40)
      SpellMastery = core.InformedCharacterModifier("스펠 마스터리", att = 10)
      MagicCritical = core.InformedCharacterModifier("매직 크리티컬", crit = 30, crit_damage = 13)
      ElementAmplication = core.InformedCharacterModifier("엘리멘트 엠플리피케이션", pdamage = 50)
        
      ElementalReset = core.InformedCharacterModifier("엘리멘탈 리셋", pdamage_indep = 40)
        
      MasterMagic = core.InformedCharacterModifier("마스터 매직", att = 30 + 3*passive_level, buff_rem = 50 5*passive_level)
      ArcaneAim = core.InformedCharacterModifier("아케인 에임", armor_ignore = 20 + ceil(passive_level / 2))
        
      return [HighWisdom, SpellMastery, MagicCritical, ElementalReset, 
                                    MasterMagic, ElementAmplication, ArcaneAim]  # 마지막에 정의한 패시브 스킬정보를 리턴해야 합니다.
      ```
    
  - get_not_implied_skill_list(self)
    
    패시브처럼 적용되지만, 1. 무기상수/숙련도이거나 2. 전투가 시작되어야 발동되는 옵션을 여기에 정의합니다.
  
    - Example
       
      ```python
      def get_not_implied_skill_list(self):
      WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 20)  # 무기상수
      Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -2.5)  # 숙련도
      ExtremeMagic = core.InformedCharacterModifier("익스트림 매직", pdamage_indep = 20)  # 익스트림 매직은 전투가 시작되어야 스텟에 반영됩니다.
      ArcaneAim = core.InformedCharacterModifier("아케인 (실시간)", pdamage = 40)
      PerventDrain = core.InformedCharacterModifier("퍼번트 드레인", pdamage_indep = 25)
      ElementalResetActive = core.InformedCharacterModifier("엘리멘탈 리셋(사용)", prop_ignore = 10)
      
      return [WeaponConstant, Mastery, ExtremeMagic, PerventDrain, ArcaneAim, ElementalResetActive] # 마지막에 리턴해야 합니다.
      ```

  - generate(self, vEhc, chtr : AbstractCharacter, combat : bool = False):
    
    스킬 그래프를 구성합니다. 다음과 같은 순서로 그래프를 구성합니다.

    1. 스킬 그래프 오브젝트를 생성합니다. 스킬 오브젝트는 세 단계로 생성합니다.

      - 스킬 오브젝트를 생성합니다.
        ```python
        core.BuffSkill("메디테이션", 0, 240000, att = 30, rem = True, red = True) # 버프스킬
        core.SummonSkill("이프리트", 600, 3030, 150+2*self.combat, 3, (260+5*self.combat)*1000) # 소환스킬
        core.DamageSkill("페럴라이즈", 600, 220 + 3*self.combat, 7+1, modifier = core.CharacterModifier(pdamage = 10)) # 공격스킬.
        
        core.DamageSkill("도트 퍼니셔", 690, 400+vEhc.getV(0,0)*15, 5, cooltime = 25 * 1000, red = True) # 5차인 경우 getV(first_priority, second_priority)로 스킬 레벨을 가져옵니다.
        ```

      - 4차 이하 및 하이퍼 스킬이고 강화 코어가 존재하는 경우, 강화 수치를 적용합니다.
        ```python
        Paralyze = core.DamageSkill("페럴라이즈", 600, 220 + 3*self.combat, 7+1, modifier = core.CharacterModifier(pdamage = 10)).setV(vEhc, 1, 2, False) #setV(vEhc, priority, increment, crit_rate) 
        ```

      - 5차 스킬일 경우 강화 우선순위를 적용합니다.
        ```python
        DotPunisher = core.DamageSkill("도트 퍼니셔", 690, 400+vEhc.getV(0,0)*15, 5, cooltime = 25 * 1000, red = True).isV(vEhc,0,0) #isV(vEhc, skill_importance, enhance_importance)
        ```
        
      - 마지막으로, wrapper로 감싸서 스킬 그래프 오브젝트를 생성합니다.
        ```python
        Paralyze = core.DamageSkill("페럴라이즈", 600, 220 + 3*self.combat, 7+1, modifier = core.CharacterModifier(pdamage = 10)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper) # wrap(core.DamageSkillWrapper) 로 오브젝트를 감싸고 리턴합니다.
        ```

    2. 스킬 간의 연계가 있는 경우 서로 연결합니다. 스킬들을 연결하는 방법은 여러가지가 있습니다.

       - 패럴라이즈 이후에는 메테오 패시브, 이그나이트가 발생합니다.
         ```python
         Paralyze.onAfter(Ignite)
         ```
       
       - 카이저는 변신 여부에 따라 스킬이 다르게 시전됩니다.
         ```python
         BasicAttack.onAfter(core.OptionalElement(DrakeSlasher.is_available, DrakeSlasher, GigaSlasher, name = "드라코 슬래셔 충전시"))
         ```

       - 아란의 아드레날린 스킬은 콤보가 1000보다 커야 사용할 수 있습니다.
         ```python
         AdrenalineBoost.onConstraint(core.ConstraintElement('콤보가 1000이상', Combo, partial(Combo.judge,1000,1) ))
         ```

    3. 마지막으로, 시전 가능한 스킬들을 리스트로 만들어 리턴합니다.
      - 직접적으로 시전할 수 없는 스킬들은 넣지 않습니다.
      - 소환수는 시전할 수 없어도 넣어야 합니다(그렇지 않으면 계산이 되지 않습니다)
      - 필요한 경우, ensure() 함수를 통해 조건을 만족하지 않는 경우 주어진 값을 None으로
        만들 수 있습니다. None으로 전달된 요소들은 무시됩니다.
        
      - Example

        ```python
        return (Paralyze, 
                [Infinity, Meditation, EpicAdventure, OverloadMana.ensure(vEhc,1,5),
                globalSkill.maple_heros(chtr.level, combat_level=self.combat), globalSkill.useful_sharp_eyes(), globalSkill.useful_combat_orders(), globalSkill.useful_wind_booster(),
                globalSkill.MapleHeroes2Wrapper(vEhc, 0, 0, chtr.level, self.combat), globalSkill.soul_contract()] +\
                [DotPunisher.ensure(vEhc,0,0), PoisonChain, Meteor, MegidoFlame, FlameHeize, MistEruption, PoisonNova.ensure(vEhc,2,1), MirrorBreak, MirrorSpider] +\
                [Ifritt, FireAura, FuryOfIfritt.ensure(vEhc,3,2),
                    SlimeVirus, ParalyzeDOT, MistDOT, PoisonBreathDOT, IfrittDot, HeizeFlameDOT, TeleportMasteryDOT, MegidoFlameDOT, DotPunisherDOT.ensure(vEhc,0,0), PoisonNovaDOT.ensure(vEhc,2,1), PoisonChainToxic] +\
                [UnstableMemorize] +\
                [Paralyze])
        ```

        - 

      


