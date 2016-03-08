import os
import poetics

for file in os.listdir("poems"):
    print(file + ' = ' + poetics.guess_form('poems/' + file))