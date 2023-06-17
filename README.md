# docker-energy

Measuring the impact of the base image choice for different workloads inside Docker containers

-   [docker-energy](#docker-energy)
    -   [Setup](#setup)
        -   [Prerequisites](#prerequisites)
        -   [Installing the dependencies](#installing-the-dependencies)
    -   [Usage](#usage)
        -   [Measuring the energy consumption](#measuring-the-energy-consumption)
        -   [Statistical analysis](#statistical-analysis)
    -   [Workloads](#workloads)
        -   [llama.cpp](#llamacpp)
        -   [nginx-vod-module-docker](#nginx-vod-module-docker)
        -   [cypress-realworld-app](#cypress-realworld-app)
        -   [mattermost](#mattermost)

## Setup

### Prerequisites

-   Ubuntu (or a similar Linux distribution)
-   Docker engine
-   Python 3

### Installing the dependencies

To use perf run the following commands:

```bash
# install perf
sudo apt-get -y install linux-tools-common linux-tools-generic linux-tools-`uname -r`

# allow perf to be used by non-root users
sudo sh -c 'echo -1 >/proc/sys/kernel/perf_event_paranoid'
sudo sysctl -w kernel.perf_event_paranoid=-1
```

Install the Python packages to use the monitoring pipeline:

```bash
python -m venv venv

venv/bin/pip install -r requirements.txt
```

To use the predefined workloads, pull the submodules with the corresponding commit:

```bash
# Pull all submodules
git submodule update --init

# Pull a specific submodule
git submodule update --init <name of submodule>
```

For the workload specific dependencies, see [Workloads](#workloads).

<details>
  <summary>Install all dependencies using the setup script</summary>

To install the necessary dependencies, use the `setup` script by running the following command:

```bash
sudo bash setup
```

This `setup` script installs the following dependencies:

-   The following git submodules:
    -   [llama.cpp](https://github.com/ggerganov/llama.cpp)
    -   [nginx-vod-module-docker](https://github.com/nytimes/nginx-vod-module-docker)
    -   [cypress-realworld-app](https://github.com/cypress-io/cypress-realworld-app)
-   The following Linux packages:
    -   linux-tools-common
    -   linux-tools-generic
    -   vlc
    -   python3.10-venv
-   nvm, node v16, and yarn
-   The following Python packages:
    -   matplotlib
    -   numpy
    -   pandas
    -   scipy
    -   statsmodels
    -   seaborn
    -   PyQt5

</details>

## Usage

### Measuring the energy consumption

The `measure.py` script is used to measure the energy consumption of Docker containers for the various workloads using different base images.
It takes the following arguments:

-   **_-l_** or **_--workload_**: Workload to monitor (e.g. -l "llama.cpp" or -l "video-stream")
-   **_-b_** or **_--base_**: Base image to monitor; can be used for multiple base images (e.g. -b ubuntu -b alpine) (default "ubuntu")
-   **_-n_** or **_--runs_**: Number of monitoring runs per base image (e.g. -n 30) (default 1)
-   **_-w_** or **_--warmup_**: Warm up time (s) (e.g. -w 30) (default 10)
-   **_-p_** or **_--pause_**: Pause time (s) (e.g. -p 60) (default 15)
-   **_-o_** or **_--options_**: Options for the Docker run command (default "")
-   **_-c_** or **_--command_**: Command for the Docker run command (default "")
-   **_-a_** or **_--all_**: Monitor all compatible base images (i.e. ubuntu, debian, alpine, centos)
-   **_--shuffle_**: Enables shuffle mode; random order of monitoring base images

For example, to obtain 30 energy consumption measurements and power samples of the _llama.cpp_ using _ubuntu_, _debian_, and _alpine_, in shuffle mode, run the following command:

```bash
sudo venv/bin/python measure.py -l llama.cpp -b ubuntu -b debian -b alpine -n 30 --shuffle
```

This command will output the logs of the warm-up and the workload for each image in `logs/llama.cpp-{uuid}`.

The energy consumption measurements for each image can be found in `results/llama.cpp-{uuid}`, and the samples in `results/llama.cpp-{uuid}/samples`.

**NOTE:** It is important to run the script with _sudo_, since reading power statistics from RAPL domains require root privileges.

### Statistical analysis

When the measurements are obtained, it is possible to determine the statistical significance of the results using the `analyze.py` script. This script takes the following arguments:

-   **_-f_** or **_--file_**: the input file(s)
-   **_-d_** or _**--directory**_: the directory containing the input file(s)
-   **_--shapiro_**: perform the Shapiro-Wilk test for normality for each part of each base image
-   **_--anova_**: perform the one-way ANOVA test for each part between the base images
-   **_--tukey_**: perform the Tukey HSD test for each part between the base images
-   **_--cohen_**: perform the Cohen's d test for each part between the base images
-   **_--plot_**: plot the data for each part
-   **_--full_**: perform all tests and plot the data
-   **_--plot_samples_**: plot the power samples over time
-   **_--statistics_**: print the mean and standard deviation for each part of each base image

For example, to perform all tests for all measurements, run the following commands, respectively:

```bash
python analyze.py -d results/llama.cpp-{uuid} --full
```

The Shapiro-Wilk test will print _False_ if the data is normal, and _True_ if it is not.
The ANOVA test will print _True_ if the means are significantly different, and _False_ if they are not.
The Tukey test will print the actual differences between the datasets.
The Cohen's d test will print the effect size between the datasets.

## Workloads

### llama.cpp

For the _llama.cpp_ workload it is important that the quantized model is in `llama.cpp/models`. If you already have the model, and moved it to `llama.cpp/models`, it is possible to quantize it using the following steps (_taken from the llama.cpp README_):

```bash
# obtain the original LLaMA model weights and place them in ./models
ls ./models
65B 30B 13B 7B tokenizer_checklist.chk tokenizer.model

# install Python dependencies
python3 -m pip install -r requirements.txt

# convert the 7B model to ggml FP16 format
python3 convert.py models/7B/

# quantize the model to 4-bits (using q4_0 method)
./quantize ./models/7B/ggml-model-f16.bin ./models/7B/ggml-model-q4_0.bin q4_0
```

### nginx-vod-module-docker

At the moment, the _nginx-vod-module-docker_ workload requires VLC to be installed on the host machine, in order to stream the video files:

```bash
sudo apt-get -y install vlc
```

### cypress-realworld-app

The _cypress-realworld-app_ requires node 16, yarn and the project dependencies to be installed on the host machine, in order to run the cypress tests:

```bash
# install nvm and node 16
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
nvm install 16
nvm use 16

# install yarn
npm install yarn -g

# install the project dependencies
yarn --cwd "${PWD}"/cypress-realworld-app install
```

### mattermost

Similar to the other web application workload, it is recommended to also use node 16 for the _mattermost_ workload. The project dependencies can be installed using the following command:

```bash
npm install --prefix "${PWD}"/mattermost/e2e-tests/cypress/
```
