import os
import random
import sys
import pickle

from game import Game
from learning import Learning
from instance import create_random_instance, read_from_file


def default(str):
    return str + ' [Default: %default]'


def readCommand(argv):
    """
    Processes the command used to run pacman from the command line.
    """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python gardener.py <options>
    """
    parser = OptionParser(usageStr)

    parser.add_option('--horizon', dest='horizon', type='int',
                      help=default(
                          'horizon of ASP FR'),
                      metavar='HORIZON', default=5)
    parser.add_option('--radius', dest='radius', type='int',
                      help=default(
                          'radius of ASP FR'),
                      metavar='RADIUS', default=6)
    parser.add_option('--cache', dest='cache', type='int',
                      help=default(
                          'cache of ASP FR'),
                      metavar='RADIUS', default=1)
    parser.add_option('-n', '--numInst', dest='numInst', type='int',
                      help=default(
                          'the number of INSTANCES to generate (per setting)'),
                      metavar='INSTANCES', default=10)
    parser.add_option('-r', '--randSeed', dest='randSeed', type='int',
                      help=default(
                          'the RANDOM SEED for the entire session'),
                      metavar='RANDOM SEED', default=42)
    parser.add_option('-s', '--instSizes', dest='instSizes', help=default(
            'list of instance SIZES to generate (comma separated)'),
                      metavar='INSTANCES', default='10,25,50,100')
    parser.add_option('-p', '--parameter', dest='parameter', help=default(
            'list of parameter for instances to generate (comma separated)'),
                      metavar='parameter', default='0.25,0.05,0.5')
    parser.add_option('--prefix', dest='prefix', help=default(
            'prefix for generated instances'),
                      metavar='parameter', default='small')
    parser.add_option('-m', '--mode', dest='mode', type='int',
                      help=default(
                          '0 - create instances, 1 run rl, 2 run aspfr'),
                      metavar='MODE', default=1)
    parser.add_option('-i', '--interface', dest='interface', action='store_true',
                      help='Show the interface while evaluation',
                      default=False)
    options, files = parser.parse_args(argv)
    if (len(files) != 1 and options.mode != 0) or (options.mode == 0 and len(files) != 0):
        raise Exception('Command line input not understood: ' + str(files))

    random.seed(options.randSeed)

    args = dict()
    args['numInst'] = options.numInst
    args['instSizes'] = list(map(int, options.instSizes.split(',')))
    args['parameter'] = list(map(float, options.parameter.split(',')))
    args['mode'] = options.mode
    args['interface'] = options.interface
    args['prefix'] = options.prefix
    args['horizon'] = options.horizon
    args['radius'] = options.radius
    args['cache'] = options.cache
    return args, files


def createInstances(numInst, instSizes, parameter, prefix):
    settings = ["deterministic", "nondeterministic"]

    total = len(settings) * len(instSizes) * numInst
    count = 0
    for setting in settings:
        for instSize in instSizes:
            for i in range(numInst):
                count += 1
                instance = create_random_instance(instSize, setting, i,
                                                  parameter[0], parameter[1],
                                                  parameter[2], prefix)
                instance.save()
                printProgressBar(count, total, prefix='Progress:',
                                 suffix='Complete', )


def trainRL():
    total = len(os.listdir('instances'))
    count = 0
    for file in os.listdir('instances'):
        if os.path.isdir('instances/' + file):
            continue

        instance = read_from_file('instances/' + file)
        learning = Learning()
        learning.learn(instance)
        count += 1
        printProgressBar(count, total, prefix='Progress:',
                         suffix='Complete', )


def evaluateRL(files, show):
    instance = read_from_file(files[0])
    learning = pickle.load(
        open('instances/learning/' + instance.name + '.pkl', 'rb'))
    game = Game(instance, learning, show, False)
    game.run()
    instance.print_report('rl')

def evaluateFR(files, show, horizon, radius, cache, telingo):
    instance = read_from_file(files[0])
    learning = pickle.load(
        open('instances/learning/' + instance.name + '.pkl', 'rb'))
    game = Game(instance, learning, show, True, horizon=horizon + 1, radius=radius, cache=cache, telingo=telingo)
    game.run()
    instance.print_report('asp')




# Print iterations progress
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1,
                     length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(
        100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


if __name__ == '__main__':
    """
    The main function called when gardener.py is run
    from the command line:

    > python gardener.py

    See the usage string for more details.

    > python gardener.py --help
    """
    args, files = readCommand(sys.argv[1:])

    if args['mode'] == 0:
        createInstances(args['numInst'], args['instSizes'], args['parameter'], args['prefix'])
        trainRL()
    if args['mode'] == 1:
        evaluateRL(files, args['interface'])
    if args['mode'] == 2:
        evaluateFR(files, args['interface'], args['horizon'], args['radius'], args['cache'], False)
    if args['mode'] == 3:
        evaluateFR(files, args['interface'], args['horizon'], args['radius'], args['cache'], True)


# pyinstaller --onefile gardener.py --hidden-import=_cffi_backend
# gardener -a instance.txt learning.txt