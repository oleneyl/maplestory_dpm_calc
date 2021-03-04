from dpmModule.util.dpmgenerator import IndividualDPMGenerator

job_name = '제로'  # Zero
gen = IndividualDPMGenerator(job_name)
print(job_name, gen.get_dpm(spec_name="8000", ulevel=8000))
