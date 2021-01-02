from dpmModule.util.dpmgenerator import IndividualDPMGenerator

job_name = '제로'
gen = IndividualDPMGenerator(job_name)
print(job_name, gen.get_dpm(ulevel=8000))
