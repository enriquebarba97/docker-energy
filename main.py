import os, sys, getopt, subprocess, uuid, random


def execute(command):
    # Execute the given command
    subprocess.call(command)


def run(command, queue):
    # Number of runs per image
    number = list(queue.values())[0]+1
    # Current execution number in total
    total = 1

    # Monitor the selected images for the selected number of times in regular order
    for image in queue:
        while queue[image] > 0:
            # Execute the monitoring script;
            # -r is the current run for the image;
            # -t is the current run in total
            run_command = command + ["-b", image, "-r", str(number-queue[image]), "-t", str(total)]
            execute(run_command)

            # Subtract one value of the queue value of the image
            queue[image] -= 1
            total += 1


def shuffle(command, queue):
    # Number of runs per image
    number = list(queue.values())[0]+1
    # Current execution number in total
    total = 1

    # Monitor the selected images for the selected number of times in random order
    while len(queue) > 0:
        image = random.choice(list(queue.keys()))

        # Execute the monitoring script;
        # -r is the current run for the image;
        # -t is the current run in total
        run_command = command + ["-b", image, "-r", str(number-queue[image]), "-t", str(total)]
        execute(run_command)

        # Subtract one value of the queue value of the image
        queue[image] -= 1
        total += 1

        # If the queue value of the image is 0, remove it from the dictionary
        if queue[image] == 0:
            queue.pop(image, None)


def help():
    print(
        "A tool for measuring energy consumption for specific workloads using different base images.\n",
        "Options:",
        "   -l              Workload to monitor (e.g. -l \"llama.cpp\" or -l \"video-stream\")",
        "   -b              Base image to monitor; can be used for multiple base images (e.g. -b ubuntu -b alpine) (default \"ubuntu\")",
        "   -n              Number of monitoring runs per base image (e.g. -n 30) (default 1)",
        "   -w              Warm up time (s) (default 10)",
        "   -p              Pause time (s) (default 10)",
        "   -i              Change the inference input for llama.cpp (default \"Building a website can be done in 10 simple steps:\")",
        "   -o              Options for the Docker run command (default \"\")",
        "   -c              Command for the Docker run command (default \"\")",
        "   -a              Monitor all compatible base images (i.e. ubuntu, debian, alpine, centos)",
        "   --shuffle       Enables shuffle mode; random order of monitoring base images",
        sep=os.linesep
    )


def parse_args(argv):
    # Create an ID for the experiment
    exp_id = str(uuid.uuid4())

    # Set up the commands for the scripts
    prepare_command = ['bash', 'prepare', '-x', exp_id]
    monitor_command = ['bash', 'monitor']

    # Default values
    workload = ""
    images = set()
    number = 1
    shuffle_mode = False
    help_mode = False

    # Get the arguments provided by the user
    opts, args = getopt.getopt(argv, "l:b:n:w:p:i:o:c:ah", ["shuffle", "help"])
    for opt, arg in opts:
        # Set shuffle mode to true
        if opt == "--shuffle":
            shuffle_mode = True
        # Add the images to the list and the preparation command
        elif opt == "-l":
            workload = arg
            prepare_command += [opt, arg]
            monitor_command += [opt, arg]
        # Add the images to the list and the preparation command
        elif opt == "-b":
            images.add(arg)
        # Set the number of runs
        elif opt == "-n":
            number = arg
        # Set up the warm up time (s)
        elif opt == "-w":
            prepare_command += [opt, arg]
        # Set up the pause time (s)
        elif opt == "-p":
            monitor_command += [opt, arg]
        # Add the additional arguments to the monitoring command
        # -i is the inference input for llama.cpp;
        # -o are the options for the Docker run command;
        # -c is the command for the Docker run command;
        elif opt in ["-i", "-o", "-c"]:
            monitor_command += [opt, arg]
        # Set help mode to true
        elif opt in ["-h", "--help"]:
            help_mode = True
        # Add all (pre-selected) images to the image set
        elif opt == "-a":
            images |= {"ubuntu", "alpine", "debian"}

    # Add the images that needs to be built to the prepare command
    for image in images:
        prepare_command += ["-b", image]

    # The queue is a dictionary with the image as key and number of runs as value
    queue = {x: int(number) for x in images}

    # Put the arguments in a dictionary
    arguments = {"prepare_command": prepare_command, "monitor_command": monitor_command, "queue": queue,
                 "shuffle_mode": shuffle_mode, "help_mode": help_mode, "workload": workload}
    return arguments


def main(argv):
    # Get the arguments from the command
    arguments = parse_args(argv)

    # If help mode is enabled, do not monitor and open the help menu
    if arguments["help_mode"]:
        help()
        return

    # If no workload is specified, do not monitor
    if len(arguments["workload"]) == 0:
        print("No workload provided (e.g. -w \"llama.cpp\" or -w \"video-stream\")")
        return
    
    # Initiate the preparation phase: building the images and warming up the machine
    execute(arguments["prepare_command"])

    # If shuffle mode is set to true, monitor in random order
    if arguments["shuffle_mode"]:
        shuffle(arguments["monitor_command"], arguments["queue"])
    # Monitor in regular order
    else:
        run(arguments["monitor_command"], arguments["queue"])

    # Remove the base images used in the experiment
    remove_command = arguments["prepare_command"].copy()
    remove_command[1] = "remove"
    execute(remove_command)


if __name__ == '__main__':
    main(sys.argv[1:])
