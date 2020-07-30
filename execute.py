import getopt, sys
import dpmModule
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
import dpmModule.character.characterTemplateHigh as template

def main(argv):
    FILE_NAME = argv[0]
    JOB_NAME = ""
    UNION_LEVEL = ""
    UNION_PRESET = {
        '4000': template.getU4000CharacterTemplate,
        '5000': template.getU5000CharacterTemplate,
        '6000': template.getU6000CharacterTemplate,
        '7000': template.getU7000CharacterTemplate,
        '8000': template.getU8000CharacterTemplate,
        '8500': template.getU8500CharacterTemplate
    }

    try:
        opts, _ = getopt.getopt(argv[1:], "hj:u:", ["help", "job=", "union="])
    
    except getopt.GetoptError:
        print(FILE_NAME, '-j <job name> -u <union level>')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(FILE_NAME, '-j <job name> -u <union level>')
            sys.exit()
        
        elif opt in ("-j", "--job"):
            JOB_NAME = arg

        elif opt in ("-u", "--union"):
            UNION_LEVEL = arg

    if len(JOB_NAME) < 1:
        print(FILE_NAME, "-j option is mandatory")
        sys.exit(2)

    if len(UNION_LEVEL) < 1:
        print(FILE_NAME, "-u option is mandatory")
        sys.exit(2)

    if UNION_LEVEL not in UNION_PRESET:
        print(FILE_NAME, "invalid -u option")
        sys.exit(2)

    gen = IndividualDPMGenerator(JOB_NAME, UNION_PRESET[UNION_LEVEL])
    print(JOB_NAME, gen.get_dpm(ulevel = 8000))


if __name__ == '__main__':
    main(sys.argv)
