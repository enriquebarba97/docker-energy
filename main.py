import os, sys, getopt, subprocess, uuid, random


def execute(command):
    # Execute the given command
    subprocess.call(command)


def run(command, queue):
    # Monitor the selected images for the selected number of times in regular order
    for image in queue:
        for x in range(len(queue)):
            # Execute the monitoring script
            run_command = command + ["-b", image, "-r", str(x+1)]
            execute(run_command)


def shuffle(command, queue):
    number = list(queue.values())[0]+1
    # Monitor the selected images for the selected number of times in random order
    while len(queue) > 0:
        image = random.choice(list(queue.keys()))
        run_command = command + ["-b", image, "-r", str(number-queue[image])]

        # Execute the monitoring script
        execute(run_command)

        # Subtract one value of the queue value of the image
        queue[image] -= 1
        # If the queue value of the image is 0, remove it from the dictionary
        if queue[image] == 0:
            queue.pop(image, None)


def help():
    print(
        "A tool for measuring energy consumption for specific workloads using different base images.\n",
        "Options:",
        "   -b              Base image to monitor; can be used for multiple base images (e.g. -b ubuntu -b alpine) (default \"ubuntu\")",
        "   -n              Number of monitoring runs per base image (e.g. -n 30) (default 1)",
        "   -i              Change the inference input for llama.cpp (default \"Building a website can be done in 10 simple steps:\")",
        "   -t              Change the numbmer of tokens for the llama.cpp inference (default 512)",
        "   -a              Monitor all compatible base images (i.e. ubuntu, debian, alpine, centos)",
        "   -w              Workload to monitor (e.g. -w \"llama.cpp\" or -w \"video-stream\")",
        "   --shuffle       Enables shuffle mode; random order of monitoring base images",
        sep=os.linesep
    )


def parse_args(argv):
    # Create an ID for the experiment
    exp_id = str(uuid.uuid4())

    # Set up the commands for the scripts
    prepare_command = ['bash', 'prepare', '-x', exp_id]
    monitor_command = ['bash', 'monitor', '-x', exp_id]

    workload = ""
    images = set()
    number = 1
    shuffle_mode = False
    help_mode = False

    # Get the arguments provided by the user
    opts, args = getopt.getopt(argv, "b:n:i:t:ahw:", ["shuffle", "help"])
    for opt, arg in opts:
        # Set shuffle mode to true
        if opt == "--shuffle":
            shuffle_mode = True
        # Add the images to the list and the preparation command
        elif opt == "-w":
            workload = arg
            prepare_command += [opt, arg]
            monitor_command += [opt, arg]
        # Add the images to the list and the preparation command
        elif opt == "-b":
            images.add(arg)
            # prepare_command += [opt, arg]
        elif opt == "-a":
            images |= {"ubuntu", "alpine", "debian", "centos"}
        # Set the number of runs
        elif opt == "-n":
            number = arg
        # Add the additional arguments to the monitoring command
        elif opt in ["-i", "-t"]:
            monitor_command += [opt, arg]
        elif opt in ["-h", "--help"]:
            help_mode = True
    
    for image in images:
        prepare_command += ["-b", image]

    # The queue is a dictionary with the image as key and number of runs as value
    queue = {x: int(number) for x in images}
    return prepare_command, monitor_command, queue, shuffle_mode, help_mode, workload


def main(argv):
    prepare_command, monitor_command, queue, shuffle_mode, help_mode, workload = parse_args(argv)

    if help_mode:
        help()
        return

    if len(workload) == 0:
        print("No workload provided (e.g. -w \"llama.cpp\" or -w \"video-stream\")")
        return
    
    # Initiate the preparation phase: building the images and warming up the machine
    execute(prepare_command)

    # If shuffle mode is set to true, monitor in random order
    if shuffle_mode:
        shuffle(monitor_command, queue)
    # Monitor in regular order
    else:
        run(monitor_command, queue)

    # Remove the base images used in the experiment
    remove_command = prepare_command.copy()
    print(remove_command)
    remove_command[1] = "remove"
    execute(remove_command)


if __name__ == '__main__':
    main(sys.argv[1:])