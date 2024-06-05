import subprocess
import xml.etree.ElementTree as ET

def get_zfs_disk_status():
    try:
        # Get the status of all ZFS pools in XML format
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
        
        # Print the results
        print(f"Healthy disks: {healthy_disks}")
        print(f"Failed disks: {failed_disks}")
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running zpool command: {e}")

if __name__ == "__main__":
    get_zfs_disk_status()
