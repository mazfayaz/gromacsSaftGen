Description : 
  - This is a tool to generator gromacs input files using the SAFT-gamma Mie forcefield. 
  - The input files contain all information except the angle and torsion potentials, so add accordingly. 
 
Requirements: 
  - Python
  - GROMACS/4.5.5 (if you want to change this to 5.1 or later version let me know, we could collaborate!)

To run:
  1. Edit the file input.sh
    - quite self explanatory, if not talk to me
    
  2. If molecule doesnt exist in db.csv or parameters are wrong, add the molecule to the db.
    - make sure no first-third letter combination molecular names are repeated:
      e.g. gromacs would fail if you want to simulate Carbon and Coronene and name molecules the same way
           instead you could do Ca1rbon and Co2ronene
           
  2. type "bash input.sh"
    - output would be Simul-hr-min-second

