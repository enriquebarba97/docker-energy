import sys, getopt, subprocess, uuid

def build(argv):
    print(argv)

def shuffle(argv):
    print(argv)

def run(command):
    subprocess.call(command)

def main(argv):
    runid = str(uuid.uuid4())
    command = ['bash', 'monitor', '-u', runid]
    # base = ""
    opts, args = getopt.getopt(argv, "b:n:i:t:a")
    for opt, arg in opts:
        command += [opt, arg]
    run(command)
    # print(command)

if __name__ == '__main__':
    # build(sys.argv[1:])
    main(sys.argv[1:])