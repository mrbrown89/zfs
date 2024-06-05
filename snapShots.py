import subprocess

def get_zfs_snapshots():
    try:
        # Get the list of all ZFS snapshots
        result = subprocess.run(['zfs', 'list', '-t', 'snapshot', '-o', 'name,used'], capture_output=True, text=True, check=True)
        snapshots = result.stdout.strip().split('\n')
        
        # Print the snapshots and their sizes
        for snapshot in snapshots:
            print(snapshot)
            
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running zfs command: {e}")

if __name__ == "__main__":
    get_zfs_snapshots()
