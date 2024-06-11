import subprocess
import platform
import requests
import argparse

def get_zfs_datasets():
    try:
        result = subprocess.run(['zfs', 'list', '-o', 'name', '-t', 'filesystem,volume'], capture_output=True, text=True, check=True)
        datasets = result.stdout.strip().split('\n')
        return datasets
    except subprocess.CalledProcessError as e:
        return f"An error occurred while running zfs command: {e}"

def get_zfs_version():
    try:
        result = subprocess.run(['zfs', '--version'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"An error occurred while running zfs command: {e}"

def get_os_info():
    return platform.platform()

def get_zfs_snapshots_count():
    try:
        result = subprocess.run(['zfs', 'list', '-t', 'snapshot', '-o', 'name'], capture_output=True, text=True, check=True)
        snapshots = result.stdout.strip().split('\n')
        return len(snapshots) - 1  # Exclude header
    except subprocess.CalledProcessError as e:
        return f"An error occurred while running zfs command: {e}"

def get_zfs_disk_status():
    try:
        result = subprocess.run(['zpool', 'status', '-v'], capture_output=True, text=True, check=True)
        status_output = result.stdout.strip()

        status_counts = {
            'ONLINE': 0,
            'DEGRADED': 0,
            'FAULTED': 0,
            'OFFLINE': 0,
            'UNAVAIL': 0,
            'REMOVED': 0
        }

        for line in status_output.split('\n'):
            for status in status_counts:
                if status in line:
                    status_counts[status] += 1

        return status_counts
    except subprocess.CalledProcessError as e:
        return f"An error occurred while running zpool command: {e}"

def get_zfs_space():
    try:
        result = subprocess.run(['zpool', 'list', '-Ho', 'name,size,alloc,free'], capture_output=True, text=True, check=True)
        pools = result.stdout.strip().split('\n')

        pool_details = []
        for pool in pools:
            name, size, alloc, free = pool.split()
            size = convert_to_bytes(size)
            alloc = convert_to_bytes(alloc)
            free = convert_to_bytes(free)

            used_percentage = (alloc / size) * 100
            remaining_percentage = 100 - used_percentage

            pool_info = {
                'name': name,
                'size': size,
                'alloc': alloc,
                'free': free,
                'remaining_percentage': remaining_percentage
            }
            pool_details.append(pool_info)

        return pool_details
    except subprocess.CalledProcessError as e:
        return f"An error occurred while running zpool command: {e}"

def convert_to_bytes(size_str):
    size_str = size_str.strip()
    size, unit = float(size_str[:-1]), size_str[-1].upper()
    unit_multipliers = {'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4, 'P': 1024**5, 'E': 1024**6}
    return size * unit_multipliers.get(unit, 1)

def send_to_slack(webhook_url, message):
    payload = {"text": message}
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print("Message sent to Slack successfully.")
    except requests.exceptions.HTTPError as e:
        print(f"Failed to send message to Slack: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a ZFS health check and send the results to a Slack channel.")
    parser.add_argument('-w', '--webhook', type=str, required=True, help="Slack webhook URL")
    args = parser.parse_args()

    webhook_url = args.webhook
    message = "Starting ZFS Health Check...\n\n"

    message += "Server OS:\n"
    message += get_os_info() + "\n\n"

    message += "ZFS Version:\n"
    message += get_zfs_version() + "\n\n"

    message += "ZFS Datasets:\n"
    datasets = get_zfs_datasets()
    if isinstance(datasets, str):
        message += datasets + "\n\n"
    else:
        message += "\n".join(datasets) + "\n\n"

    message += f"Number of ZFS Snapshots: {get_zfs_snapshots_count()}\n\n"

    disk_status = get_zfs_disk_status()
    if isinstance(disk_status, str):
        message += disk_status + "\n\n"
    else:
        message += "ZFS Disk Status:\n"
        for status, count in disk_status.items():
            message += f"{status}: {count}\n"
        message += "\n"

    message += "ZFS Space Usage:\n"
    pool_details = get_zfs_space()
    if isinstance(pool_details, str):
        message += pool_details + "\n\n"
    else:
        for pool in pool_details:
            message += f"Pool: {pool['name']}\n"
            message += f"Total Size: {pool['size'] / (1024 ** 3):.2f} GB\n"
            message += f"Used: {pool['alloc'] / (1024 ** 3):.2f} GB\n"
            message += f"Free: {pool['free'] / (1024 ** 3):.2f} GB\n"
            message += f"Remaining Space: {pool['remaining_percentage']:.2f}%\n"
            if pool['remaining_percentage'] < 10:
                message += f"WARNING: Remaining space in pool '{pool['name']}' is less than 10%\n"
            message += "\n"

    message += "ZFS Health Check Completed."

    send_to_slack(webhook_url, message)
