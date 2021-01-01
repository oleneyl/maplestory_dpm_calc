from dpmModule.util.dpmgenerator import IndividualDPMGenerator

job_name = '히어로'
gen = IndividualDPMGenerator(job_name)
print(job_name, gen.get_dpm(ulevel=8000))
