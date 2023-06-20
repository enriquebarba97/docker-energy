import os, sys, getopt, subprocess, uuid, random, re
import parse


def execute(command: list):
    # Execute the given command
    subprocess.call(command)


def run(command: list, queue: list):
    # Current execution number in total
    total = 1

    # Monitor the selected images for the selected number of times in regular order
    for image in queue:
        # Execute the monitoring script;
        # -r is the current run for the image;
        # -t is the current run in total
        run_command = command + ["-b", image, "-r", str(total)]
        execute(run_command)
        total += 1


def help():
    print(
        "A tool for measuring energy consumption for specific workloads using different base images.\n",
        "Options:",
        '   -l --workload       Workload to monitor (e.g. -l "llama.cpp" or -l "video-stream")',
        '   -b --base           Base image to monitor; can be used for multiple base images (e.g. -b ubuntu -b alpine) (default "ubuntu")',
        "   -n --runs           Number of monitoring runs per base image (e.g. -n 30) (default 1)",
        "   -w --warmup         Warm up time (s) (e.g. -w 30) (default 10)",
        "   -p --pause          Pause time (s) (e.g. -p 60) (default 15)",
        '   -o --options        Options for the Docker run command (default "")',
        '   -c --command        Command for the Docker run command (default "")',
        "   -a --all            Monitor all compatible base images (i.e. ubuntu, debian, alpine, centos)",
        "   --shuffle           Enables shuffle mode; random order of monitoring base images",
        sep=os.linesep,
    )


def parse_args(argv):
    # Create an ID for the experiment
    exp_id = str(uuid.uuid4())

    # Set up the commands for the scripts
    prepare_command = ["bash", "prepare", "-x", exp_id]
    monitor_command = ["bash", "monitor", "-x", exp_id]

    # Default values
    workload = ""
    images = set()
    number = 1
    shuffle_mode = False
    help_mode = False
    cpus = ""

    # Get the arguments provided by the user
    opts, args = getopt.getopt(
        argv,
        "l:"  # workload
        "b:"  # base image
        "n:"  # number of runs
        "w:"  # warm up time
        "p:"  # pause time
        "o:"  # options for the Docker run command
        "c:"  # command for the Docker run command
        "a"  # all compatible base images
        "i:"  # isolate cpus
        "s"  # shuffle mode
        "h",  # help
        [
            "isolate=",
            "shuffle",
            "help",
            "all",
            "workload=",
            "base=",
            "runs=",
            "warmup=",
            "pause=",
            "options=",
            "command=",
        ],
    )
    for opt, arg in opts:
        # Set shuffle mode to true
        if opt in ["-s", "--shuffle"]:
            shuffle_mode = True
        # Add the images to the list and the preparation command
        elif opt in ["-i", "--isolate"]:
            cpus = arg
        elif opt in ["-l", "--workload"]:
            workload = arg
            opt = "-l"
            prepare_command += [opt, arg]
            monitor_command += [opt, arg]
        # Add the images to the list and the preparation command
        elif opt in ["-b", "--base"]:
            if ":" not in arg:  # If no version is specified, use the latest
                arg += ":latest"
            elif (
                arg[-1] == ":"
            ):  # If the version is specified but empty, use the latest
                arg += "latest"
            if arg not in images:
                images.add(arg)
                prepare_command += ["-b", arg]
        # Set the number of runs
        elif opt in ["-n", "--runs"]:
            number = arg
        # Set up the warm up time (s)
        elif opt in ["-w", "--warmup"]:
            opt = "-w"
            prepare_command += [opt, arg]
        # Set up the pause time (s)
        elif opt in ["-p", "--pause"]:
            opt = "-p"
            monitor_command += [opt, arg]
        # Set the options for the Docker run command
        elif opt in ["-o", "--options"]:
            opt = "-o"
            prepare_command += [opt, arg]
            monitor_command += [opt, arg]
        # Set the command for the Docker run command
        elif opt in ["-c", "--command"]:
            opt = "-c"
            prepare_command += [opt, arg]
            monitor_command += [opt, arg]
        # Set help mode to true
        elif opt in ["-h", "--help"]:
            help_mode = True
        # Add all (pre-selected) images to the image set
        elif opt in ["-a", "--all"]:
            images |= {
                "ubuntu:latest",
                "alpine:latest",
                "debian:latest",
                "centos:latest",
            }
            prepare_command += [
                "-b",
                "ubuntu:latest",
                "-b",
                "alpine:latest",
                "-b",
                "debian:latest",
                "-b",
                "centos:latest",
            ]

    # # Add the images that needs to be built to the prepare command
    # for image in images:
    #     prepare_command += ["-b", image]
    #     queue += [image] * int(number)

    # # The queue is a dictionary with the image as key and number of runs as value
    # # queue = {x: int(number) for x in images}
    # if shuffle_mode:
    #     random.shuffle(queue)

    # Put the arguments in a dictionary
    arguments = {
        "prepare_command": prepare_command,
        "monitor_command": monitor_command,
        "images": images,
        "number": number,
        "shuffle_mode": shuffle_mode,
        "help_mode": help_mode,
        "workload": workload,
        "exp_id": exp_id,
        "cpus": cpus,
    }
    return arguments


def init_queue(images, number, shuffle_mode):
    queue = list()
    for image in images:
        queue += [image] * int(number)
    if shuffle_mode:
        random.shuffle(queue)
    return queue


def set_cpus(cpus):
    isolate_cpus = list()
    background_cpus = list(range(os.cpu_count()))

    if cpus == "":
        return isolate_cpus, background_cpus

    if "-" in cpus:
        print("Specify a set of CPUs instead of a range (e.g. -i 0,1,2,3)")

    for c in re.split(",|-| ", cpus.replace(" ", "")):
        try:
            if int(c) not in background_cpus:
                print(f"CPU {c} is not available, select a core from {background_cpus}")
            isolate_cpus.append(c)
            background_cpus.remove(int(c))
        except ValueError:
            print(f"{c} is not a valid integer")

    isolate_cpus = ",".join(str(i) for i in list(isolate_cpus))
    background_cpus = ",".join(str(i) for i in list(background_cpus))

    return isolate_cpus, background_cpus


def main(argv):
    # Get the arguments from the command
    arguments = parse_args(argv)

    # If help mode is enabled, do not monitor and open the help menu
    if arguments["help_mode"]:
        help()
        return

    # If no workload is specified, do not monitor
    # if len(arguments["workload"]) == 0:
    #     print('No workload provided (e.g. -w "llama.cpp" or -w "video-stream")')
    #     return

    if len(arguments["images"]) == 0:
        print("No base images provided (e.g. -b ubuntu -b alpine)")
        return

    isolate_cpus, background_cpus = set_cpus(arguments["cpus"])

    arguments["prepare_command"] += ["-i", isolate_cpus, "-j", background_cpus]
    arguments["monitor_command"] += ["-i", isolate_cpus, "-j", background_cpus]

    queue = init_queue(
        arguments["images"], arguments["number"], arguments["shuffle_mode"]
    )

    # Initiate the preparation phase: building the images and warming up the machine
    execute(arguments["prepare_command"])

    run(arguments["monitor_command"], queue)

    # Remove the base images used in the experiment
    remove_command = arguments["prepare_command"].copy()
    remove_command[1] = "remove"
    execute(remove_command)

    # Parse the results
    # directory = f"results/{arguments['workload']}-{arguments['exp_id']}"
    # files, files_samples = parse.get_files(directory, "*.txt")
    # parse.parse_files(files, files_samples, directory)


if __name__ == "__main__":
    main(sys.argv[1:])
