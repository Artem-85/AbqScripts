#!/usr/bin/python
import subprocess
import sys
import time
import os
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-a', help='Number of attempts, 0 is for endless')

args = parser.parse_args()

atmax = int(args.a) if args.a else 5

# subprocess.call('pgrep -f "standard.*UMAT_plast_val_templ_UMAT_plast_validation_p1_c4" | xargs kill', shell=True)

counter = 0

timeout = 5

while True:

    if atmax > 0:

        if counter >= atmax: break

        # give it some time to start a new process in the case of i.e. parametric study
        print("Attempt {} out of {}\n".format(counter + 1,atmax))

    else:

        print("Attempt {}\n".format(counter + 1))

    time.sleep(timeout)

    process = subprocess.Popen(['pgrep', '-f', '-a','standard.*-job'], stdout=subprocess.PIPE)

    output, error = process.communicate()

    res_lines = output.splitlines()

    n = len(res_lines)

    print("Found appropriate processes: {}\n".format(n))

    if n > 0:

        counter = 0

        for i,line in enumerate(res_lines):

            print("Process #{}".format(i+1))

            words = line.split()

            pid = int((str(words[0]).strip("b")).strip("'"))

            print("PID: {}".format(pid))

            for i,word in enumerate(words):

                if '-job' in str(word):

                    j_flag = 1

                    job = (str(words[i+1]).strip("b")).strip("'")

                    print("Job name: {}".format(job))

                if '-indir' in str(word):

                    dir = (str(words[i+1]).strip("b")).strip("'")

                    d_flag = 1

                    print("Path: {}".format(dir))

            complete = False

            termination_criteria = [' THE ANALYSIS HAS COMPLETED SUCCESSFULLY\n',
                                    ' THE ANALYSIS HAS NOT BEEN COMPLETED\n']

            while complete is False:

                # wait every timeout seconds
                time.sleep(timeout)

                try:

                    with open(dir + '/' + job + '.sta', 'r') as f:

                        last = f.readlines()[-1]

                        if last in termination_criteria:

                            # this will kill any process named standard
                            os.kill(pid, 9)

                            print("Job completed and process killed\n")

                            complete = True

                except IOError:
                    
                    # model.sta has been deleted or doesn't exist
                    # try again in timeout seconds
                    time.sleep(timeout)

    else:

        counter += 1

print("No appropriate processes found\n")

    # else:

    #     break

        # continue # uncomment to have endless loop
# print("All jobs finished. Press Enter for exit")

# quit()

# sys.exit()

# subprocess = subprocess.Popen(['ps', '-A', stdout=subprocess.PIPE)