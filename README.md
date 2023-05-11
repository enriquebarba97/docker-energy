# docker-energy
Measuring the impact of the base image choice for different workloads inside Docker containers

## Measuring the energy consumption of Docker containers
The _main.py_ script is used to measure the energy consumption of Docker containers for the various workloads using different base images.
It takes the following arguments:
- _-l_: the workload to measure (e.g. _-l llama.cpp_)
- _-b_: the base image to use (e.g. _-b ubuntu_)
- _-n_: the number of iterations to run (default: 30)
- _-w_: the warm-up time in seconds (default: 10)
- _-p_: the pause time between the iterations in seconds (default: 10)
- _-o_: the options for the Docker command
- _-c_: the command for the Docker command
- _--shuffle_: enables shuffle mode, which shuffles the order of the base image iterations

For example, to obtain 30 energy consumption measurements of the _llama.cpp_ using _ubuntu_, _debian_, and _alpine_, in shuffle mode, run the following command:
```bash
python measure.py -l llama.cpp -b ubuntu -b debian -b alpine -n 30 --shuffle
```

This command will output the logs of the warm up and of the workload for each image in the _logs_ folder, and the energy consumption measurements for each image in the _results_ folder.

## Determining the statistical significance of the results
When the measurements are obtained, it is possible to determine the statistical significance of the results using the _statistical_tests.py_ script.
This script expects a tsv file in the following format:
```tsv
image
part1   part2    part3   ...
x1      y1       z1      ...
x2      y2       z2      ...
x3      y3       z3      ...
...     ...      ...     ...
```
where _part1_, _part2_, _part3_, ... are the different part measurements (such as cores, gpu, and ram), and _x_, _y_, and _z_ are the energy consumption measurements for parts. The first line indicates the base image of the measurements.

<details>
  <summary>Reformat perf_events output for the tests</summary>

  In order to use the _statistical_tests.py_ script, the output of the perf_events script needs to be reformatted. This can be done using the following command:
  ```bash
    python parse.py -f input_file.txt
  ```

</details>

The _statistical_tests.py_ script takes the following arguments:
- _-f_: the input file(s)
- _--shapiro_: perform the Shapiro-Wilk test for normality for each part of each base image
- _--anova_: perform the one-way ANOVA test for each part between the base images
- _--tukey_: perform the Tukey HSD test for each part between the base images

For example, to perform the Shapiro-Wilk, ANOVA, and Tukey test for each part of each base image, run the following commands, respectively:
```bash
python analyze.py -f llama.cpp_ubuntu.csv -f llama.cpp_debian.csv -f llama.cpp_alpine.csv --shapiro
python analyze.py -f llama.cpp_ubuntu.csv -f llama.cpp_debian.csv -f llama.cpp_alpine.csv --anova
python analyze.py -f llama.cpp_ubuntu.csv -f llama.cpp_debian.csv -f llama.cpp_alpine.csv --tukey
```

The Shapiro-Wilk test will print _True_ if the data is normal, and _False_ if it is not.
The ANOVA test will print _True_ if the means are not significantly different, and _False_ if they are.
The Tukey test will print the actual differences between the datasets.

## Misc
In order to run the perf_events script, the following commands need to be run:
```
sudo sh -c 'echo -1 >/proc/sys/kernel/perf_event_paranoid'
sudo sysctl -w kernel.perf_event_paranoid=-1
```