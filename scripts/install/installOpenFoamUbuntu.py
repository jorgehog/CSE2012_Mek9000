import sys, os

aptSettings = """
VERS=`lsb_release -cs`
sudo sh -c "echo deb http://www.openfoam.org/download/ubuntu $VERS main > /etc/apt/sources.list.d/openfoam.list"
"""

aptUpd = "sudo apt-get update"

aptGetCMD = """
sudo apt-get install openfoam211
sudo apt-get install paraviewopenfoam3120 
"""

reloadBashRC = """
usermod -s /bin/bash %s
bash ~/.bashrc
""" % os.getlogin()




def __configBashRC():
	print "Updating source directories..."

	os.system("cp ~/.bashrc .")
	
	testFile = open(".bashrc", "r")

	for line in testFile:
		if "source /opt/openfoam211/etc/bashrc" in str(line):
			print "Source directories up-to-date."
			return None

	bRC = open(".bashrc", 'a')
	bRC.write("\n# Open FOAM sources\nsource /opt/openfoam211/etc/bashrc\n")
	bRC.close()
	bRC = open(".bashrc", 'r')
	os.system("cp .bashrc ~/")

	print "Source directories successfully updated."
	


def main():
	print "Configurating apt-get sources for openFOAM and paraView..."
	os.system(aptSettings)
	print "Done."

	print "Updating apt-get package list..."
	os.system(aptUpd)
	print "Done."

	print "Installing openFOAM and paraView..."
	os.system(aptGetCMD)
	print "Done"

	__configBashRC()

	print "\n#######################################################################"
	print "# Installation script done.                                           #"
	print "# Reload the terminal (or type '. ~/.bashrc') to activate the changes.#"
	print "#######################################################################\n"

#	try: 
#		os.system("icoFoam -help > /dev/null")
#		print "Installation successfull."
#	except:
#		print "ERROR: Installation failed."
#		print "See http://www.openfoam.org/download/ubuntu.php for details about the steps of the installation."
#		sys.exit(1)



if __name__ == "__main__":
	main()








	
