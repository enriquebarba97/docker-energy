import sys, getopt, subprocess

def main(argv):
    command = ['bash', 'monitor']
    # base = ""
    opts, args = getopt.getopt(argv, "b:n:i:t:")
    for opt, arg in opts:
        command += [opt, arg]
        # base += " " + opt + " " + arg
        # if opt == "-b":
        #     base = arg
    subprocess.call(command)

if __name__ == '__main__':
    main(sys.argv[1:])