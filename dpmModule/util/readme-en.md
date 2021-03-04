util.py
===========

Utility functions for calculate DPM easier.




- uitl.optimizer
  
  - Hyperstat optimization, union optimization, etc. are performed.

  - get_optimal_hyper_from_bare(spec : CharacterModifier, job, level : int) -> HyperStat
    
    - Compute the optimal hyperstat.

  - get_optimal_hyper_union(spec, job, otherspec, hyper, union) -> {"hyper" : newHyper, "union" : newUnion }
    
    - Calculate optimal hyperstats and unions.



- util.dpmgenerator
  
  - It supports builders and macro functions that can quickly calculate DPM without complicated settings.

  - IndividualDPMGenerator(job, template)

    - set_runtime(time) -> None
      
      - Set the operation time. Unit: ms

    - get_dpm(self, ulevel = 6000, weaponstat = [4,9], level = 240, printFlag = False)
      
      - Calculate dpm.



- util.configuration
  
  - DPM 계산에 사용되고 있는 값을 JSON으로 꺼내볼 수 있습니다.

  - export_configuration(jobname)
    
    - jobname 직업의 계산 설정을 출력합니다.
    - storage.export의 wrapper 함수입니다.