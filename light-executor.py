import sys
import os
import shlex
import subprocess
import time



# python /home/eli/light-weight-executer/jack/light-executor.py /media/eli/8004857404856E4A/auto_light_executer/samples__bakc/test_wine.exe /media/eli/8004857404856E4A/auto_light_executer/output /media/eli/8004857404856E4A/auto_light_executer/mount/test_wine


mount_path = ""
mount_dll_path = "/home/eli/container-fs/wine_dll/"

target_sample_path ='' 
api_log_filename = ''

#return 0: not alive, 1: alive
def process_is_alive(process_name):
    pid = 0 
    try:
        pid= int(subprocess.check_output(["pidof",process_name]))
    except subprocess.CalledProcessError:
        return 0 
    else:
        return 1 

#if the process exist , kill it
#return 0: dont' exist, the process termanated by itself   1:killed
def process_kill_if_exist(process_name):
    pid = 0 
    try:
        pid= int(subprocess.check_output(["pidof",process_name]))
    except subprocess.CalledProcessError:
        os.system("docker rm "+process_name) 

        return 0 
    else:
        print "[executor] the process %s ,terminated by monitor!" % process_name
        os.system("docker kill "+process_name) 
        os.system("docker rm "+process_name) 
        return 1 


def prepare(input_sample_path):

    global target_sample_path 
    
    target_sample_path = os.path.join(mount_path, os.path.basename(input_sample_path) ) 

    command = "cp "+input_sample_path+" "+target_sample_path 
    os.system(command) 
    
def wait_container_run(target_name):
    #cmd = "docker inspect "+ target_name
    while True:
        try:
            return_inspect = subprocess.check_output(["docker","inspect",target_name])
        except subprocess.CalledProcessError:
            #print "[WARNING] wait for container %s to start" % target_name
            time.sleep(1)
        else:
            #print "[SUCCESS] contrainter %s start succ" % target_name
            return

def run():
    
    global target_sample_path
    global api_log_filename 

    target_name = os.path.basename(target_sample_path) 

    target_path = os.path.join("/samples",target_name) 

    api_log_filename = os.path.splitext(target_name)[0]+"_api.log"
    # docker run -i -t --mount type=bind,src=/home/eli/container-fs/wine_dll/,dst=/wine_dll,readonly --mount type=bind,src=/home/eli/light-weight-executer/mount,dst=/samples wine-test /bin/sh
    # WINEPREFIX=/home/jack/.wine WINEDLLPATH=/wine_dll WINEDEBUG=+relay /wine_dll/wine /samples/test_findfirstfile.exe &>/samples/api.log
    # docker run --name test_findfirstfile.exe -i -t --mount type=bind,src=/home/eli/container-fs/wine_dll/,dst=/wine_dll,readonly --mount type=bind,src=/home/eli/light-weight-executer/mount,dst=/samples wine-test /bin/sh -c "WINEPREFIX=/home/jack/.wine WINEDLLPATH=/wine_dll WINEDEBUG=+relay /wine_dll/wine /samples/test_findfirstfile.exe &>/samples/api.log "
    command = "docker run "+ "--name "+target_name+ " --mount type=bind,src=" + mount_dll_path+",dst=/wine_dll,readonly --mount type=bind,src="+mount_path+",dst=/samples wine-test /bin/sh -c \"WINEPREFIX=/home/jack/.wine WINEDLLPATH=/wine_dll WINEDEBUG=+relay /wine_dll/wine "+ target_path+" &>/samples/"+ api_log_filename +" \"" 
    #print command 

    args = shlex.split(command) 

    #print args
    #print "" 

    
    p = subprocess.Popen(args) 

    wait_container_run(target_name)  # fix bug cause by process_is_alive , due to the Popen return wthout wait, so docker may not running when check process_is_alive
    
    time_remain = 600

    slip = 2 

    while time_remain >= 0:
        time.sleep(slip) 

        if not process_is_alive(target_name):
            print "[executor] the process: %s , terminated by itself!" % target_name
            os.system("docker rm "+target_name)
            #os.system("docker kill "+target_name) 
            return 
        time_remain=time_remain-slip 

    process_kill_if_exist(target_name) 

    





def finish(output_path):
    global api_log_filename
    global mount_path
    command = "cp "+os.path.join(mount_path,api_log_filename)+" "+output_path 
    #command = "cp "+os.path.join(mount_path,"api.log")+" "+output_path 

    os.system(command) 


if __name__=="__main__":
    if len(sys.argv)!=4:
        print "python light-executor.py <sample path> <output log path> <mount dir>" 
        sys.exit(1) 
    
    sample_path = sys.argv[1] 
    output_path = sys.argv[2] 
    mount_path  = sys.argv[3]

    prepare(sample_path) 
    run() 
    finish(output_path) 

