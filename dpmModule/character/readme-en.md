
JobGenerator
==============================

- To simulate a job we use the JobGenerator class.
- The purpose of Jobgenerator is to return SimluationGraph, which defines the method of using the skill of the job through the following process.
- There are two ways to create a graph. 
  - JobGenerator.package (chtr : ck.Character, vEhc : jt.VEnhancer, kwargs)
    
    * package is a function called to compute information related to job simulation.
    * The package automatically performs all the secondary tasks, such as creating a job graph, applying the basic capabilities of the job, optimizing hyper/union specifications, and so on.

  - JobGenerator.package_bare (chtr : ck.Character, vEhc : jt.VEnhancer, kwargs)

    * package_bare does not make any changes to the provided character, it only creates job graphs that have been set.

  - Internally, the procedure is as follows. 
    ```
    <-- Jobgenerator.package()
    Apply class passive, calculate and apply optimal weapon stats, links, etc. 
    <-- JobGenerator.package_bare()
    -------|
           JobGenerator.build( chtr )
           * The build function is only intended to generate graphs. 
           * Internally, the build function is no different from calling generate(). 
           -------|
                  JobGenerator.generate(chtr, vEhc, kwargs)
                  * In generate, jt.ScheduleGraph() is actually created, and the graph is built and returned using an internal function.
           |------|
           |
    |------|
     ```

- If you want to define a new job JobGenerator, you can override the following functions. 

  - __init__(self, vEhc = None)

    Reset the values below to the correct values. 
    
    - self.jobname : Job name. 
    - self.jobtype : This is ??. One of "STR", "DEX", "INT", "LUK", "LUK2", "HP" or "xenon". 
    - self.buffrem : Shows if the buff duration is an important class. 
    - self.vEnhanceNum : The number of skills strengthened through the 5th core. 
    - self.vSkillNum : The number of 5th skills to use. Except for things like Venom Burst. 
    - self.ability_list : This is the ability to use. Use the Ability_tool.get_ability_set function. 
    - self._use_critical_reinforce : Whether or not you have a critical reinforcement. 

  - apply_complex_options(self, chtr)

    Enter changes that are not the usual stats. 
    - Example
      
      ```python
      chtr.buff_rem += 50 # If you have an additional buff duration increase skill. 
      chtr.add_property_ignorance(10) # If you have the ability to ignore additional defence. 
      ```

  - get_ruleset(self)

    Defines the rule for the optimal damage cycle that I think. It is not essential. 

  - get_passive_skill_list(self)

    Defines a passive skill. I use dpmModule.kernel.core.InformedCharacterModifier. 

    `self.combat` is the level of Combat Orders. 

    `passive_level` is the sum of the passive skill level increase ability and combat order. 

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
                                    MasterMagic, ElementAmplication, ArcaneAim]  # The last defined passive skill information should be returned. 
      ```
    
  - get_not_implied_skill_list(self)
    
    It is applied like a passive, but is 1. Weapon constant/skilled or 2. Defined here an option that is activated only after the battle begins. 
  
    - Example
       
      ```python
      def get_not_implied_skill_list(self):
      WeaponConstant = core.InformedCharacterModifier("무기상수", pdamage_indep = 20)  # IED constant. 
      Mastery = core.InformedCharacterModifier("숙련도", pdamage_indep = -2.5)  # Mastery. 숙련도.
      ExtremeMagic = core.InformedCharacterModifier("익스트림 매직", pdamage_indep = 20)  # Extreme Magic will not be reflected in your stats until the battle begins. 
      ArcaneAim = core.InformedCharacterModifier("아케인 (실시간)", pdamage = 40)
      PerventDrain = core.InformedCharacterModifier("퍼번트 드레인", pdamage_indep = 25)
      ElementalResetActive = core.InformedCharacterModifier("엘리멘탈 리셋(사용)", prop_ignore = 10)
      
      return [WeaponConstant, Mastery, ExtremeMagic, PerventDrain, ArcaneAim, ElementalResetActive]
      ```

  - generate(self, vEhc, chtr : AbstractCharacter, combat : bool = False):
    
    Build the skill graph. Build the graph in the following order. 

    1. Create a skill graph object. Skill objects are created in three stages. 

      - Create a skill object. 
        ```python
        core.BuffSkill("메디테이션", 0, 240000, att = 30, rem = True, red = True) # Buff Skill. 
        core.SummonSkill("이프리트", 600, 3030, 150+2*self.combat, 3, (260+5*self.combat)*1000) # Summoning skill. 
        core.DamageSkill("페럴라이즈", 600, 220 + 3*self.combat, 7+1, modifier = core.CharacterModifier(pdamage = 10)) # Attack skill. 
        
        core.DamageSkill("도트 퍼니셔", 690, 400+vEhc.getV(0,0)*15, 5, cooltime = 25 * 1000, red = True) # For 5th order, get the skill level with getV(first_priority, second_priority). 
        ```

      - If it is a 4th or lower and hyper skill and has a reinforced core, the reinforcement value is applied. 
        ```python
        Paralyze = core.DamageSkill("페럴라이즈", 600, 220 + 3*self.combat, 7+1, modifier = core.CharacterModifier(pdamage = 10)).setV(vEhc, 1, 2, False) #setV(vEhc, priority, increment, crit_rate) 
        ```

      - For the 5th skill, the reinforcement priority is applied. 
        ```python
        DotPunisher = core.DamageSkill("도트 퍼니셔", 690, 400+vEhc.getV(0,0)*15, 5, cooltime = 25 * 1000, red = True).isV(vEhc,0,0) #isV(vEhc, skill_importance, enhance_importance)
        ```
        
      - Finally, wrap it in a wrapper to create a skill graph object. 
        ```python
        Paralyze = core.DamageSkill("페럴라이즈", 600, 220 + 3*self.combat, 7+1, modifier = core.CharacterModifier(pdamage = 10)).setV(vEhc, 1, 2, False).wrap(core.DamageSkillWrapper) # Wrap the object with wrap(core.DamageSkillWrapper) and return. wrap(core.DamageSkillWrapper)
        ```

    2. If there is linkage between skills, link them together. There are many ways to connect skills. 

       - Meteor Passive and Ignite occur after Paralyze.
         ```python
         Paralyze.onAfter(Ignite)
         ```
       
       - Kaiser's skill is cast differently depending on whether he is transformed or not.
         ```python
         BasicAttack.onAfter(core.OptionalElement(DrakeSlasher.is_available, DrakeSlasher, GigaSlasher, name = "드라코 슬래셔 충전시"))
         ```

       - Aran's Adrenaline Skill can only be used with a combo greater than 1000. 
         ```python
         AdrenalineBoost.onConstraint(core.ConstraintElement('콤보가 1000이상', Combo, partial(Combo.judge,1000,1) ))
         ```

    3. Finally, it returns a list of castable skills. 
      - Skills that cannot be cast directly are not included. 
      - Minions must be added even if they cannot be cast (otherwise they will not be counted). 
      - If necessary, the given value can be made None if the condition is not satisfied via the ensure() function. Elements passed as None are ignored. 
        
      - Example

        ```python
        class MirrorBreakWrapper(core.DamageSkillWrapper):
          def __init__(self, vEhc, num1, num2, modifier) -> None:
            super(MirrorBreakWrapper, self).__init__(
              core.DamageSkill("스파이더 인 미러(공간 붕괴)", 720, 450+18*vEhc.getV(num1, num2), 15, cooltime = 250*1000, red = True, modifier=modifier)
            )

          def ensure(self, chtr: AbstractCharacter) -> bool:
            return chtr.level >= 235
        ```

        

      


