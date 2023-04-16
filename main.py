import sys, getopt, subprocess, uuid, random



def prepare(command):
    # Initiate the preparation phase: building the images and warming up the machine
    # print(command)
    subprocess.call(command)

def run(command, queue):
    # Monitor the selected images for the selected number of times in regular order
    for image in queue:
        for x in range(len(queue)):
            # Execute the monitoring script
            run_command = command + ["-b", image, "-r", str(x+1)]
            # print(run_command)
            subprocess.call(run_command)

def shuffle_mode(command, queue):
    number = list(queue.values())[0]+1
    # Monitor the selected images for the selected number of times in random order
    while len(queue) > 0:
        image = random.choice(list(queue.keys()))
        run_command = command + ["-b", image, "-r", str(number-queue[image])]

        # Execute the monitoring script
        # print(run_command)
        subprocess.call(run_command)

        # Subtract one value of the queue value of the image
        queue[image] -= 1
        # If the queue value of the image is 0, remove it from the dictionary
        if queue[image] == 0:
            queue.pop(image, None)

def parse_args(argv):
    # Create an ID for the experiment
    exp_id = str(uuid.uuid4())

    # Setup the commands for the scripts
    prepare_command = ['bash', 'prepare', '-x', exp_id]
    monitor_command = ['bash', 'monitor', '-x', exp_id]

    images = []
    number = 1
    shuffle = False

    # Get the arguments provided by the user
    opts, args = getopt.getopt(argv, "b:n:i:t:a", ["shuffle"])
    for opt, arg in opts:
        # Set shuffle mode to true
        if opt == "--shuffle":
            shuffle = True
        # Add the images to the list and the preparation command
        elif opt == "-b":
            images.append(arg)
            prepare_command += [opt, arg]
        # Set the number of runs
        elif opt == "-n":
            number = arg
        # Add the additional arguments to the monitoring command
        elif opt in ["-i", "-t", "-a"]:
            monitor_command += [opt, arg]
    
    # The queue is a dictionary with the image as key and number of runs as value
    queue = {x: int(number) for x in images}
    return prepare_command, monitor_command, queue, shuffle

def main(argv):
    prepare_command, monitor_command, queue, shuffle = parse_args(argv)

    # Start the preparation phase
    prepare(prepare_command)

    # If shuffle mode is set to true, monitor in random order
    if shuffle:
        shuffle_mode(monitor_command, queue)
    # Monitor in regular order
    else:
        run(monitor_command, queue)

if __name__ == '__main__':
    # build(sys.argv[1:])
    main(sys.argv[1:])