import sys
import os
import subprocess

# input/output utils

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

def get_input(prompt, default=None):
    """
    Get user's input, only checking for non-empty response.
    """
    user_input = ""
    if default is not None:
        prompt = prompt+" (default: "+default+")"

    while user_input == "":
        user_input = raw_input(prompt+"\n")

        if user_input == "":
            if default is not None:
                user_input = default
            else:
                print "The value cannot be blank."

    return user_input

# converted from one line script utils to python callable

def print_warn(msg):
    print ""
    call_command("tput setaf 3") # 3 = yellow
    sys.stdout.write("[ WARNING ]\n")
    call_command("tput sgr0")
    sys.stderr.write(msg+"\n")

def print_failure():
    print ""
    call_command("tput setaf 1") # 1 = red
    print_right("[ FAILED ]")
    call_command("tput sgr0")

def print_success():
    call_command("tput setaf 2") # 2 = green
    print_right("[ OK ]")
    call_command("tput sgr0")

def print_step(msg):
    call_command("tput setaf 6")
    sys.stdout.write(msg+"\n")
    call_command("tput sgr0")

def print_right(msg):
    call_command("tput cuu1")
    call_command("tput cuf $(tput cols)")
    call_command("tput cub %d" % len(msg))
    sys.stdout.write(msg+"\n")

def exit_with_message(msg):
    sys.stderr.write(msg+"\n")
    sys.exit()

def exit_with_failrue(msg):
    print_failure()
    exit_with_message(msg)
  
# utils using subprocess 

def call_command(command):  
    """
    Process the given command in a bash shell and return the returncode.

    Warning: Make sure the command is sanitized before 
    calling this function to prevent any vulnerability. 
    """
    res = subprocess.call(command, shell=True, 
    executable='/bin/bash')
    return res

def command_exists(command):
    """From install.sh
    """
    res = call_command("hash "+ command+ " >/dev/null 2>&1")
    if res != 0:
       return False
    else:
       return True

def get_command_output(command):
    try:
        res = subprocess.check_output(command, shell=True, 
        stderr=subprocess.STDOUT,
        executable='/bin/bash')
    except:
        res = None

    return res

# utils using os

def check_path_exists(path, expand=False):
    if( expand ):
        path = os.path.expanduser(path)

    return os.path.exists(path)

# Other helpers

def write_file(filename):
    try:
        out = open(filename, "w")
    except:
        sys.stderr.write("Unable to write %s.\n" % filename)
        out = None
    return out

def get_http_status(url):
    status_cmd = "curl --head -s "+url+" | head -n 1"
    return get_command_output(status_cmd)

if __name__ == "__main__":
    ask("Begin testing")
    print call_command("ls > /dev/null")
    print command_exists("python")
    print_step("Next step is")
    print_warn("REALLY long text"*10)
