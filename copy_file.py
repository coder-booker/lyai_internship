from pathlib import Path
import time


def copy_folder(terminal_input=False, origin_path=r'E:\learning\python\myPythonVS\intern\task_2\testing', destination_path=r"E:\learning\python\myPythonVS\intern\task_2\testing2"):

    if terminal_input:
        origin_path = Path(input("Please enter origin path: "))
        destination_path = Path(input("Please enter destination_path: "))
        print(f"Origin path: {origin_path}")
        print(f"Destination_path: {destination_path}")
    else:
        origin_path = Path(origin_path)
        if not origin_path.exists():
            print(f"Origin_path {origin_path} does not exist, please check the path.")
            exit()
        destination_path = Path(destination_path)


    file_name_list = [f.name for f in origin_path.iterdir()]

    print(f"\nCopying folder {destination_path}")
    destination_path.mkdir(parents=True, exist_ok=True)

    for file_name in file_name_list:
        
        file_ori_path = origin_path/file_name
        file_des_path = destination_path/file_name
        if file_ori_path.is_dir():
            copy_folder(origin_path=file_ori_path, destination_path=file_des_path)
        else:
            file_des_path.write_bytes(file_ori_path.read_bytes())

def main():
    time_now = time.time()
    
    copy_folder(terminal_input=False, origin_path=r"C:\Users\cp793\Desktop\temp", destination_path=r"C:\Users\cp793\Desktop\onedrive_temp\cloud\OneDrive\test upload")
    
    print(f"\nCompleted | Total time taken: {time.time() - time_now} s")

if __name__ == '__main__':
    main()
