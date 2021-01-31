Rules
========

Intro
------

- Rule is used to control graph execution. Rule은, 그래프의 실행을 제어하기 위해 사용됩니다.

- All rules work like this: 모든 Rule은, 다음과 같이 작동합니다.

  - Elements received with get_related_element() are checked by the check() function before being executed. get_related_element()로 받아온 element들은 실행되기 전에 check() 함수의 검사를 받습니다.
  - It cannot be executed if the check() function does not pass the check (that is, if False is returned). check() 함수의 검사를 통과하지 못하면(즉, False가 return 되면) 실행될 수 없습니다.

- Rule, in general, takes two arguments, A and B. At this time, the execution of object A is restricted by the state of object B. Rule은, 일반적으로 인자를 A, B 둘을 받습니다. 이 때, A object는 B object의 상태에 의해서 실행을 제한받게 됩니다.



Type of Rule | Rule의 종류
-------

- ConditionRule
  - For two GraphElements A,B and check_function, use A if check_function(B) returns True. 두 GraphElement A,B와 check_function에 대해, check_function(B)가 True를 리턴하면 A를 사용.
  - This is the most common type of Rule. 제일 일반적인 형태의 Rule입니다.

- UniquenessRule
  - This is the most basic and essential rule. If the given element is not on, use is prohibited. 제일 기본적이고 필수적인 Rule입니다. 주어진 Element가 on 상태가 아니면 사용을 금지합니다.
  - Without this Rule, it will continue to be used even if the buff or pet is already on. 이 Rule이 없다면, 버프나 소환수가 이미 켜져 있더라도, 계속 사용합니다.

- ConcurrentRunRule
  - For two GraphElements A and B, it is forced to use only when A is using B. 두 GraphElement A,B에 대해, A가 B를 사용중일 때만 사용하도록 강제합니다.
  - Use case. 용례.
    - When attempting to hit a 90-second extreme (A) twice and one of them to a 150-second extreme (B): ```ConcurrentRunRule(B, A)```. 90초 극딜기(A)를 두 번 돌리고, 그중 하나에 150초 극딜기(B)를 맞추려 할 때 : ```ConcurrentRunRule(B, A)```
  
- ReservationRule
  - For two GraphElements A,B, force A to use only when B is available. 두 GraphElement A,B에 대해, A가 B가 사용가능할 때만 사용하도록 강제합니다.
  - Use case. 용례.
    - When trying to wait 150 seconds by setting the 90 second extreme skill (A) to the 150 second extreme skill (B): ```ReservationRule(A, B)```. 90초 극딜기(A)를 150초 극딜기(B)에 맞춰서, 150초를 기다리게 하려 할 때 : ```ReservationRule(A, B)```

- SynchronizeRule
  - If B is on, A can be used when the remaining time of B (buff or minion) is more than time(ms) (direction=1) / less than (direction=-1). B가 켜져있다면, B(버프 또는 소환수) 의 남은 시간이 time(ms) 이상(direction=1) / 이하(direction=-1) 일 때 A를 사용할 수 있습니다.
  - If B is off, A can be used. B가 꺼져있다면, A를 사용할 수 있습니다.
  - If B is on, you can think of it as saving A. B가 켜져있을 경우 A를 아낀다고 생각하면 됩니다.
  - Use case. 용례.
    - When you want to use ?? (B) in the last 20 seconds of Infinity (A): ```SynchronizeRule(A, B, 40*1000, direction=-1)```. 인피니티(A)의 마지막 20초에 엔버링크(B)를 사용하고자 할 때 : ```SynchronizeRule(A, B, 40*1000, direction=-1)```

- MutualRule
  - Avoid using A when B is available. A를 B가 사용 가능할 때는 사용하지 않도록 합니다.

- InactiveRule
  - Avoid using A when B is being used. A를 B가 사용되고 있을 때는 사용하지 않도록 합니다.

- DisableRule
  - Disable the use of the given GraphElement. 주어진 GraphElement를 사용하지 못하도록 합니다.