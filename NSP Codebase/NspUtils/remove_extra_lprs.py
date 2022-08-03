import os
import re

input_dir = "/home/thomas/Desktop/All Datafiles/Scheduling Benchmarks/rest-skill"
for file in os.listdir(input_dir):
    if re.match(f'.*-0-rest-skill-0-lpr.*', file):
        new_name = re.sub("-0-rest-skill-0-lpr", "-rest-skill-0-lpr", file)
        os.rename(f"{input_dir}/{file}", f"{input_dir}/{new_name}")

for file in os.listdir(input_dir):
    if re.match(f'.*-[\d]-rest-skill-0-lpr.*', file):
        print("Removing: ", file)
        os.remove(f"{input_dir}/{file}")
