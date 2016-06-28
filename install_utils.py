import sys
import os

def ask(question, default="yes"):
   """Ask a yes/no question via raw_input() and return their answer.

   source: http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input
   "question" is a string that is presented to the user.
   "default" is the presumed answer if the user just hits <Enter>.
   It must be "yes" (the default), "no" or None (meaning
       an answer is required of the user).

   The "answer" return value is True for "yes" or False for "no".
   """

   valid = {"yes": True, "y": True, "ye": True,
            "no": False, "n": False}

   if default is None:
      prompt = " [y/n] "
   elif default == "yes":
      prompt = " [Y/n] "
   elif default == "no":
      prompt = " [y/N] "
   else:
      raise ValueError("Invalid default answer: '%s'" % default)

   while True:
      sys.stdout.write(question + prompt)
      choice = raw_input().lower()
      if default is not None and choice == '':
          return valid[default]
      elif choice in valid:
          return valid[choice]
      else:
          sys.stdout.write("Please respond with 'yes' or 'no' "
                           "(or 'y' or 'n').\n")

def check_collecd_path():
    path = os.path.expanduser("/etc/collectd")

    if not os.path.exists(path):
        print "%s does not exists" % (path)
    else:
        print "%s does exists" % (path)

def file_append(filename):
    try:
        out = open(filename, "a")
    except:
        sys.stderr.write("Unable to write to %s.\n" % filename)
        sys.exit()
    return out



if __name__ == "__main__":
    query_yes_no("Just checkng", None)

