import os
import sys
import zipfile
import datetime
import re
import shutil

def delete_pycache():
  for root, dirs, files in os.walk(os.getcwd()):
    for dir_name in dirs:
      if dir_name == "__pycache__":
        pycache_path = os.path.join(root, dir_name)
        try:
          shutil.rmtree(pycache_path)
          # print(f"Deleted: {pycache_path}")
        except Exception as e:
          print(f"Error deleting {pycache_path}: {e}")

def find_downloads_folder():
  downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
  if not os.path.isdir(downloads_path):
    os.makedirs(downloads_path, exist_ok=True)
  return downloads_path

def download_file(file_to_download = None):
  if file_to_download == None or file_to_download == -1:
    if file_to_download == None:
      print("\nNothing has been passed into the file_to_download variable. \nThus, downloading all py files :)")
    # file_paths = ["./main_interface.c", "./article_summarizer.py", "./article_generator.py"]
    file_paths = [f for f in os.listdir('.') if f.endswith('.py')]

    r = datetime.datetime.today()
    todayyy = f"{r.day}-{r.month}-{r.year}_{r.hour}-{r.minute}-{r.second}"

    zipper_file_name = f"zipped_file_{todayyy}.zip"

    zipper = zipfile.ZipFile(zipper_file_name, 'w')
    for fp in file_paths:
      zipper.write(fp, compress_type = zipfile.ZIP_DEFLATED)
    zipper.close()

    unzipper = zipfile.ZipFile(zipper_file_name, 'r')

    dwnlds_path = find_downloads_folder()
    unzipper.extractall(path = dwnlds_path)

    file_names = [fp.split('/')[-1] for fp in file_paths]
    print(f"\nDownload of files: {', '.join(file_names)} complete! Check your downloads folder :) \n")

    unzipper.close()

    curr_dir = os.getcwd()
    # parent_dir = os.path.dirname(curr_dir)

    count = 0

    # for folders, _, files in os.walk(parent_dir):
    #   for file in files:
    #     if re.search(r'^zipped_file_', file):
    #       print(f"Deleting file: {file}")
    #       os.remove(os.path.join(folders, file))
    #       count+=1

    for file in os.listdir(curr_dir):
      if file.startswith("zipped_file_"):
        try:
          os.remove(os.path.join(curr_dir, file))
          count += 1
        except PermissionError:
          print(f"Could not delete {file} (in use).")

    if count == 0:
      print("No zipped files found. So, nothing deleted.")
    else:
      print(f"{count} files deleted.")

    return

  else: # something has been passed into the file_to_download variable
    # only_file_name = (((file_to_download.strip('C:')).split('/')[-1]).split('\\')[-1]).split('\\\\')[-1]
    file_to_download = file_to_download.replace("\\", "/")
    only_file_name = os.path.basename(file_to_download)

    exists = False

    curr_dir = os.getcwd()
    for folders, _, files in os.walk(curr_dir):
      for file in files:
        if file == only_file_name:
          exists = True
          # print("FILE FOUND!")
          break
      if exists == True:
        break

    if exists == False:
      print("\nCannot download file as it doesn't exist :(")
      print("Thus, downloading all py files :)")
      download_file(-1)
      return

    try:
      extension = re.search(r'\.([^.]+)$', only_file_name).group(1)
    except:
      print("Cannot download file as it is not a csv, py, or txt :(")
      print("Thus, downloading all py files :)")
      download_file(-1)
      return

    file_path = file_to_download

    r = datetime.datetime.today()
    todayyy = f"{r.day}-{r.month}-{r.year}_{r.hour}-{r.minute}-{r.second}"

    zipper_file_name = f"zipped_file_{todayyy}.zip"

    zipper = zipfile.ZipFile(zipper_file_name, 'w')
    zipper.write(file_path, compress_type = zipfile.ZIP_DEFLATED)
    zipper.close()

    unzipper = zipfile.ZipFile(zipper_file_name, 'r')

    dwnlds_path = find_downloads_folder()
    unzipper.extractall(path = dwnlds_path)

    print(f"\nDownload of file: {file_path} complete! Check your downloads folder :) \n")
    unzipper.close()

    curr_dir = os.getcwd()
    # parent_dir = os.path.dirname(curr_dir)

    count = 0

    # for folders, _, files in os.walk(parent_dir):
    #   for file in files:
    #     if re.search(r'^zipped_file_', file):
    #       print(f"Deleting file: {file}")
    #       os.remove(os.path.join(folders, file))
    #       count+=1

    for file in os.listdir(curr_dir):
      if file.startswith("zipped_file_"):
        os.remove(os.path.join(curr_dir, file))
        count += 1

    if count == 0:
      print("No zipped files found. So, nothing deleted.")
    else:
      print(f"{count} files deleted.")

    return

if __name__ == "__main__":
  if len(sys.argv) > 1:
    download_file(sys.argv[1])
  else:
    download_file()
