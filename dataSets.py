import subprocess

def get_zfs_datasets():
    try:
        # Get the list of all ZFS datasets
        result = subprocess.run(['zfs', 'list', '-o', 'name', '-t', 'filesystem,volume'], capture_output=True, text=True, check=True) 
        datasets = result.stdout.strip().split('\n')
        
        # Print the datasets
        for dataset in datasets:
            print(dataset)
            
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running zfs command: {e}")

if __name__ == "__main__":
    get_zfs_datasets()
