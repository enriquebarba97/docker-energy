import os, sys, getopt, subprocess, uuid, random, re, time, math
import yaml
import parse
import psutil
from datetime import datetime


class Workload:
    def __init__(
        self,
        exp_id: str,
        name: str,
        images: set,
        queue: list,
        isolate_cpus: str,
        background_cpus: str,
        threads: int,
        warmup: int,
        pause: int,
        interval: int,
        clients: int,
        monitor: str,
    ):
        self.exp_id = exp_id
        self.name = name
        self.images = images
        self.queue = queue
        self.isolate_cpus = isolate_cpus
        self.background_cpus = background_cpus
        self.threads = threads
        self.warmup = warmup
        self.pause = pause
        self.interval = interval
        self.clients = clients
        self.monitor = monitor

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
            "-t",
            str(self.threads),
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
            "-t",
            str(self.threads),
            "-p",
            str(self.pause),
            "-v",
            str(self.interval),
            "-m",
            self.monitor,
        ]

        if self.clients > 0:
            command += ["-s", str(self.clients)]

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
        "   -l --workload       Workload to monitor; can be used to for multiple workloads (e.g. -l llama.cpp -l mattermost)",
        '   -b --base           Base image to monitor; can be used for multiple base images (e.g. -b ubuntu -b alpine) (default "ubuntu")',
        "   -n --runs           Number of monitoring runs per base image (e.g. -n 30) (default 1)",
        "   -w --warmup         Warm up time (s) (e.g. -w 30) (default 10)",
        "   -p --pause          Pause time (s) (e.g. -p 60) (default 15)",
        "   -i --interval       Interval of monitoring (ms) (e.g. -i 100) (default 100)",
        '   -m --monitor        Monitoring tool (e.g. -m "perf") (default "greenserver")',
        # '   -o --options        Options for the Docker run command (default "")',
        # '   -c --command        Command for the Docker run command (default "")',
        "   --all-images        Monitor all compatible base images (i.e. ubuntu, debian, alpine, centos)",
        "   --all-workloads     Monitor all compatible workloads (i.e. llama.cpp, nginx-vod-module-docker, cypress-realworld-app, mattermost)",
        "   --full              Monitor all compatible workloads using all compatible base images",
        "   --no-shuffle        Disables shuffle mode; regular order of monitoring base images",
        "   --cpus              Number of CPUs to isolate; will use threads on the same physical core (e.g. --cpus 2)",
        "   --cpuset            CPUs to isolate (e.g. --cpuset 0-1)",
        sep=os.linesep,
    )


def parse_args(argv):
    # Default values
    workloads = set()
    images = set()
    number = 30
    warmup = 15
    pause = 15
    interval = 100
    monitor = ""
    shuffle_mode = True
    help_mode = False
    cpus = 0
    cpuset = ""
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
        "i:"  # interval of monitoring
        "m:"  # monitoring tool
        "o:"  # options for the Docker run command
        "c:"  # command for the Docker run command
        "s"  # shuffle mode
        "h",  # help
        [
            "cpus=",
            "cpuset=",
            "no-shuffle",
            "help",
            "all-images",
            "all-workloads",
            "full",
            "workload=",
            "base=",
            "runs=",
            "warmup=",
            "pause=",
            "interval=",
            "monitor=",
            "options=",
            "command=",
        ],
    )
    for opt, arg in opts:
        # Set shuffle mode to false
        if opt in ["-s", "--no-shuffle"]:
            shuffle_mode = False
        # Add the images to the list and the preparation command
        elif opt == "--cpus":
            try:
                cpus = int(arg)
            except ValueError:
                print("Number of CPUs must be an integer")
        elif opt == "--cpuset":
            cpuset = arg
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
        elif opt in ["-i", "--interval"]:
            try:
                interval = int(arg)
            except ValueError:
                print("Pause time must be an integer")
        # Set the monitoring tool
        elif opt in ["-m", "--monitor"]:
            monitor = arg
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
        "cpuset": cpuset,
        "warmup": warmup,
        "pause": pause,
        "interval": interval,
        "monitor": monitor,
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
    # Get the number of physical and logical CPUs
    physical_cpus = psutil.cpu_count(logical=False)
    logical_cpus = psutil.cpu_count()

    # Allocate the logical CPUs to the physical CPUs
    dict_cpus = {x: [] for x in range(physical_cpus)}
    core = 0
    for x in range(logical_cpus):
        dict_cpus[core].append(x)
        core += 1
        if core >= physical_cpus:
            core = 0

    # Isolate the amount of threads on the same physical CPU
    cpuset = list()
    reserve = list()
    threads = logical_cpus / physical_cpus
    for x in range(math.ceil(cpus / threads)):
        cpuset.extend(dict_cpus[x])

    # Reserve the remaining threads on a physical CPU
    for x in range(len(cpuset) - cpus):
        reserve.append(cpuset.pop())

    # Convert the list to a string
    cpuset = ",".join([str(x) for x in cpuset])
    return cpuset, reserve


