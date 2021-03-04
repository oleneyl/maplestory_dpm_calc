

/kernel
===========


The kernel contains a set of modules needed for a program to actually work. 
Modules other than kernel are implemented so that dpmModule can be applied to actual situations. 
As for code, the kernel guides you through the basic operation of dpmModule. 

- abstract.py

  - Abstract class required for program operation is defined. 
  
- graph.py

  - The functions required for the internal operation of the simulation graph are defined. 
  
- policy.py

  - Classes for controlling simulation operation are defined. 

- core

  - This is a sub-module that defines the classes required for Maplestory DPM calculation. 
    
    - callback.py: The callback function is defined. 

    - constant.py: The constants such as Mc Dem, Bangmu, halved or final dem are defined. 

    - graph_element.py: Defined for `GraphElement`. 

    - modifier.py: Defines `CharacterModifier`, `SkillModifier` and other functions that change character specifications. 

    - result_object.py: A `ResultObject` representing the result of each action is defined. 

    - simulator.py: DPM calculation simulator and analyzer are defined. 

    - skill.py: Defines `AbstractSkill` and `DamageSkill`, `SummonSkill`, and `BuffSkill` based on it. 

    - skill_wrapper.py: Defines `AbstractSkillWrapper`, each skill wrapper based on it, and applied special wrappers. 

    - vmatrix.py: Defined for strengthening the V matrix core. 


Basic how dpmModule works 
-------------------------

dpmModule is designed to operate in the following order. 

# Define graph builder
# Build graph from builder
# Push graph into scheduler
# Run scheduler by session
# Analyze result from session by analytics

- Graph

  - -`Graph` is defined as the connection of GraphElements that have 0 or more links with direction. 
  - `GraphElement` is an operation unit that can perform action in simulation. The following things can be `GraphElement`. 
  
    - Specific buff (ex.'Maple Warrior' buff). 
    - Specific skills (ex.'Final Blow' skill). 
    - Conditions (ex.Check the cooldown of the'Infinity' skill). 
    - Stack, gauge (ex.'Lacness gauge' of'Luminous'). 
    
- Task
  
  - `Task` means the actual action performed when the simulation is running. The following things can be `Task`. 
  
    - 'Use' of a specific buff (ex.Use of the'Maple Warrior' buff).
    - 'Use' of specific skills (ex. use of'Final Blow' skill). 
    - 'Evaluation' of the condition (ex.Check if the'Infinity' skill is available). 
    - Decrease of stack and gauge (ex.Increase the `Largeness Gauge` of `Luminous` by 100). 
    
  - One `GraphElement` has one representative `Task`. This task can be obtained through `GraphElement.build_task()`.
  - To say that a GraphElement is `used` means that this representative `Task` is used. 

    - The representative task of buff skills is defined as the use of buffs. 
    - The representative task of attack skill is defined as the use of attack skill. 
         
  - However, one `GraphElement` can have multiple related `Tasks`. 
  
    - You may want to reduce the cooldown of buff skills
    - You may want to reset the cooldown of the attack skill. 공
    
  - To obtain these other tasks, you can use a method defined separately for each GraphElement. 
  
- Graph Element Cascading

  - When running a simulation, there are actions that must be followed after certain actions. 
  
    - Final Attack Skills: Must be activated immediately after the attack skill is activated. 
    - Stack type skill: After the skill is used, the stack must be changed. 
    - Linked skill: You must always use another skill after the skill is activated. 
    
  - After a specific GraphElement is used, several functions are supported to allow other GraphElements to be used. About GraphElement `origin`. 
    
    - origin.onAfter(target: GraphElement): target is used immediately after origin is used. 
    - origin.onBefore(target: GraphElement): The target is used just before origin is not used. 
    - origin.onTick(target: GraphElement): If origin is activated periodically, the target is used immediately after the periodic activation. 
  
- Logical and utility Graph Elements

  - The simulation conditions are not static. Each condition changes with each simulation run. 
  
     - Remaining cooldown of all skills. 
     - Gauge-type skill gauge. 
     
  - The creator of the simulation may wish to add logical elements for an optimized simulation. For this, this library supports `OptionalElement`. 
  
    - OptionalElement(disc : function, after : GraphElement, fail = None : GraphElement, name = "Optional Element" : string)
      
      - When this element is used, the disc function is executed, and if it is True, it uses after, and if it is False, it uses fail if it exists. 
      
  - In addition to this, several convenience elements are supported for the convenience of simulation production. 
    
    - RepeatElement : It is used when you want to use a specific element repeatedly. 
    - TaskHolder : It is simply a GraphElement for wrapping a specific task. 
    

