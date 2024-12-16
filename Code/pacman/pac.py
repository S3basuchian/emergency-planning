import subprocess
import os

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
    extractors = ['SimpleExtractor', 'HungryExtractor']
    total = len(os.listdir('layouts')) * len(extractors)
    count = 0
    for file in os.listdir('layouts'):
        if os.path.isdir('layouts/' + file) or '.lay' not in file:
            continue
        for extractor in extractors:
            command = 'python pacman.py -p ApproximateQAgent -a extractor=' + extractor + ' -x 1000 -n 1000 -m 0  -f 42 -q -l ' + file
            os.system(command)
            count += 1
            printProgressBar(count, total)
    #os.system(
    #    'python pacman.py -p ApproximateQAgent -a extractor=HungryExtractor -x 10 -n 40 -l mediumClassic -f -q')
