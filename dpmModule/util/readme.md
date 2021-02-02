util.py
===========

Utility functions for calculate DPM easier.




- uitl.optimizer
  
  - 하이퍼스텟 최적화, 유니온 최적화 등을 수행합니다.

  - get_optimal_hyper_from_bare(spec : CharacterModifier, job, level : int) -> HyperStat
    
    - 최적 하이퍼스텟을 계산합니다.

  - get_optimal_hyper_union(spec, job, otherspec, hyper, union) -> {"hyper" : newHyper, "union" : newUnion }
    
    - 최적 하이퍼스텟과 유니온을 계산합니다.



- util.dpmgenerator
  
  - 복잡한 설정 없이 빠르게 DPM을 계산할 수 있는 builder와 macro 함수들을 지원합니다.

  - IndividualDPMGenerator(job, template)

    - set_runtime(time) -> None
      
      - 연산 시간을 설정합니다. 단위 : ms

    - get_dpm(self, ulevel = 6000, weaponstat = [4,9], level = 240, printFlag = False)
      
      - dpm을 계산합니다. 



- util.configuration
  
  - DPM 계산에 사용되고 있는 값을 JSON으로 꺼내볼 수 있습니다.

  - export_configuration(jobname)
    
    - jobname 직업의 계산 설정을 출력합니다.
    - storage.export의 wrapper 함수입니다.