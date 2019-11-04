import sys
import subprocess
import os
import ctypes

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            "Insufficient number of arguments provided to \"{}\"!\n".format(sys.argv[0]) + \
            "\n" + \
            "usage: run_gui_over_admin_ssh.cmd session_num cmd [cmd_args]\n" + \
            "    mode: Limited (l) or elevated (h).\n" + \
            "    session_num: Active GUI session ID to run the GUI app into.\n" + \
            "    cmd: The command name from the \"Path\" environment variable or the full path to the command to execute.\n" + \
            "    cmd_args: List of command line arguments for the command to execute."
        )
        sys.exit(1)
    
    # Set the user.
    user = None
    if 'user' not in os.environ or os.environ['user'].strip() == "":
        user = subprocess.check_output('C:\\Windows\\System32\\whoami.exe').decode('utf8').strip()
    else:
        user = os.environ['user'].strip()
    computername = '' if 'computername' not in os.environ else os.environ['computername'].strip()
    if computername != '' and user == '{0}\\{1}'.format(computername, user):
        user = os.environ['username'].strip()
    
    # Set the password (if possible).
    password = None
    password_file_path = os.path.join(os.path.expanduser('~'), ".run_gui_over_admin_ssh", "mypass")
    if os.path.exists(password_file_path):
        with open(password_file_path, "r") as fd:
            password = fd.read().strip()
    
    # Run the command through "PSExec" and exit.
    cmd = ['psexec', '\\\\127.0.0.1', '-u', user]
    if password:
        cmd += ['-p', password]
    cmd += ['-accepteula', '-nobanner', '-h' if sys.argv[1] == 'h' else '-l', '-i'] + sys.argv[2:]
    output = None
    exit_code = 0
    try:
        output = subprocess.check_output(cmd).decode('utf8')
    except subprocess.CalledProcessError as fd:
        fd_output = str(fd)
        fd_output_parts = fd_output.split()
        fd_output_last_part = fd_output_parts[len(fd_output_parts) - 1]
        fd_output_last_part_without_dot = fd_output_last_part[:len(fd_output_last_part) - 1]
        exit_code = ctypes.c_long(int(fd_output_last_part_without_dot)).value
    if output:
        print(output)
    sys.exit(exit_code)
