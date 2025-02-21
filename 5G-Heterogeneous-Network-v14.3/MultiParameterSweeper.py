import subprocess
import shlex
import random
import shutil
import math
import sys
import datetime
import time
import os
import csv
from unittest import result

# Set the path of 64 bit NetSim Binaries to be used for simulation.
NETSIM_PATH = "C:\\Program Files\\NetSim\\Pro_v14_3\\bin\\bin_x64"

# Floating on-premise License
LICENSE_ARG = "5053@192.168.0.4"
# Node Locked/ Cloud License
# LICENSE_ARG="\"C:\\Program Files\\NetSim\\Pro_v13_1\\bin\"";

# Set NETSIM_AUTO environment variable to avoid keyboard interrupt at the end of each simulation
os.environ["NETSIM_AUTO"] = "1"

# Create IOPath directory to store the input Configuration.netsim file and the simulation output files during each iteration
if not os.path.exists("IOPath"):
    os.makedirs("IOPath")

# Create Data directory to store the Configuration.netsim and the Metrics.xml files associated with each iteration
if not os.path.exists("Data"):
    os.makedirs("Data")

# Clear the IOPath folder if it has any files created during previous multi-parameter sweep runs
for root, dirs, files in os.walk("IOPath"):
    for file in files:
        os.remove(os.path.join(root, file))

# Delete result.csv and individual_throughput.csv file if it already exists
if os.path.isfile("individual_throughput.csv"):
    os.remove("individual_throughput.csv")

if os.path.isfile("result.csv"):
    os.remove("result.csv")

# create a csv file to log the output metrics for analysis
csvfile = open("individual_throughput.csv", "w")

# Add headings to the CSV file
csvfile.write("TTT,HandoverMargin,Th_57,Th_58,Th_59,Th_60,Th_61,Th_62,Th_63,Th_64,Th_65,Th_66,Th_67,Th_68,Th_69,Th_70,Th_71,Th_72,Th_73,Th_74,Th_75,Th_76,Th_77,Th_78,Th_79,Th_80,Th_81,Th_82,Th_83,Th_84,Th_85,Th_86,Th_87,Th_88,Th_89,Th_90,Th_91,Th_92,Th_93,Th_94,Th_95,Th_96,Th_97,Th_98,Th_99,Th_100,Th_101,Th_102,Th_103,Th_104,Th_105,Th_106,Th_107,Th_108,Th_109,Th_110,Th_111,Th_112,Th_113,Th_114,Th_115,Th_116,Sum_Throughput(Mbps),Handover_Count")
csvfile.close()

# Individual Throughput file
resultfile = open("result.csv", "w")
resultfile.write("TTT,HandoverMargin,Sum_Throughput(Mbps),Handover_Count")
resultfile.close()

#Lines for Multiple Application in the file
lines = [
    'MENU NAME="Application_Metrics"\n',
    'TABLE NAME="Application_Metrics"\n',
    'SET A="Throughput (Mbps)" WHERE "Application Id"="{}"\n'
]

TTT =[128, 256, 512, 1024]

# create a folder with name as year-month-day-hour.minute.seconds inside the data folder
today = time.strftime("%Y-%m-%d-%H.%M.%S")
foldername = str(today)
sum_throughput = 0

