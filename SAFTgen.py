import numpy as np
import scipy as sc
import pandas as pd
import ast
import sys
import os
import datetime
import random

###### position class
class particle():
    def __init__(self,name, nseg, df):
        self.polyName = name
        self.name = (name[0]+name[2]).upper()
        if len(df[df['name'] == name]) == 0:
            raise LookupError('couldnt find the %i segment representation of molecule " %s " in the database' %(nseg, name))
        
        self.dfData = df[df['name'] == name]
        self.molName = self.name + self.polyName[len(self.polyName)-1].upper()
        self.dfData = self.dfData[self.dfData['m']==nseg]
        self.nseg = nseg
        self.eps = self.dfData.epsilon.values[0]
        self.eps2 = self.eps*1.3806488e-23/1000*6.0221413e23
        self.sig = self.dfData.sigma.values[0]
        self.lam = self.dfData.lambda_r.values[0]
        self.lamAtt = 6.
        self.MW = 40.
        self.preFact = (self.lam/(self.lam-self.lamAtt))*(self.lam/self.lamAtt)**(self.lamAtt/(self.lam-self.lamAtt))
        self.C = self.preFact*self.eps2*(self.sig*1e9)**self.lamAtt
        self.A = self.preFact*self.eps2*(self.sig*1e9)**self.lam


###### input files
## polymer epsilon, sigmas, lambdas table
df = pd.read_csv('db.csv', header=0)

print( '\n')
sysNu = int(raw_input('# of molecules'))

nav = []
for i in range(0, sysNu):
    nav.append(raw_input('Pls input the molecule [], and the nu of beads [], and total number of molecules []\n'))

temp = float(raw_input('Temperature  '))
press = float(raw_input('Pressure  '))
for i in range(0, len(nav)):
    nav[i] = ast.literal_eval(nav[i])

for i in range(0, len(nav)):
    nav[i][0][0] = nav[i][0][0].lower()


####### output files 
## gro files


####### ordering polymer beads etc 
polyTypes = []
for i in nav:
    for j in i[0]:
        polyTypes.append(j)

###### for each file type extract the epsilon sigmas etc
dataPolyTypes = []
for i in polyTypes:
    dataPolyTypes.append(i) 

print ('\n\n', nav)
for i in range(0, len(dataPolyTypes)):
    dataPolyTypes[i] = particle(nav[i][0][0], nav[i][1], df)
    print ('\n')


###### make itp file
itpfile = open('archipelago.itp', 'w')
os.system("rm tableMIE*")
itpfile.write('[ atomtypes ]\n')
itpfile.write('; Polymer interaction file generated by Maziar Fayaz Torshizi, Erich Muller on %s\n' % (datetime.date.today()))
itpfile.write('; Coarse-grained lego beads:\n')
for i in dataPolyTypes:
    itpfile.write('; %20s = %5s \t MW = %.2f \t nseg = %i\n' % (i.polyName, i.name, i.MW, i.nseg))
itpfile.write('\n')
itpfile.write('; name  bond_type  mass      charge   ptype   C            A\n')

##### make tables
for i in dataPolyTypes:
    itpfile.write('  %s\tC          %.5f  0.000    A       %.9f       %.5e\n' % (i.name, i.MW, i.C, i.A))
    os.system("echo '%f\n%f\n20' | forcefield/mie2gmx.exe" % (i.lam, i.lamAtt))
    os.system("mv tableMIE_*.xvg table_%s_%s.xvg" % (i.name, i.name))

itpfile.write('\n[ nonbond_params ]\n')
for i in range(0, len(dataPolyTypes)):
    for j in range(i+1, len(dataPolyTypes)):
        crossSig = (dataPolyTypes[i].sig+dataPolyTypes[j].sig) * .5
        crossEps = (dataPolyTypes[i].eps2*dataPolyTypes[j].eps2)**.5 * ((dataPolyTypes[j].sig**3 * dataPolyTypes[i].sig**3)**.5/crossSig**3)
        ##### Note to self here we assume lamAtt is 6 for calculating cross Lam, need to rewrite
        crossLam = 3+((dataPolyTypes[i].lam-3)*(dataPolyTypes[j].lam-3))**.5
        crosspreFact = (crossLam/(crossLam-6.))*(crossLam/6.)**(6./(crossLam-6))
        crossC = crosspreFact*crossEps*(crossSig*1e9)**6.
        crossA = crosspreFact*crossEps*(crossSig*1e9)**crossLam
        os.system("echo '%f\n%f\n20' | forcefield/mie2gmx.exe" % (crossLam, 6))
        os.system("mv tableMIE_*.xvg table_%s_%s.xvg" % (dataPolyTypes[i].name, dataPolyTypes[j].name))
        
        itpfile.write('  %s\t%s\t1        %.9f   %.5e\n' % ( dataPolyTypes[i].name, dataPolyTypes[j].name, crossC, crossA))
