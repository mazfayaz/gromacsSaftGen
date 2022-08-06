
#!/bin/sh
for i in `seq 1 2`
do
grompp -v -f EQM.mdp -c out.gro -o run_mpi.tpr -p system.top -n index.ndx -maxwarn 1
mdrun -v -s run_mpi.tpr -c out.gro -table table.xvg -nt 8
done

grompp -v -f EQM.mdp -c out.gro -o run_mpi.tpr -p system.top -n index.ndx -maxwarn 1
mdrun -v -s run_mpi.tpr -c out3.gro -table table.xvg -nt 8


for i in `seq 1 20`
do
rm \#*
grompp -v -f NPT.mdp -c out3.gro -o run_mpi.tpr -p system.top -n index.ndx -maxwarn 1
mdrun -v -s run_mpi.tpr -c out3.gro -table table.xvg -nt 12
done

for j in `seq 1 5`
do
grompp -v -f NPT.mdp -c out3.gro -o run_mpi.tpr -p system.top -n index.ndx -maxwarn 1
mdrun -v -s run_mpi.tpr -c out3.gro -table table.xvg -cpi state.cpt -nt 12
done

grompp -v -f NVT.mdp -c out3.gro -o run_mpi.tpr -p system.top -n index.ndx -maxwarn 1
mdrun -v -s run_mpi.tpr -c out4.gro -table table.xvg -nt 12


#trjconv -s run_mpi.tpr -f out4.gro -o out5.gro -pbc whole << EOF
#0
#EOF
#
#genconf -f out5.gro -o FinalBox2.gro -nbox 2
#
#for i in `seq 1 7`; do awk '/moleculetype/{getline; print $3 " " $4}' archipelago.itp >> system.top; done
#b=$(awk -F= '/energygrps/{print $2}' NVT.mdp | awk '{gsub (" ", "\na ", $0) ;print}')
#
#make.ndx -maxwarn 1 -f FinalBox2.gro << EOF
#${b}
#q
#EOF
#
#grompp -v -f NVT3.mdp -c FinalBox2.gro -o run_mpi.tpr -p system.top -n index.ndx -maxwarn 1
#mdrun -v -s run_mpi.tpr -c FinalBox2.gro -table table.xvg -nt 12
