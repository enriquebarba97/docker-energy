import os, sys, getopt, subprocess, uuid, random, re, time
import yaml
import parse


class Workload:
    def __init__(
        self,
        name: str,
        images: set,
        queue: list,
        isolate_cpus: str,
        background_cpus: str,
        warmup: int,
        pause: int,
    ):
        self.exp_id = str(uuid.uuid4())
        self.name = name
        self.images = images
        self.queue = queue
        self.isolate_cpus = isolate_cpus
        self.background_cpus = background_cpus
        self.warmup = warmup
        self.pause = pause

    def prepare(self):
        # Execute the given command
        command = [
            "bash",
            "prepare",
            "-x",
            self.exp_id,
            "-l",
            self.name,
            "-i",
            self.isolate_cpus,
            "-j",
            self.background_cpus,
            "-w",
            str(self.warmup),
        ]
        for image in self.images:
            command += ["-b", image]
        subprocess.call(command)

    def run(self):
        # Current execution number in total
        total = 1

        command = [
            "bash",
            "monitor",
            "-x",
            self.exp_id,
            "-l",
            self.name,
            "-i",
            self.isolate_cpus,
            "-j",
            self.background_cpus,
            "-p",
            str(self.pause),
        ]

        # Monitor the selected images for the selected number of times in regular order
        for image in self.queue:
            # Execute the monitoring script;
            # -r is the current run for the image;
            # -t is the current run in total
            run_command = command + ["-b", image, "-r", str(total)]
            subprocess.call(run_command)
            total += 1

    def remove(self):
        command = ["bash", "remove", "-x", self.exp_id, "-l", self.name]
        for image in self.images:
            command += ["-b", image]
        subprocess.call(command)


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
        "   --all-images        Monitor all compatible base images (i.e. ubuntu, debian, alpine, centos)",
        "   --all-workloads     Monitor all compatible workloads (i.e. llama.cpp, nginx-vod-module-docker, cypress-realworld-app, mattermost)",
        "   --shuffle           Enables shuffle mode; random order of monitoring base images",
        sep=os.linesep,
    )


def parse_args(argv):
    # Default values
    workloads = set()
    images = set()
    number = 1
    warmup = 10
    pause = 15
    shuffle_mode = False
    help_mode = False
    cpus = ""
    all_images = False
    all_workloads = False

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
        "i:"  # isolate cpus
        "s"  # shuffle mode
        "h",  # help
        [
            "isolate=",
            "shuffle",
            "help",
            "all-images",
            "all-workloads",
            "full",
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
            workloads.add(arg)
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
        # Set the number of runs
        elif opt in ["-n", "--runs"]:
            number = arg
        # Set up the warm up time (s)
        elif opt in ["-w", "--warmup"]:
            try:
                warmup = int(arg)
            except ValueError:
                print("Warm up time must be an integer")
        # Set up the pause time (s)
        elif opt in ["-p", "--pause"]:
            try:
                pause = int(arg)
            except ValueError:
                print("Pause time must be an integer")
        # Set the options for the Docker run command
        elif opt in ["-o", "--options"]:
            opt = "-o"
        # Set the command for the Docker run command
        elif opt in ["-c", "--command"]:
            opt = "-c"
        # Set help mode to true
        elif opt in ["-h", "--help"]:
            help_mode = True
        # Add all (pre-selected) images to the image set
        elif opt == "--all-images":
            all_images = True
        elif opt == "--all-workloads":
            # workloads |= set(get_workloads("workloads"))
            all_workloads = True
        elif opt == "--full":
            all_images = True
            all_workloads = True

    # Put the arguments in a dictionary
    arguments = {
        "images": images,
        "number": number,
        "shuffle_mode": shuffle_mode,
        "help_mode": help_mode,
        "workloads": workloads,
        "cpus": cpus,
        "warmup": warmup,
        "pause": pause,
        "all_images": all_images,
        "all_workloads": all_workloads,
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
    isolate_cpus = set()
    background_cpus = set(range(os.cpu_count()))

    if cpus == "":
        isolate_cpus = ",".join(str(i) for i in list(background_cpus))
        background_cpus = ",".join(str(i) for i in list(background_cpus))
        return isolate_cpus, background_cpus

    total_cpus = set(range(os.cpu_count()))
    cpus = cpus.replace(" ", "").split(",")
    for cpu in cpus:
        if "-" in cpu:
            cpu_range = re.split("-", cpu)
            try:
                if int(cpu_range[0]) in total_cpus and int(cpu_range[-1]) in total_cpus:
                    isolate_cpus |= set(
                        range(int(cpu_range[0]), int(cpu_range[-1]) + 1)
                    )
                    background_cpus -= set(
                        range(int(cpu_range[0]), int(cpu_range[-1]) + 1)
                    )
            except ValueError:
                print("Invalid CPU range")
        else:
            try:
                if int(cpu) in total_cpus:
                    isolate_cpus.add(int(cpu))
                    background_cpus.remove(int(cpu))
            except ValueError:
                print("Invalid CPU")

    isolate_cpus = ",".join(str(i) for i in list(isolate_cpus))
    background_cpus = ",".join(str(i) for i in list(background_cpus))

    return isolate_cpus, background_cpus


def get_workloads(directory: str):
    try:
        return [
            workload
            for workload in os.listdir(directory)
            if os.path.isdir(f"{directory}/{workload}")
        ]
    except FileNotFoundError:
        print(f"Directory {directory} not found")
        return []


def get_workload_config(workload: str):
    with open(f"workloads/{workload}/config.yml", "r") as file:
        config = yaml.safe_load(file)
    return config


def main(argv):
    # Get the arguments from the command
    arguments = parse_args(argv)

    # If help mode is enabled, do not monitor and open the help menu
    if arguments["help_mode"]:
        help()
        return

    # If no workload is specified, do not monitor
    if len(arguments["workloads"]) == 0 and not arguments["all_workloads"]:
        print("No workload provided, all workloads will be used")
        arguments["all_workloads"] = True

    if len(arguments["images"]) == 0 and not arguments["all_images"]:
        print("No base images provided, all images will be used")
        arguments["all_images"] = True

    isolate_cpus, background_cpus = set_cpus(arguments["cpus"])

    workloads = get_workloads("workloads")

    if not arguments["all_workloads"]:
        workloads = set(workloads).intersection(arguments["workloads"])

    for workload in workloads:
        config = get_workload_config(workload)

        # Skip development workloads
        if config["development"]:
            continue

        # Use all images if all_images is enabled, otherwise use the provided images (if they exist)
        images = (
            config["images"]
            if arguments["all_images"]
            else set(config["images"]).intersection(arguments["images"])
        )

        # Create the queue of images for the workload
        queue = init_queue(images, arguments["number"], arguments["shuffle_mode"])

        # Create the workload
        current_workload = Workload(
            workload,
            images,
            queue,
            isolate_cpus,
            background_cpus,
            arguments["warmup"],
            arguments["pause"],
        )

        # Run the workload
        current_workload.prepare()
        current_workload.run()
        current_workload.remove()
        time.sleep(15)

    # Parse the results
    # directory = f"results/{arguments['workload']}-{arguments['exp_id']}"
    # files, files_samples = parse.get_files(directory, "*.txt")
    # parse.parse_files(files, files_samples, directory)


if __name__ == "__main__":
    main(sys.argv[1:])