itpfile.write('\n\n\n')

for i in range(0,len(nav)): 
    itpfile.write('[ moleculetype ]\n')
    itpfile.write('; name %s  %i\n' % (dataPolyTypes[i].molName, nav[i][2]))
    itpfile.write('; name nrexcl\n')
    molName = dataPolyTypes[i].name + dataPolyTypes[i].polyName[len(dataPolyTypes[i].polyName)-1].upper()
    itpfile.write(' %s  1\n\n' % (molName))
    itpfile.write('[ atoms ]\n')
    itpfile.write(';       nr      type    resnr   residue atom    cgnr\n')
    for j in range(0, dataPolyTypes[i].nseg):
        itpfile.write('\t%i\t%s\t1\t%s\t%s\t%i\n' % (j+1, dataPolyTypes[i].name, molName, dataPolyTypes[i].name, j+1))

    itpfile.write('\n\n\n')

    itpfile.write('[ bonds ]\n')
    itpfile.write(';       ai      aj   funct   bo      kbo\n')

    mabdaArr = []

    for p in range(1, dataPolyTypes[i].nseg):
        itpfile.write('\t%i\t%i\t1\t%.4f\t6310.47\n' % (p, p+1, dataPolyTypes[i].sig*1e9))

    itpfile.write('\n\n\n')
    itpfile.write(';[ angles ]\n;;      ai   aj    ak    funct     angle    Kangle\n')
    itpfile.write('\n\n\n')
itpfile.close()



###### make the gro file
for i in range(0, len(nav)):
    molFound    = False
    atomFound   = False
    bondFound   = False
 
    molArr = [] 
    bondArr = []
    itpfile = open('archipelago.itp', 'r')
    for line in itpfile:
        words = line.split()
        if dataPolyTypes[i].molName in words and len(words) == 6:
            molFound = True
            print ([int(words[0]), words[1]], 'yayayayaya')
            molArr.append([int(words[0]), words[1]])

        if molFound == True and len(words) > 2 and words[1] == 'bonds':
            bondFound = True
        if bondFound == True and len(words) != 0 and words[0] != ';' and words[0] != '[' and words[0] != ';[':
            bondArr.append([int(words[0]), int(words[1])])
        if len(words) > 2 and words[1] == 'angles' and molFound == True:
            bondFound = False
            break

    polygro = open('polygro_%s.gro' % (dataPolyTypes[i].molName), 'w')
    xdir = 0
    ydir = 0
    zdir = 0


    polygro.write('Polymer configuration file generated by Maziar Fayaz Torshizi on %s\n' % (datetime.date.today()))
    polygro.write('    '+str(dataPolyTypes[i].nseg)+'\n')

    positionArr = []
    distSig = .6

    for j in range(0, dataPolyTypes[i].nseg):
        polygro.write('%5d%-5s%5s%5d' % (1, dataPolyTypes[i].molName, dataPolyTypes[i].name, j+1))
        for klm in xdir, ydir, zdir:
            polygro.write('%8.3f' % klm)
        polygro.write('\n')
        
        xdir = xdir + distSig
    polygro.write('   %.7f %.7f %.7f\n' %(xdir+distSig,xdir+distSig,xdir+distSig)  )
    polygro.close()


#totalNoBeads = 0
#for i in range(0,len(nav)):
#    totalNoBeads = totalNoBeads + (nav[i][len(nav[i]) - 1] * nav[i][1])

for i in range(0, len(nav)):
    if i == 0:
        os.system("genbox -cs polygro_%s.gro -maxsol %i -box %f -o out.gro" % (dataPolyTypes[i].molName, nav[i][len(nav[i])-1], 40))
        os.system("cat out.gro")
    else:
        os.system("genbox -cp out.gro -cs polygro_%s.gro -maxsol %i -o out.gro" % (dataPolyTypes[i].molName, nav[i][len(nav[i])-1]))
