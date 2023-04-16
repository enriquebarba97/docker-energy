import sys, getopt, subprocess, uuid

def build(argv):
    print(argv)

def main(argv):
    runid = str(uuid.uuid4())
    command = ['bash', 'monitor', '-u', runid]
    # base = ""
    opts, args = getopt.getopt(argv, "b:n:i:t:")
    for opt, arg in opts:
        command += [opt, arg]
    subprocess.call(command)

if __name__ == '__main__':
    # build(sys.argv[1:])
    main(sys.argv[1:])