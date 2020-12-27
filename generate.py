from os import getcwd, listdir, walk, mkdir
from shutil import copyfile, copy2, rmtree
from PIL import Image
import re

def main():
    files = list();
    for(dirpath, dirnames, filenames) in walk(getcwd()):
        files.extend(filenames)
        break

    paths = list(["workfolder", "gallery-big", "gallery-sm"])
    try:
        for path in paths:
            mkdir(f"{getcwd()}/{path}", 0o0777)
    except:
        print("program attempted to create needed directories and failed...")

    allowed_extensions = set(["jpg", "jpeg", "png", "bmp"])
    for file in files:
        extension = file.split(".")[-1]
        if extension.lower() in allowed_extensions:
            generate_image(file, extension)
            generate_HTML(file)
    fix_HTML()
    try:
        rmtree("workfolder")
    except:
        print("could not delete workfolder")

def generate_image(file, extension):
    filename = " ".join(file.split(".")[:-1:])
    try:
        image = Image.open(file)
    except:
        print(f"Image {file} couldn't load. Skipping...")
        return
    # Save original as png
    png = convert_image("", file, "png")
    copy2(png, "gallery-big")
    # Calculate new size
    height, width, minH, minW = 450, 450, 450, 450
    if (image.width < image.height):
        width = 450
        height = round(image.height * (450 / image.width))
        minH = 450
        minW = round(image.width * (450 / image.height))
    elif (image.width > image.height):
        height = 450
        width = round(image.width * (450 / image.height))
        minW = 450
        minH = round(image.height * (450 / image.width))
    # Remove alpha channel (if exists)
    if extension.lower() == "png":
        image = image.convert("RGB")
    # Save resized image and convert to jpeg
    resized_image = image.resize((minW, minH))
    resized_image = resized_image.save(f"workfolder/{filename}.{extension}")
    resized_image = convert_image("workfolder", f"{filename}.{extension}", "jpg")
    copy2(resized_image, "gallery-big")
    # Crop and save
    cropped = image.resize((width, height))
    box = [0, 0, width, height]
    difference = 0
    if (width > height):
        difference = width - height
        margin = difference / 2
        box[0], box[2] = margin, width - margin
    elif (width < height):
        difference = height - width
        margin = difference / 2
        box[1], box[3] = margin, height - margin
    cropped = cropped.crop(tuple(box))
    cropped = cropped.save(f"workfolder/{filename}.{extension}")
    cropped = convert_image("workfolder", f"{filename}.{extension}", "jpg")
    copy2(cropped, "gallery-sm")
    
def convert_image(directory, filename, extenstion):
    currentname = " ".join(filename.split(".")[:-1:])
    currentextension = filename.split(".")[-1]
    if currentextension != extenstion:
        try:
            directory = directory + "/"
            with Image.open(directory + filename) as im:
                im.save(f"workfolder/{currentname}.jpg", subsampling=0, quality=100)
            return f"workfolder/{currentname}.jpg"
        except OSError:
            print("cannot convert", filename)
    else:
        return filename

def generate_HTML(file):
    filename = " ".join(file.split(".")[:-1:])
    with open("output.html", "r") as file:
        current_HTML = file.read()
        with open("makefile", "r") as makefile:
            makefile = makefile.read()
            find_case = re.compile(r"(?:<---\s\w+\sSTART)(.+)(\s[a-zA-Z]+\sEND\s--->)")
            find_content = re.compile(r"(?:.+)(\{content\})(?:.+)")
            contents = find_case.finditer(makefile)
            i = 0
            base, row, img = "", "", ""
            for content in contents:
                if i == 0:
                    base = content.group(1)
                if i == 1:
                    row = content.group(1)
                else:
                    img = content.group(1)
                i += 1
            with open("output.html", "w") as write:
                if current_HTML == "":
                    current_HTML = base
                    current_HTML = re.sub(r"{content}", row, current_HTML)
                
                # Get row count
                rowC = re.compile("row")
                row_count = len(rowC.findall(current_HTML)) - 1

                # Get column count
                columnC = re.compile("src")
                column_count = len(columnC.findall(current_HTML))

                if column_count % 4 == 0 and column_count != 0:
                    current_HTML = re.sub(r"{content}", "", current_HTML)
                    current_HTML = re.sub(r"{postrow}", row, current_HTML)

                ## Create image
                image = ""
                image = img
                image = re.sub(r"{img}", filename, image)
                current_HTML = re.sub(r"{content}", image, current_HTML)
                write.write(current_HTML)

def fix_HTML():
    with open("output.html", "r") as file:
        current_HTML = file.read()
        with open("output.html", "w") as write:
            current_HTML = re.sub(r"{content}", "", current_HTML)
            current_HTML = re.sub(r"{postrow}", "", current_HTML)
            write.write(current_HTML)


main()



