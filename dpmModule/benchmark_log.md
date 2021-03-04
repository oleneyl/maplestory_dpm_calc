1. Operation speed before optimization. 최적화 이전 연산속도.
    
    Character creation request time: Total time 107 ms / 100
    Character creation request time: 1 ms, 0.001070 second
    Simulator creation time: Total time 2213 ms / 100
    Simulator generation time: 22 ms, 0.022 130 second
    Simulation: Total time 27385 ms / 20
    Simulation: 1369 ms, 1.369 250 second

    캐릭터 생성 요구시간 : 총 소요시간 107 ms / 100
    캐릭터 생성 요구시간 : 1 ms, 0.001070 second
    시뮬레이터 생성 시간 : 총 소요시간 2213 ms / 100
    시뮬레이터 생성 시간 : 22 ms, 0.022130 second
    시뮬레이션 : 총 소요시간 27385 ms / 20
    시뮬레이션 : 1369 ms, 1.369250 second

2. Caching ResultObject.

    Character creation request time: Total time 113 ms / 100
    Character creation request time: 1 ms, 0.001130 second
    Simulator creation time: Total time 2465 ms / 100
    Simulator creation time: 24 ms, 0.024650 second
    Simulation: Total time required ms / 20
    Simulation: 1324 ms, 1.324 250 second
    
    캐릭터 생성 요구시간 : 총 소요시간 113 ms / 100
    캐릭터 생성 요구시간 : 1 ms, 0.001130 second
    시뮬레이터 생성 시간 : 총 소요시간 2465 ms / 100
    시뮬레이터 생성 시간 : 24 ms, 0.024650 second
    시뮬레이션 : 총 소요시간 26485 ms / 20
    시뮬레이션 : 1324 ms, 1.324250 second
    
3. Damage Calculation check step add.

    Character creation request time: Total time 110 ms / 100
    Character creation request time: 1 ms, 0.001100 second
    Simulator creation time: Total time 2332 ms / 100
    Simulator generation time: 23 ms, 0.023320 second
    Simulation: Total time 18980 ms / 20
    Simulation: 949 ms, 0.949000 second

    캐릭터 생성 요구시간 : 총 소요시간 110 ms / 100
    캐릭터 생성 요구시간 : 1 ms, 0.001100 second
    시뮬레이터 생성 시간 : 총 소요시간 2332 ms / 100
    시뮬레이터 생성 시간 : 23 ms, 0.023320 second
    시뮬레이션 : 총 소요시간 18980 ms / 20
    시뮬레이션 : 949 ms, 0.949000 second
    
4. Character modifier calculation caching

    Character creation request time: Total time 171 ms / 100
    Character creation request time: 1 ms, 0.001710 second
    Simulator creation time: Total time 2421 ms / 100
    Simulator generation time: 24 ms, 0.024210 second
    Simulation: Total time 13708 ms / 20
    Simulation: 685 ms, 0.685 400 second

    캐릭터 생성 요구시간 : 총 소요시간 171 ms / 100
    캐릭터 생성 요구시간 : 1 ms, 0.001710 second
    시뮬레이터 생성 시간 : 총 소요시간 2421 ms / 100
    시뮬레이터 생성 시간 : 24 ms, 0.024210 second
    시뮬레이션 : 총 소요시간 13708 ms / 20
    시뮬레이션 : 685 ms, 0.685400 second
    
5. Printlog area optimization.

6. Using __iadd__ makes calculation faster due to not assigning new obejct.

7. Using __slots__ for fast access to data.

    Character creation request time: Total time 119 ms / 100
    Character creation request time: 1 ms, 0.001190 second
    Simulator creation time: Total time 2210 ms / 100
    Simulator generation time: 22 ms, 0.022 100 second
    Simulation: Total time 53400 ms / 100
    Simulation: 534 ms, 0.534000 second

    캐릭터 생성 요구시간 : 총 소요시간 119 ms / 100
    캐릭터 생성 요구시간 : 1 ms, 0.001190 second
    시뮬레이터 생성 시간 : 총 소요시간 2210 ms / 100
    시뮬레이터 생성 시간 : 22 ms, 0.022100 second
    시뮬레이션 : 총 소요시간 53400 ms / 100
    시뮬레이션 : 534 ms, 0.534000 second

8. Cacheing Meaningless Buff Modifier calculation.

    Character creation request time: Total time 106 ms / 100
    Character creation request time: 1 ms, 0.001060 second
    Simulator creation time: Total time 2201 ms / 100
    Simulator generation time: 22 ms, 0.022010 second
    Simulation: Total time 45817 ms / 100
    Simulation: 458 ms, 0.458 170 second

    캐릭터 생성 요구시간 : 총 소요시간 106 ms / 100
    캐릭터 생성 요구시간 : 1 ms, 0.001060 second
    시뮬레이터 생성 시간 : 총 소요시간 2201 ms / 100
    시뮬레이터 생성 시간 : 22 ms, 0.022010 second
    시뮬레이션 : 총 소요시간 45817 ms / 100
    시뮬레이션 : 458 ms, 0.458170 second

9. Using __slots__ for fast access to data ( Scheduler)

    Character creation request time: Total time 98 ms / 100
    Character creation request time: 0 ms, 0.000980 second
    Simulator creation time: Total time 2455 ms / 100
    Simulator creation time: 24 ms, 0.024550 second
    Simulation: Total time 42711 ms / 100
    Simulation: 427 ms, 0.427 110 second

    캐릭터 생성 요구시간 : 총 소요시간 98 ms / 100
    캐릭터 생성 요구시간 : 0 ms, 0.000980 second
    시뮬레이터 생성 시간 : 총 소요시간 2455 ms / 100
    시뮬레이터 생성 시간 : 24 ms, 0.024550 second
    시뮬레이션 : 총 소요시간 42711 ms / 100
    시뮬레이션 : 427 ms, 0.427110 second


Core problem: It was in the calculation of getBuffedModifier().
    --> The calculation speed can be increased by caching the calculation of this value.

핵심 문제점 : getBuffedModifier()의 계산에 있었음.
    --> 이 값의 계산을 caching하면 연산 속도 증대 가능.

