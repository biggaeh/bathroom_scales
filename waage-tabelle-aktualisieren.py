#!/usr/bin/python
from datetime import datetime
import glob
import mmap
import os
import shutil

def tail(fname, window=20):
    """
    Returns the last `window` lines of file `f` as a list.
    """
    if window == 0:
        return []
    BUFSIZ = 1024
    f = open (fname, "r")
    f.seek(0, 2)
    bytes = f.tell()
    size = window + 1
    block = -1
    data = []
    while size > 0 and bytes > 0:
        if bytes - BUFSIZ > 0:
            # Seek back one whole BUFSIZ
            f.seek(block * BUFSIZ, 2)
            # read BUFFER
            data.insert(0, f.read(BUFSIZ))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            data.insert(0, f.read(bytes))
        linesFound = data[0].count('\n')
        size -= linesFound
        bytes -= BUFSIZ
        block -= 1
    f.close()
    return ''.join(data).splitlines()[-window:]

print "Content-type: text/html"
print ""
print "Started updating...<br>"

DATDIR = "/var/www/waage"
INFILE = DATDIR + "/waage.log"

# we save some data in this directory, just in case thee server dies...
BACKUPDIR = "/apps/owncloud/web/data/birger/files/Dev/Waage/backup"

# read in the log file, sent to us from the scales
# convert the date and the weight
inf = open (INFILE, 'r')
backf = open (BACKUPDIR + "/waage.log", 'a')
for line in inf:
    backf.write(line)
    lineliste = line.split(" ")
    wiegezeitsek = int(lineliste[0])
    wiegezeit = datetime.fromtimestamp(wiegezeitsek)
    wiegezeitstr = wiegezeit.strftime("%Y-%m-%d %H:%M")
    massehex = line[54:58]
    masse = float(int(massehex, 16))/100.0
    datfile = DATDIR + "waage.unknown.dat"
    # Assign the values to the correct family member
    if masse > 80 and masse < 110:
        datfile = DATDIR + "/waage.dad.dat"
    if masse > 50 and masse < 70:
        datfile = DATDIR + "/waage.mum.dat"
    if masse > 32 and masse < 40:
        datfile = DATDIR + "/waage.son.dat"
    if masse > 25 and masse < 31:
        datfile = DATDIR + "/waage.daughter.dat"
    dat = open (datfile, 'a')
    dat.write(wiegezeitstr + " " + str(masse) + "\n") 
    dat.close()
inf.close()
backf.close()
inf = open (INFILE, 'w')
inf.close()

index = open (DATDIR + "/index.html", "w")
index.write("<html>\n")
index.write("<head>\n")
index.write("<title>Bathroom scales</title>\n")
index.write("<link rel=\"stylesheet\" href=\"waage.css\" type=\"text/css\">\n")
index.write("</head>\n")
index.write("<body>\n")
index.write("<h2>Results of the last measurements</h2>\n")
index.write("<a href=\"http://ardbeg.daheim/devicedataservice/waage-tabelle-aktualisieren.py\">Click here for updating.</a><br>\n")


# We (re)draw the images based on the updated data files
# We use gnuplot for that
datfilelist = glob.glob(DATDIR + "/waage.*.dat")
for tdatfile in datfilelist:
    name = tdatfile.split(".")[-2]
    gpfile = open (DATDIR + "/waage." + name + ".gp", "w")
    gpfile.write("set xdata time\n")
    gpfile.write("set timefmt \"%Y-%m-%d %H:%M\"\n")
    gpfile.write("set term jpeg\n")
    gpfile.write("set output \"" + DATDIR + "/waage." + name + ".jpg\"\n")
    gpfile.write("set title \"Gewicht von " + name + "\"\n")
    gpfile.write("plot \"" + tdatfile + "\" using 1:3 with linespoints notitle\n")
    gpfile.close()
    os.system ("gnuplot " + DATDIR + "/waage." + name + ".gp > /dev/null 2>&1\n")
    index.write("<table><tr><td class='LIMG'><img src=\"waage." + name + ".jpg\" alt=\"" + name + "\">\n")
    index.write("</td><td><pre>\n")
    for tailline in tail (tdatfile, 20): 
        index.write(tailline + "\n")
    index.write("</pre></td></tr></table>\n")
    index.write("<br clear=all>\n")
    # backup the most important files (just in case)
    shutil.copy(DATDIR + "/waage." + name + ".gp", BACKUPDIR)
    shutil.copy(DATDIR + "/waage." + name + ".dat", BACKUPDIR)
    shutil.copy(DATDIR + "/waage." + name + ".jpg", BACKUPDIR)
index.write("<hr>\n")
index.write("</body>\n")
index.write("</html>\n")
shutil.copy(DATDIR + "/index.html", BACKUPDIR)

index.close()

print "Finished updating...<br>"
print "<a href=\"http://ardbeg.daheim/waage\">the results can be found here...</a>"
