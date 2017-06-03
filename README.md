# README #

Set up a Linux or Ubuntu VM instance to run this experiment.

### To Setup: ###

1. git clone https://bitbucket.org/cs244ms/pfabric_v2.git
2. cd pfabric_v2
3. chmod a+x setupenv.sh and run.sh
4. Run sudo ./setupenv.sh.  You will have to respond to some yes/no prompts during the execution of this script. 

### To Run Experiment: ###

1. Inside pfabric_v2, run with: sudo ./run.sh
2. Resulting plots will be saved in outputs folder
3. The entire experiment will take ~2.5 hours to run and each run will overwrite the current outputs folder.