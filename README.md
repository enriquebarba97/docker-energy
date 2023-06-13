# docker-energy

Measuring the impact of the base image choice for different workloads inside Docker containers

-   [docker-energy](#docker-energy)
    -   [Setup](#setup)
        -   [Prerequisites](#prerequisites)
        -   [Installing the dependencies](#installing-the-dependencies)
    -   [Usage](#usage)
        -   [Measuring the energy consumption](#measuring-the-energy-consumption)
        -   [Statistical analysis](#statistical-analysis)

## Setup

### Prerequisites

-   Ubuntu (or a similar Linux distribution)
-   Docker engine
-   Python 3

### Installing the dependencies

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

Pull the submodules and install the packages

```bash
git submodule update --init

< packages.txt xargs apt-get -y install

apt-get -y install linux-tools-`uname -r`
```

Set up node for the web application workloads

```bash
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
nvm install 16
nvm use 16
npm install yarn -g

yarn --cwd "${PWD}"/cypress-realworld-app install

npm install --prefix "${PWD}"/mattermost/e2e-tests/cypress/
```

Install Python packages

```bash
python -m venv venv

venv/bin/pip install -r requirements.txt
```

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
