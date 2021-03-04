Rules
========

Intro
------

- Rule is used to control graph execution. 

- All rules work like this: 

  - Elements received with get_related_element() are checked by the check() function before being executed. 
  - It cannot be executed if the check() function does not pass the check (that is, if False is returned). 

- Rule, in general, takes two arguments, A and B. At this time, the execution of object A is restricted by the state of object B. 



Type of Rule 
-------

- ConditionRule
  - For two GraphElements A,B and check_function, use A if check_function(B) returns True. 
  - This is the most common type of Rule. 

- UniquenessRule
  - This is the most basic and essential rule. If the given element is not on, use is prohibited. 
  - Without this Rule, it will continue to be used even if the buff or pet is already on. 

- ConcurrentRunRule
  - For two GraphElements A and B, it is forced to use only when A is using B. 
  - Use case. 
    - When attempting to hit a 90-second extreme (A) twice and one of them to a 150-second extreme (B): ```ConcurrentRunRule(B, A)```. 
  
- ReservationRule
  - For two GraphElements A,B, force A to use only when B is available. 
  - Use case. 
    - When trying to wait 150 seconds by setting the 90 second extreme skill (A) to the 150 second extreme skill (B): ```ReservationRule(A, B)```. 

- SynchronizeRule
  - If B is on, A can be used when the remaining time of B (buff or minion) is more than time(ms) (direction=1) / less than (direction=-1). 
  - If B is off, A can be used. 
  - If B is on, you can think of it as saving A. 
  - Use case. 용례.
    - When you want to use ?? (B) in the last 20 seconds of Infinity (A): ```SynchronizeRule(A, B, 40*1000, direction=-1)```. 

- MutualRule
  - Avoid using A when B is available. 

- InactiveRule
  - Avoid using A when B is being used. 

- DisableRule
  - Disable the use of the given GraphElement. 