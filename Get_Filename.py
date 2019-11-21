import os
path = r"C:\Users\ABCPT\Desktop\Project-Ditto-master\certafonso"
captions = []
for filename in os.listdir(path):
    #print(filename)
    if filename.endswith(".txt"):
        print(filename)
        with open(path + r"\\" + filename, "r") as file:
            print("1")
            for line in file:
                print("2")
                captions.append(line)
print(captions)
        
