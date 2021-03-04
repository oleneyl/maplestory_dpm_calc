jobs.py
======================


- In jobs.py, there is a graph that defines the skill composition and skill mechanism of real jobs. 


Organization of files
-----------------------------------

- Within the code, the mechanism by which each job is counted is defined. 
- In the `generate` function in the code file. 코드 파일 내의 
- The code in the `generate` function is structured as follows. 

  - `Comment`: This is a description of the setting implicitly applied to the code. 
  - `Skill Definition`: The values required for skill use are hard-coded. In actual calculation, the calculation is performed based on the corresponding value. 
  - `Graph Composition`: When the `Skill Definition` area is over, the connection relationship of each skill is defined. 
  - `return`: Returns a list of skills that can be used directly. 

- Passive skills and their effects are defined in the `get_passive_skill_list` function. 
- In the `get_not_implied_skill_list` function, the effects applied at the time of battle and the weapon constant / skill level are defined. 
- In the `get_ruleset` function, rules for optimizing DPM calculations are written. 
- Special values necessary for calculating job performance are defined in the `apply_complex_option` function. 

Writing your own JobGenerator
------------------------------------------------------------
  - ```warning
    This guide is not yet complete. Rather than creating a new JobGenerator, it is recommended to change the job file that already exists.
    If you want to make it yourself, ask for an issue when there is a blockage.
    ```

  - For simulation, you need to create a graph made of GraphElements. GraphElement consists of: 

    - time - A variable containing the dependency. This value is updated at every simulation step. 
    - buildTask() function. Define what happens when that graph element is executed. 
    - A controller function that can change its own state. Each graph element changes the state of each other through a controller. 
  
  - Examples of GraphElements are as follows. See kernel.core for more details. 

    - `공격스킬` (Attack Skill)
    - `버프스킬` (Buff Skill)
    - `소환스킬` (Summon Skill)
    - `도트 데미지` (Dot Damage)
    - `조건` (condition)
    - `반복` (Repeat)
    - `제한` (Limit)

- Each GraphElement can be connected to other GraphElements through the following functions. 

    - By calling the onAfter() and onAfters() functions, you can define the actions to follow after the corresponding GraphElement has been performed. 
      
      - For example, a final attack is always triggered after Storm's Poetry. So you need a syntax like this: 
        
        ```python
        ArrowOfStorm.onAfter(AdvancedFinalAttack)
        ```

    - Calls to the onBefore() and onBefores() functions allow you to define what happens before the corresponding GraphElement is performed. 

    - By calling the onTick() function, you can make that GraphElement be called at a specific cycle. 

      - For example, Ignite triggers after Ifrit's attack. This is not the point of eprit's `summons`, so it should be assigned to `onTick`, not `onAfter`.

        ```python 
        Ifritt.onTick(Ignite)
        ```
    - Other Users-You can define actions to be performed after a specific Task of the GraphElement through a defined function call. 

    - Note: Objects connected to GraphElement must *must* be GraphElement This is essential to maintain the overall maintainence of the program. 


- When the connection relationship of GraphElements is defined, you can build the Task Graph by calling the buildGraph() function. 

- The build of the Task Graph proceeds through the following process.

  - Initially, we pass the starting targets as arguments. BuildTask() of the started target GraphElements received is called. 
  - The buildTask() function creates a Task object that contains a function that defines the task to be done by itself. 
  - After that, by calling buildTask() of graphs connected to GraphElement through onAfter(), onBefore(), etc., the task obtained through their buildTask() is properly linked with the own task. 
  - This is done recursively, and when there are no more GraphElements connected (i.e. when all traversals have reached the endpoint of the Graph), it completes and returns the resulting Task. 
  - Through such a task, you can get a unique graph and an individual task. 

- To make it easier for users to understand the connection relationship of Graph, this program supports the built-in function of GraphElements, getLink(). 
  When the getLink() function is called, it returns a list of [self, connected GraphElement, connection type]. By calling the getLink() function recursively, you can find out the network of all GraphElements connected to a specific GraphElement. 

- Link can have the following properties: You can see which element is connected through the Link property. 
  
  - `before`
  - `after`
  - `effect`
  - `repeat`
  - `check`
  - `tick`


- generate

  - For practical graph building, the jobs package utilizes characterKernel.JobGenerator. 
    characterKernel.JobGenerator is a builder that builds graph settings based on character properties. In addition, the builder holds the properties of the built graph, and can use them to call the properties of the built graph. 

  - jobGenerator holds the following properties. 

    - `buffrem` : The duration of the buff. 
    - `jobtype` : This is the core stat. 
    - `vEhc` : It is an object that contains the 5th skill enhancement information. 
    - `SkillNum` : The number of 5th skills to use. 
    - `vEnhanceNum` : This is the number of possible 5th enhancement skills. 
    - `passiveSkillList` : This is a list of passive skill effects. It doesn't count until generate. 

Other files
-----------------------

In addition to the job code, there are `globalSkill.py` and `jobutils.py` in the jobs module. 

- `globalSkill.py` : Includes common skills used by several professions. 
  - Maple Warrior
  - Soul Contract
  - Common 5th skill (useful skill, Spider in Mirror, Maple World Goddess' blessing, etc.)
  - Genesis weapon skill
- `jobutils.py` : Contains special logic required for some classes. 
  - Skill replication
  - Weapon attack power
  - Debug | 디버그

There are `jobbranch` and `jobclass` as submodules of jobs. Here, common skills for each class and class are stored. 

Skills that are used only by a specific class and class are included in the class code. 

The skills of a single class are implemented in the script for that class. (Zero, Kinesis, Hoyoung). 

- The jobbranch module includes: jobbranch 모듈은 다음을 포함합니다.
  - `warriors.py` : This is a common skill for warriors. 
  - `magicians.py` : This is a common skill for wizards. 
  - `bowmen.py` : This is a common archer skill. 
  - `thieves.py` : This is a common skill for thieves. (Excluding Venom Burst). 
  - `pirates.py` : This is a common skill for pirates. 
- The jobclass module contains: 
  - `adventurer.py` : This is a common skill for adventurers. 
  - `cygnus.py` : This is a common skill for the Knights of Cygnus. 
  - `heroes.py` : This is a common skill for heroes. 
  - `resistance.py` : Resistance (excluding daemons) is a common skill. 
  - `demon.py` : Demon common skill. 
  - `nova.py` : Nova common skill. 
  - `flora.py` : This is a common skill for Lef. 