- An example of actual Graph Element Cascading is provided below. 

  - Final Attack is activated after Dark Knight's Dark Impale is used. 
  
    ```python
    DarkImpail.onAfter(FinalAttack)
    ```

  - The Dark Knight's attacks are twofold. If Sacrifice is on, it uses Goongnil, otherwise it uses Impale. 

    ```python
    def InfGoungnil():
        return (Sacrifice.is_active() or Reincarnation.is_active()) # Determines whether Sacrifice is turned on or not. 
    
    BasicAttack = core.OptionalElement(InfGoungnil, GoungnilDescentNoCooltime, DarkImpail) # If it is on, it uses Goongnil, otherwise it uses Impale. 
    ```
    
  - The cooldown of Dark Knight's Sacrifice skill decreases by 0.3 seconds when non-holder skills are used. 
  
    ```python
    # SkillWrapper.controller(time, type) returns a GraphElement that changes the duration or cooldown of the target skill. 
    # Therefore, Sacrifice.controller(300,'reduce_cooltime') is a GraphElement that reduces the cooldown of Sacrifice by 0.3 seconds when used. 
    
    BiholderDominant.onTick(Sacrifice.controller(300,'reduce_cooltime'))
    BiholderShock.onAfter(Sacrifice.controller(300,'reduce_cooltime'))
    BiholderImpact.onTick(Sacrifice.controller(300,'reduce_cooltime'))
    ```
    
- Graph can be created as a collection of GraphElements. Graph is created like this: 

  - First, define the graph elements. 
  
    ```python
    from dpmModule.kernel.core import GraphElement 
    x = GraphElement('X')
    y = GraphElement('Y')
    z = GraphElement('Z')
    x.onAfter(x)
    ```
    
  - To define the graph, you need three things. 
    
    - `Executable graph element`. These can be used directly by the Simulator when the simulation is running (X, Y). 
    - `Non-executable graph element`. These cannot be used directly, but there are moments when they are used indirectly. such as onAfter. It is connected to'executable graph elements' through method (Z). 
    - `Default Graph Element` This element is the element that the simulation will use by default when there are no other available elements (X). 
    
    - In order to get all existing graph elements, the graph elements created so far are imported. 
      
      ```python
      from dpmModule.kernel.graph import GlobalOperation
      storage = GlobalOperation.export_storage_without_complex_option()
      ```
      
  - Finally, we put all three of these values together to create a graph. 
  
    ```python
    from dpmModule.kernel.policy import StorageLinkedGraph
    graph = StorageLinkedGraph(X, storage, accessible_elements=[X, Y])
    ```
    
- Two things are needed to operate the created graph. 

  - A `Policy` that sets the priority to use `GraphElement`. 
  - A `Rule` that determines whether the `GraphElement` is available within the priority.
  
  - Policy can be defined by inheriting `dpmModule.kernel.graph.FetchingPolicy`. 
  - Basically, we support TypebaseFetchingPolicy, which determines the priority according to the properties of GraphElement. 
  - If you want to use the buff first, increase your pet, and adopt a policy that uses attack skills, proceed as follows. 
  
    ```python
    from dpmModule.kernel.policy import TypebaseFetchingPolicy
    from dpmModule.kernel import core
    my_policy = TypebaseFetchingPolicy(priority_list = [
        core.BuffSkillWrapper,
        core.SummonSkillWrapper,
        core.DamageSkillWrapper
    ])
    ```
    
  - Rule can be defined by inheriting `dpmModule.kernel.graph.AbstractRule`. 
  - Basically, some useful rules are defined in `dpmModule.execution.rules`. 
  
    - `UniquenessRule` : This is the most basic and essential rule. If the given element is on, use is prohibited. 
    
    - `ConcurrentRunRule` : For both GraphElements A and B, force A to use only when B is in use. This is useful when you want to use extreme deals together. 
    
    - `ReservationRule` : For both GraphElements A and B, force B to use only when A is available. This is useful when you want to use extreme deals together. 
    
    - `MutualRule` : For two GraphElements A and B, it forces them not to be used together. 
    
    - In addition to this, there are various rules. 
    - If you do not want to use any rule, only `UniquenessRule` is applied. 
    
  - If Rule and Policy are defined, you can create Scheduler. Scheduler presents the next task to be used based on the given rule and policy. 
  
    ```python
    from dpmModule.kernel.policy import AdvancedGraphScheduler
    scheduler = AdvancedGraphScheduler(graph, fetching_policy=policy, rules=rules)
    ```
    
- Finally, it is the stage of the simulation. Simulation can be done through the Simulator object. 
  - After receiving the next task to be executed from the scheduler
  - Run the task
  - Spend time as much as the delay defined in the task. 
  - The results are saved and analyzed until the end of the simulation. 
  
  - Analytics is responsible for the analysis of the simulation. Example code is as follows: 
  
  ```python
  from dpmModule.kernel import core
  
  analytics = core.Analytics()  # Create an analyzer to analyze the data. 
  control = core.Simulator(scheduler, character, analytics) # Connect and create schedulers, characters, and analytics to the simulator. 
  # The character has not yet been covered in the text. This is because the Simulator is an object defined only for DPM calculations. 
  control.start_simulation(3600*1000) # 1 hours. 
  ```