os.system("rm \#*")


####### make index file
index = open('index.sh', 'w')
index.write('#!/bin/bash\nmake_ndx -f out.gro << EOF\n')
for i in dataPolyTypes:
    index.write('a '+i.name+'\n')
index.write('q\n')
index.write('EOF\n')
index.close()
os.system('bash index.sh')


####### mdp files
mdpIn = open('mdpIn', 'w')
for i in dataPolyTypes:
    mdpIn.write('%s ' % i.name)
mdpIn.write('\n')

for i in range(0, len(dataPolyTypes)):
    for j in range(i, len(dataPolyTypes)):
        mdpIn.write('%s %s ' % (dataPolyTypes[i].name, dataPolyTypes[j].name))
mdpIn.write('\n')

for i in dataPolyTypes:
    mdpIn.write('%.2f ' %temp )
mdpIn.write('\n')

for i in dataPolyTypes:
    mdpIn.write('%.2f ' %press )
mdpIn.write('\n')

MAZ5 = 1.0
for i in dataPolyTypes:
    mdpIn.write('%.2f ' %MAZ5 )
mdpIn.write('\n')

compress = 4.50E-5
for i in dataPolyTypes:
    mdpIn.write('%.2e ' %compress )
mdpIn.write('\n')

highP = 100.0
for i in dataPolyTypes:
    mdpIn.write('%.2f ' %highP )
mdpIn.write('\n')

mdpIn.close()

os.system("for i in inputs/*.tmp; do b=$(echo ${i} | awk -F '/' '{print $NF}'| awk -F'.' '{print $1}'); a=$(head -1 mdpIn); sed \"s/MAZ /${a}/g\" inputs/${b}.tmp > ${b}.mdp; a=$(head -2 mdpIn | tail -1); sed -i \"s/MAZ2 /${a}/g\" ${b}.mdp; a=$(head -3 mdpIn | tail -1); sed -i \"s/MAZ3 /${a}/g\" ${b}.mdp; a=$(head -4 mdpIn| tail -1); sed -i \"s/MAZ4 /${a}/g\" ${b}.mdp; a=$(head -5 mdpIn| tail -1); sed -i \"s/MAZ5 /${a}/g\" ${b}.mdp; a=$(head -6 mdpIn| tail -1); sed -i \"s/MAZ6 /${a}/g\" ${b}.mdp; a=$(head -7 mdpIn| tail -1); sed -i \"s/MAZ7 /${a}/g\" ${b}.mdp;  done")

####### system.top file
sysIn = open('sysIn', 'w')
for i in range(0, len(nav)):
    sysIn.write('%s  %i\n' % (dataPolyTypes[i].molName, nav[i][len(nav[i])-1]))

sysIn.close()
os.system("cat inputs/system.tmp > system.top; cat sysIn >> system.top")


####### make vmdlog file
vmdlog = open('vmdlog', 'w')
vmdlog.write('menu graphics on\n')
for i in range(0, len(dataPolyTypes)):
    if i == 0:
        vmdlog.write('mol modselect %i 0 name %s\n' % (i, dataPolyTypes[i].name))
        vmdlog.write('mol modcolor %i 0 ColorID %i\n' % (i, i))
        vmdlog.write('mol modstyle %i 0 VDW 1.000000 12.000000\n' % (i))
    else:
        vmdlog.write('mol addrep 0\n')
        vmdlog.write('mol modselect %i 0 name %s\n' % (i, dataPolyTypes[i].name))
        vmdlog.write('mol modcolor %i 0 ColorID %i\n' % (i, i))
        vmdlog.write('mol modstyle %i 0 VDW 1.000000 12.000000\n' % (i))
    vmdlog.write('pbc box\n')
    vmdlog.write('display projection orthographic\n')

#####


time = datetime.datetime.now()

hrs = time.hour
mns = time.minute
scs = time.second

os.system("mkdir Simul-%s-%s-%s; for i in table_*.xvg; do cp ${i} table.xvg; done; for i in *.itp *.mdp *.xvg *.gro *.ndx *.top vmdlog; do mv ${i} Simul-%s-%s-%s; done; cp inputs/bashfile.sh Simul-%s-%s-%s " % (hrs,mns,scs,hrs,mns,scs,hrs,mns,scs))
os.system('rm index.sh sysIn mdpIn Simul-%s-%s-%s/system.tmp' % (hrs,mns,scs))

