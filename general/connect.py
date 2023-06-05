import os, sys
from os.path import dirname, abspath

if getattr(sys, 'frozen', False):
    filedir = os.path.dirname(sys.executable)
elif __file__:
    filedir = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, 'frozen', False):
    basedir = os.path.dirname(os.path.dirname(sys.executable))
elif __file__:
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(1, basedir)
import paramiko
import time
import traceback
import datetime
import pandas as pd
from general import ssh_connection



HOST_SERVER= sys.argv[1]
kUserName = sys.argv[2]
PASSWORD_PATH = sys.argv[3]
TARGET_LOG_FILE = sys.argv[4]
STATUS_DCT = {}
SEP = "\t"
SEPERATOR = "^^^"

if os.path.exists(TARGET_LOG_FILE):
	print("loading previous states")
	dataframe = pd.read_csv(TARGET_LOG_FILE, sep=SEP, encoding="iso-8859-1", error_bad_lines=False)
	dataframe = dataframe[["JOBID", "ST"]].groupby("JOBID").last().reset_index().to_dict("r")
	STATUS_DCT = {x["JOBID"]: x["ST"] for x in dataframe}
	print("loaded "+str(len(STATUS_DCT))+" previous states")
while True:
	try:
		ssh1 = ssh_connection.get_ssh_client(HOST_SERVER, kUserName, PASSWORD_PATH)
		while True:
			# ssh_stdin, ssh_stdout, ssh_stderr = ssh1.exec_command(
			# 	"squeue -o '%a{0}%A{0}%c{0}%C{0}%f{0}%F{0}%j{0}%o{0}%p{0}%t{0}%y{0}%s{0}%r{0}%P{0}%m{0}%B{0}%g{0}%E'".format(SEPERATOR))

			ssh_stdin, ssh_stdout, ssh_stderr = ssh1.exec_command(
				"squeue -o '%a{0}%u{0}%A{0}%E{0}%c{0}%C{0}%f{0}%F{0}%j{0}%o{0}%p{0}%t{0}%y{0}%s{0}%S{0}%e{0}%M{0}%l{0}%L{0}%r{0}%P{0}%m{0}%B{0}%g'".format(SEPERATOR))

				

			output = [x.strip().split(SEPERATOR) for x in ssh_stdout.read().decode("utf-8", errors='ignore').split("\n")[:-1]]

			for i in range(len(output)):
				output[i] = [x for x in output[i] if x]
			columns = output[0]

			if not os.path.exists(TARGET_LOG_FILE):
				F = open(TARGET_LOG_FILE, "w")
				for x in columns:
					F.write("%s" % (x) + SEP)
					
				F.write("CURRENT_TIMESTAMP\n")
				F.close()

			F = open(TARGET_LOG_FILE, "a")

			for row in output[1:]:
				updates_count = 0
				dct = {columns[i]: row[i].strip() for i in range(len(columns))}
				if ((dct["JOBID"] not in STATUS_DCT or (dct["JOBID"] in STATUS_DCT and STATUS_DCT[dct["JOBID"]] != dct["ST"])) and len(dct) == len(columns)):
					current_timestamp = str(datetime.datetime.now())
					for i in range(len(columns)):
						F.write("%s" % (row[i]) + SEP)
					F.write("%s" % (current_timestamp) + "\n")
					STATUS_DCT[dct["JOBID"]] = dct["ST"]
			F.close()
			time.sleep(1)
		time.sleep(10)
	except Exception as e:
		traceback.print_exc()
		break