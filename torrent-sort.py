import sys
import transmissionrpc

# Read a torrent file name.
file_name = sys.argv[1]
if file_name == None: sys.exit()

# Check to see if Transmission is running.  If not, attempt to start it.
c = transmissionrpc.Client()
t = c.add_torrent(file_name)
# t = c.get_torrent(0)

print t.

# Attempt to connect to Transmission

# Abort with error if Transmission isn't running

# Add the Torrent file to Transmission and get a Torrent object that we can
# read from and manipulate.

# Perform actions on Torrents based on critera read from Torrent object
# Ex: For torrents from What.cd, move the torrent download location to the appropriate place in the Music directory structure.

# Close Transmission connection (if necessary)