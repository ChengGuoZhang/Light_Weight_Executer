import os
import sys
from subprocess import call,Popen
import time

#sample_folder =  /media/eli/8004857404856E4A/auto_light_executer/samples__bakc
#output_folder = /media/eli/8004857404856E4A/auto_light_executer/output
#mount_folder = /media/eli/8004857404856E4A/auto_light_executer/mount

# cmd =  python automation.py /home/auto_light_weight_executer/samples /home/auto_light_weight_executer/output /home/auto_light_weight_executer/mount

# subcmd = python /home/auto_light_weight_executer/scripts/light-executor.py /home/auto_light_weight_executer/samples/test_findfirstfile.exe /home/auto_light_weight_executer/output/ /home/auto_light_weight_executer/mount

COMMON_DIR = r'/home/auto_light_weight_executer/'
SAMPLE_DIR = r'samples'
OUTUT_DIR  = r'output'
MOUNT_DIR  = r'mount'
CMD_PREFIX = r"python /home/auto_light_weight_executer/scripts/light-executor.py "


def batch_create_mount_dir(sample_path,mount_path):
    cmd_post = list()

    cur_outout = os.path.join(COMMON_DIR,OUTUT_DIR)

    for root, dirs, files in os.walk(sample_path):
        for f in files:
            cur_sample =  os.path.join(root,f)        
            folder_name = os.path.splitext(f)[0]
            new_dir = os.path.join(mount_path,folder_name)
            cur_mount = new_dir
            if os.path.exists(new_dir) == False:
                os.mkdir(new_dir)
            cmd_post.append(CMD_PREFIX+cur_sample+" "+cur_outout+" "+cur_mount)

    return cmd_post


def clear_docker_contain():
    os.system(r"docker rm $(docker ps -a -q)")
    print "clear dead containter"

def make_sample_name_legal(sample_path):
    for root, dirs, files in os.walk(sample_path):
        for f in files:
            legal_f = os.path.splitext(f)[0]
            os.rename(os.path.join(root,f),os.path.join(root,legal_f))

def main(sample_path, output_path, mount_path):
    clear_docker_contain()
    make_sample_name_legal(sample_path)
    cmd_post = batch_create_mount_dir(sample_path, mount_path)
    pids = list()
    for cmd in cmd_post:
        print cmd+"\n"
        pid = Popen(cmd,shell=True)
        pids.append(pid)
        time.sleep(10)
    
    for p in pids:
        p.wait()

    

if __name__ == '__main__':
    if len(sys.argv)!=4:
        print "python automation.py <sample root dir> <output log dir> <mount dir>" 
        sys.exit(1) 

    sample_path = sys.argv[1] 
    output_path = sys.argv[2]
    mount_path  = sys.argv[3] 

    main(sample_path, output_path, mount_path)

