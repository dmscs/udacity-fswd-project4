# Item Catalog
Simple website that displays asins, skus, keywords and uses Google login. Hopefully can be used as template for more complex interfaces. Next step is to add data visualization for keyword rank.

## Getting Started
Here are tools you need to get started.

## Git
If you don't already have Git installed, [download Git from git-scm.com](https://git-scm.com/downloads). Install the version for your operating system.

On Windows, Git will provide you with a Unix-style terminal and shell (Git Bash).
(On Mac or Linux systems you can use the regular terminal program.)

You will need Git to install the configuration for the VM. If you'd like to learn more about Git, take a look at our course about Git and Github.

## Virtual Box
VirtualBox is the software that actually runs the VM. [You can download it from virtualbox.org, here](https://www.virtualbox.org/wiki/Downloads). Install the platform package for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it.

Ubuntu 14.04 Note: If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center, not the virtualbox.org web site. Due to a [reported bug](https://ubuntuforums.org/showthread.php?t=2227131), installing VirtualBox from the site may uninstall other software you need.

## Vagrant
Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. [You can download it from vagrantup.com](https://www.vagrantup.com/downloads). Install the version for your operating system.

Windows Note: The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

## Fetch Source Code and VM Configuration
**Windows**: Use the Git Bash program (installed with Git) to get a Unix-style terminal.
**Other systems**: Use your favorite terminal program.

From the terminal, run:
```
git clone https://github.com/dmscs/udacity-fswd-project4 item_catalog
```
This will give you a directory named **item_catalog** complete with the source code for the flask application, a vagrantfile, and a bootstrap.sh file for installing all of the necessary tools.


## Run the virtual machine
Using the terminal, change directory to item_catalog (cd item_catalog), then change directory to vagrant (cd vagrant), then type vagrant up to launch your virtual machine.

## Running the Item Catalog App
Once it is up and running, type **vagrant ssh**. This will log your terminal into the virtual machine, and you'll get a Linux shell prompt. When you want to log out, type **exit** at the shell prompt. To turn the virtual machine off (without deleting anything), type **vagrant halt**. If you do this, you'll need to run **vagrant up** again before you can log into it.

Now that you have Vagrant up and running type **vagrant ssh** to log into your VM. change to the /vagrant directory by typing **cd /vagrant**. This will take you to the shared folder between your virtual machine and host machine.

Type ls to ensure that you are inside the directory that contains project.py, database_setup.py, and two directories named 'templates' and 'static'

Now type **python database_setup.py** to initialize the database.

Type **python lotsofasins.py** to populate the database with asins and skus. (Optional)

Type **python project.py** to run the Flask web server. In your browser visit http://localhost:5000 to view the item catalog app. You should be able to view, add, edit, and delete asins, skus, and keywords.
