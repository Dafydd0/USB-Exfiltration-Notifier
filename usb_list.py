import os
import win32api
import win32file
import time
import json
from datetime import datetime
import socket
import getpass

def list_files_in_drive(drive):
    print("Files in Drive %s:" % drive)
    try:
        for root, dirs, files in os.walk(drive):
            print(f"\nRoot folder: {root}")
            print("Files:")
            for file in files:
                print(os.path.join(root, file))
            print("Folders:")
            for dir in dirs:
                print(os.path.join(root, dir))
    except Exception as e:
        print("Error accessing drive:", e)

def monitor_usb():
    while True:
        drives = win32api.GetLogicalDriveStrings().split('\x00')[:-1]

        for device in drives:
            type = win32file.GetDriveType(device)
            print("Drive: %s" % device)
            print(drive_types[type])
            print("-" * 72)
            if type == win32file.DRIVE_REMOVABLE:
                print("USB detected:", device)
                list_files_in_drive(device)
                monitor_files_in_drive(device)

        time.sleep(5)  # Espera 5 segundos antes de volver a verificar

def monitor_files_in_drive(drive):
    monitored_files = {}
    scan_folder(drive, monitored_files)

    while True:
        new_files = {}
        scan_folder(drive, new_files)

        added_files = set(new_files.keys()) - set(monitored_files.keys())
        if added_files:
            print("New files added:")
            for file in added_files:
                print(os.path.join(drive, file))
                size = new_files[file]
                generate_json(file, drive, 'add', size)
            monitored_files.update(new_files)

        deleted_files = set(monitored_files.keys()) - set(new_files.keys())
        if deleted_files:
            print("Files deleted:")
            for file in deleted_files:
                print(os.path.join(drive, file))
                size = monitored_files[file]  # Obtener el tamaño del archivo eliminado
                generate_json(file, drive, 'delete', size)
            for file in deleted_files:
                monitored_files.pop(file)  # Eliminar el archivo de la lista de archivos monitoreados

        time.sleep(2)  # Espera 2 segundos antes de volver a verificar

def scan_folder(folder, file_dict):
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), folder)
            file_size = os.path.getsize(os.path.join(root, file))
            file_dict[file_path] = file_size

def generate_json(file_path, drive, event_type, size):
    timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    user = getpass.getuser()
    hostname = socket.gethostname()

    data = {
        "timestamp": timestamp,
        "user": user,
        "hostname": hostname,
        "filepath": os.path.dirname(file_path),
        "filename": os.path.basename(file_path),
        "size": size
    }

    if event_type == 'add':
        json_folder = os.path.join(os.getcwd(), 'Eventos', 'Add')
    elif event_type == 'delete':
        json_folder = os.path.join(os.getcwd(), 'Eventos', 'Delete')
    else:
        raise ValueError("Event type must be 'add' or 'delete'")

    os.makedirs(json_folder, exist_ok=True)
    json_filename = f"{timestamp}.json"
    json_path = os.path.join(json_folder, json_filename)

    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    drive_types = {
        win32file.DRIVE_UNKNOWN: "Unknown\nDrive type can't be determined.",
        win32file.DRIVE_REMOVABLE: "Removable\nDrive has removable media. This includes all floppy drives and many other varieties of storage devices.",
        win32file.DRIVE_FIXED: "Fixed\nDrive has fixed (nonremovable) media. This includes all hard drives, including hard drives that are removable.",
        win32file.DRIVE_REMOTE: "Remote\nNetwork drives. This includes drives shared anywhere on a network.",
        win32file.DRIVE_CDROM: "CDROM\nDrive is a CD-ROM. No distinction is made between read-only and read/write CD-ROM drives.",
        win32file.DRIVE_RAMDISK: "RAMDisk\nDrive is a block of random access memory (RAM) on the local computer that behaves like a disk drive.",
    }

    monitor_usb()