def set_cpuset(cpuset, reserve=[]):
    isolate_cpus = set()
    background_cpus = set(range(psutil.cpu_count()))

    # Remove the reserved CPUs from the available CPUs
    for x in reserve:
        background_cpus.remove(x)

    # If no cpuset is specified, use all available CPUs
    if cpuset == "":
        isolate_cpus = ",".join(str(i) for i in list(background_cpus))
        background_cpus = ",".join(str(i) for i in list(background_cpus))
        threads = len(isolate_cpus)
        return isolate_cpus, background_cpus, threads

    # If a cpuset is specified, isolate the specified CPUs
    total_cpus = set(range(psutil.cpu_count()))
    cpuset = cpuset.replace(" ", "").split(",")
    for cpu in cpuset:
        # If a range is specified, isolate the range
        if "-" in cpu:
            cpu_range = re.split("-", cpu)
            try:
                # If the range is valid, isolate the range
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
                # If the CPU is valid, isolate the CPU
                if int(cpu) in total_cpus:
                    isolate_cpus.add(int(cpu))
                    background_cpus.remove(int(cpu))
            except:
                print("Invalid CPU")

    # If no CPUs are isolated or all CPUs are isolated, use all available CPUs
    if len(background_cpus) == 0 or len(isolate_cpus) == 0:
        isolate_cpus = set(range(psutil.cpu_count()))
        background_cpus = set(range(psutil.cpu_count()))

    # Convert the sets to strings
    threads = len(isolate_cpus)
    isolate_cpus = ",".join(str(i) for i in list(isolate_cpus))
    background_cpus = ",".join(str(i) for i in list(background_cpus))

    return isolate_cpus, background_cpus, threads


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

    date = datetime.now().strftime("%Y%m%dT%H%M%S")

    # If no workload is specified, do not monitor
    if len(arguments["workloads"]) == 0 and not arguments["all_workloads"]:
        print("No workload provided, all workloads will be used")
        arguments["all_workloads"] = True

    if len(arguments["images"]) == 0 and not arguments["all_images"]:
        print("No base images provided, all images will be used")
        arguments["all_images"] = True

    workloads = get_workloads("workloads")

    if not arguments["all_workloads"]:
        workloads = set(workloads).intersection(arguments["workloads"])

    for workload in workloads:
        config = get_workload_config(workload)

        # Skip development workloads
        if "development" in config.keys() and config["development"]:
            continue

        # First set the cpuset
        if arguments["cpuset"] != "":
            cpuset = arguments["cpuset"]
            reserve = []
        # If no cpuset is provided, use the number of cpus
        elif arguments["cpus"] != 0:
            cpuset, reserve = set_cpus(arguments["cpus"])
        # If no cpus are provided, use the cpus from the config
        elif "cpus" in config.keys() and type(config["cpus"]) is int:
            cpuset, reserve = set_cpus(config["cpus"])
        # If no cpus are provided in the config, use all cpus
        else:
            cpuset = ""
            reserve = []

        isolate_cpus, background_cpus, threads = set_cpuset(cpuset, reserve)

        # Use all images if all_images is enabled, otherwise use the provided images (if they exist)
        images = set(config["images"]) if "images" in config.keys() else set()

        if not arguments["all_images"]:
            images = images.intersection(arguments["images"])

        if len(images) == 0:
            print(f"No correct images provided for workload {workload}")
            continue

        if "clients" in config.keys() and type(config["clients"]) is int:
            clients = abs(config["clients"])
        else:
            clients = 0

        # Create the queue of images for the workload
        queue = init_queue(images, arguments["number"], arguments["shuffle_mode"])

        # Create the workload
        current_workload = Workload(
            date,
            workload,
            images,
            queue,
            isolate_cpus,
            background_cpus,
            threads,
            arguments["warmup"],
            arguments["pause"],
            arguments["interval"],
            clients,
            arguments["monitor"],
        )

        # Run the workload
        current_workload.prepare()
        current_workload.run()
        # current_workload.remove()
        time.sleep(15)

    # Parse the results
    # directory = f"results/{arguments['workload']}-{arguments['exp_id']}"
    # files, files_samples = parse.get_files(directory, "*.txt")
    # parse.parse_files(files, files_samples, directory)


if __name__ == "__main__":
    main(sys.argv[1:])
