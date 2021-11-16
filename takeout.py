import re

import os
import shutil

import json
from datetime import datetime
from win32_setctime import setctime

from exif import Image

# set exif timestamp for jpg
def exif_editor(file_path, time):
    if file_path.endswith(".jpg"):
        try:
            with open(file_path, 'rb') as image_file:
                my_image = Image(image_file)
            try:
                my_image.datetime
            except:
                my_image.datetime = time
                my_image.datetime_digitized = time
                my_image.datetime_original = time

                with open(file_path, 'wb') as new_image_file:
                    new_image_file.write(my_image.get_file())
                new_image_file.close()
            image_file.close()
        except:
            pass

# put data into string
def replace_by_index(org_str, index, replacement):
    new_str = org_str
    if index < len(org_str):
        new_str = org_str[0:index] + replacement + org_str[index + 1:]
    return new_str

print("Start:")

# place files in the Year\Month structure
print("Moving files...")
# find a date match (example 2020-10-10)
tpl = "[0-9]{4}[-]{1}[0-9]{2}[-]{1}[0-9]{2}"

for root, dirs, files in os.walk(".", topdown=False):
    for file_name in files:
        if re.search(tpl, root) is not None:
            # determine the date for the file
            parts = root.split('\\')
            dir_data = parts[len(parts)-1]
            dir_data = dir_data[0:8]
            dir_data = dir_data.replace('-', '\\')
            # create the new file path
            pointer = root.rfind('\\')
            new_path = root[0:pointer]
            new_path = new_path + '\\' + dir_data
            # create the folder and move the file
            os.makedirs(new_path, exist_ok=True)
            shutil.move(os.path.join(root, file_name), new_path + file_name)
    # delete empty dir
    if os.listdir(root) == []:
        os.rmdir(root)

# change the creation date of files based on JSON data
print("Editing the file time...")

for root, dirs, files in os.walk(".", topdown=False):
    for name in files:
        if name.endswith(".json"):
            # exclude metadata
            if name.find("метаданные") == -1:
                # read json data
                new_path = os.path.join(root, name)
                with open(new_path, encoding='utf-8') as json_file:
                    data = json.load(json_file)
                    try:
                        title = data["title"]
                        timestamp = data["photoTakenTime"]["timestamp"]
                        time = datetime.fromtimestamp(
                            int(timestamp)).strftime("%Y:%m:%d %H:%M:%S")
                        int_time = int(timestamp)
                        # determine the file path
                        file_path = root + "\\" + title
                        # change exif
                        exif_editor(file_path, time)
                        # change the file time
                        try:
                            os.utime(file_path, (int_time, int_time))
                            setctime(file_path, int_time)
                        except:
                            #print("File " + file_path + " not found.")
                            pass
                        # repeat for copies
                        try:
                            pointer = file_path.rfind(".")
                            edit_path = replace_by_index(file_path, pointer, "-измененный.")
                            
                            exif_editor(edit_path, time)
                            
                            os.utime(edit_path, (int_time, int_time))
                            setctime(edit_path, int_time)
                        except:
                            pass
                    # if title not found
                    except:
                        #print("Title from " + new_path + " not found.")
                        pass

# delete json on request
y = input("Remove JSON files? (y)\n")
if y == "y":
    print("Removing JSON files...")
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            if name.endswith(".json"):
                new_path = os.path.join(root, name)
                os.remove(new_path)
        # delete empty dir
        if os.listdir(root) == []:
            os.rmdir(root)

print("Completed!")
input("Press ENTER to exit.\n")