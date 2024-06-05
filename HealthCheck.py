import subprocess
import platform

def get_zfs_filesystems():
    try:
        # Get the list of all ZFS filesystems
        result = subprocess.run(['zfs', 'list', '-o', 'name'], capture_output=True, text=True, check=True)
        filesystems = result.stdout.strip().split('\n')
        
        print("ZFS Filesystems:")
        for filesystem in filesystems:
            print(filesystem)
        print()
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running zfs command: {e}")

def get_zfs_version():
    try:
        # Get the ZFS version
        result = subprocess.run(['zfs', '--version'], capture_output=True, text=True, check=True)
        zfs_version = result.stdout.strip()
        
        print("ZFS Version:")
        print(zfs_version)
        print()
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running zfs command: {e}")

def get_os_info():
    os_info = platform.platform()
    print("Server OS:")
    print(os_info)
    print()

def get_zfs_snapshots_count():
    try:
        # Get the list of all ZFS snapshots
        result = subprocess.run(['zfs', 'list', '-t', 'snapshot', '-o', 'name'], capture_output=True, text=True, check=True)
        snapshots = result.stdout.strip().split('\n')
        
        # Exclude header
        snapshots_count = len(snapshots) - 1
        
        print(f"Number of ZFS Snapshots: {snapshots_count}")
        print()
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running zfs command: {e}")

def get_zfs_disk_status():
    try:
        # Get the status of all ZFS pools
        result = subprocess.run(['zpool', 'status', '-v'], capture_output=True, text=True, check=True)
        status_output = result.stdout.strip()
        
        # Initialize counters
        healthy_disks = 0
        failed_disks = 0
        
        # Process the output to count healthy and failed disks
        for line in status_output.split('\n'):
            if 'ONLINE' in line:
                healthy_disks += 1
            elif 'FAULTED' in line or 'OFFLINE' in line or 'UNAVAIL' in line:
                failed_disks += 1
        
        print(f"Healthy disks: {healthy_disks}")
        print(f"Failed disks: {failed_disks}")
        print()
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running zpool command: {e}")

def get_zfs_space():
    try:
        # Get the list of all ZFS pools with their used and available space
        result = subprocess.run(['zpool', 'list', '-Ho', 'name,size,alloc,free'], capture_output=True, text=True, check=True)
        pools = result.stdout.strip().split('\n')

        # Process each pool to check its space usage
        for pool in pools:
            name, size, alloc, free = pool.split()
            size = convert_to_bytes(size)
            alloc = convert_to_bytes(alloc)
            free = convert_to_bytes(free)

            used_percentage = (alloc / size) * 100
            remaining_percentage = 100 - used_percentage

            print(f"Pool: {name}")
            print(f"Total Size: {size / (1024 ** 3):.2f} GB")
            print(f"Used: {alloc / (1024 ** 3):.2f} GB")
            print(f"Free: {free / (1024 ** 3):.2f} GB")
            print(f"Remaining Space: {remaining_percentage:.2f}%")

            if remaining_percentage < 10:
                print(f"WARNING: Remaining space in pool '{name}' is less than 10%")

            print()  # Blank line for better readability

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running zpool command: {e}")

def convert_to_bytes(size_str):
    size_str = size_str.strip()
    size, unit = float(size_str[:-1]), size_str[-1].upper()
    unit_multipliers = {'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4, 'P': 1024**5, 'E': 1024**6}
    return size * unit_multipliers.get(unit, 1)

if __name__ == "__main__":
    print("Starting ZFS Health Check...\n")
    get_os_info()
    get_zfs_version()
    #get_zfs_filesystems()
    get_zfs_snapshots_count()
    get_zfs_disk_status()
    get_zfs_space()
    print("ZFS Health Check Completed.")
