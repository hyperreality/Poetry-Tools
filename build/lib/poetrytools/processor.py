import os
from poetics import guess_form

for file in os.listdir("poems"):
    print(file + ' = ' + poetics.guess_form('poems/' + file))