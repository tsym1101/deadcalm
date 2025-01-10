import subprocess
import re
import sys
import dutil
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='copy tree structure.')
    parser.add_argument('-s', '--src', type=str, required=True, help='copy source.')
    parser.add_argument('-d', '--dst', type=str, required=True, help='copy destination.')

    args = parser.parse_args()
    src = args.src
    dst = args.dst

    dutil.logError('Dry run:')
    cmd = 'rsync -a --stats --dry-run ' + src + ' ' + dst
    proc = subprocess.Popen(cmd,
      shell=True,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      )
    remainder = proc.communicate()[0]
    mn = re.findall(r'Number of files: (\d+)', remainder)
    total_files = int(mn[0])
    dutil.logError('Number of files: ' + str(total_files))

    dutil.logError('Real rsync:')
    cmd = 'rsync -avP  --progress ' + src + ' ' + dst
    proc = subprocess.Popen(cmd,
      shell=True,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
    )
    while True:
      output = proc.stdout.readline()
      if 'to-check' in output:
        m = re.findall(r'to-check=(\d+)/(\d+)', output)
        progress = (100 * (int(m[0][1]) - int(m[0][0]))) / total_files
        sys.stdout.write('\rDone: ' + str(progress) + '%')
        sys.stdout.flush()
        if int(m[0][0]) == 0:
          break

    dutil.logError('\rFinished')