# Iterate based on the number of time simulation needs to be run and the input parameter range
for j in TTT:
    for i in range(0,7):

        if os.path.isfile("Configuration.netsim"):
            os.remove("Configuration.netsim")

        if os.path.isfile("IOPath\\Configuration.netsim"):
            os.remove("IOPath\\Configuration.netsim")

        if os.path.isfile("IOPath\\Metrics.xml"):
            os.remove("IOPath\\Metrics.xml")

        # Call ConfigWriter.exe with arguments as per the number of variable parameters in the input.xml file
        cmd = "ConfigWriter.exe " + str(j)+ " " + str(i)
        print(cmd)
        os.system(cmd)

        # Copy the Configuration.netsim file generated by ConfigWriter.exe to IOPath directory
        if os.path.isfile("Configuration.netsim"):
            shutil.copy("Configuration.netsim", "IOPath\\Configuration.netsim")
            shutil.copy("ProtocolLogsConfig.txt", "IOPath\\ProtocolLogsConfig.txt")

        strIOPATH = os.getcwd() + "\\IOPath"

        # Run NetSim via CLI mode by passing the apppath iopath and license information to the NetSimCore.exe
        cmd = (
            'start "NetSim_Multi_Parameter_Sweeper" /wait /d '
            + '"'
            + NETSIM_PATH
            + '" '
            + 'NetSimcore.exe -apppath "'
            + NETSIM_PATH
            + '" -iopath "'
            + strIOPATH
            + '" -license '
            + LICENSE_ARG
        )

        # print(cmd)
        os.system(cmd)

        # Create a copy of the output Metrics.xml file for writing the result log
        if os.path.isfile("IOPath\\Metrics.xml"):
            shutil.copy("IOPath\\Metrics.xml", "Metrics.xml")
            os.system("MetricsCsv.exe IOPath")

        # Number of Script files i.e Number of Output parameters to be read from Metrics.xml
        # If only one output parameter is to be read only one Script text file with name Script.txt to be provided
        # If more than one output parameter is to be read, multiple Script text file with name Script1.txt, Script2.txt,...
        # ...,Scriptn.txt to be provided
        OUTPUT_PARAM_COUNT = 60

        if os.path.isfile("Metrics.xml"):
            # Write the value of the variable parameters in the current iteration to the result log
            csvfile = open("individual_throughput.csv", "a")
            csvfile.write("\n" +str(j)+ "," + str(i) + ",")
            csvfile.close()
            resultfile = open("result.csv", 'a')
            resultfile.write("\n" +str(j)+ "," + str(i) + ",")
            resultfile.close() 
            
            if OUTPUT_PARAM_COUNT == 1:
                # Call the MetricsReader.exe passing the name of the output log file for updating the log based on script.txt
                os.system("MetricsReader.exe individual_throughput.csv")
            else:
                for n in range(1, OUTPUT_PARAM_COUNT + 1, 1):
                    if os.path.isfile("Script.txt"):
                        os.remove("Script.txt")

                    with open('Script.txt', 'w') as file:
                        for line in lines:
                            file.write(line.format(n))
                    os.system("MetricsReader.exe individual_throughput.csv")

                    os.system("MetricsReader.exe res.txt")
                    with open('res.txt', 'r') as file:
                        content = file.readline()
                    number = float(content)
                    sum_throughput+=number;
                    os.remove('res.txt')
                    csvfile = open("individual_throughput.csv", "a")
                    csvfile.write(",")
                    csvfile.close()
                

        else:
            # Update the output Metric as crash if Metrics.xml file is missing
            csvfile = open("individual_throughput.csv", "a")
            csvfile.write("\n" + str(i) + "," + "crash" + ",")
            csvfile.close()

        # Write the sum throughput to the table
        k = str(sum_throughput) + ","
        csvfile = open("individual_throughput.csv", "a")
        csvfile.write(k)
        sum_throughput = 0
        csvfile.close()
        resultfile = open("result.csv", 'a')
        resultfile.write(k)
        resultfile.close() 

        #Get the Handover Count from log file
        file_path = strIOPATH +"\\log\\LTENR_Handover_Log.csv"  # Replace with your actual file path
        column_index = 6  # Replace with the index of the column you want to search (0 for the first column, 1 for the second, etc.)
        target_string = 'Handover Initiated'
        handover_count=0;
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) > column_index:
                    if row[column_index] == target_string:
                        handover_count += 1

        k = str(handover_count) + ","
        csvfile = open("individual_throughput.csv", "a")
        csvfile.write(k)
        csvfile.close()

        resultfile = open("result.csv", 'a')
        resultfile.write(k)
        resultfile.close() 

        # Name of the Output folder to which the results will be saved
        OUTPUT_PATH = "Data\\" + str(foldername) +"\\TTT_"+str(j)+ "\\Output_" + str(i)

        if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)

        # create a copy of individual_throughput.csv file present in sweep folder to date-time folder
        if os.path.isfile("individual_throughput.csv"):
            shutil.copy(os.path.join("individual_throughput.csv"), "Data\\" + str(foldername))
            shutil.copy(os.path.join("result.csv"), "Data\\" + str(foldername))

        # Create a copy of all files that is present in IOPATH to the desired output location
        files_names = os.listdir("IOPATH")
        for file_name in files_names:
            shutil.move(os.path.join("IOPATH", file_name), OUTPUT_PATH)

        # Delete Configuration.netsim file created during the last iteration
        if os.path.isfile("Configuration.netsim"):
            os.remove("Configuration.netsim")

        # Delete Metrics.xml file created during the last iteration
        if os.path.isfile("Metrics.xml"):
            os.remove("Metrics.xml")
    