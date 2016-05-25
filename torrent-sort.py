import sys
import re
import os
import transmissionrpc
import psutil

# TODO: Copy all torrents to a central location

# See if Transmission is running
isRunning = False
for proc in psutil.process_iter():
    try:
        pinfo = proc.as_dict(attrs=['pid', 'name'])

        p = re.compile('transmission')
        if p.search(pinfo['name']):
        	isRunning = True
        	break
    except psutil.NoSuchProcess:
        pass

if isRunning:
	print 'Transmission is running already.  Adding torrent...'
else:
	print 'Transmission isn\'t running.  You should start it.'
	exit()
	# TODO: Attempt to launch Transmission

# Read a torrent file name.
file_name = sys.argv[1]

if file_name != None:
	print 'Attempting to add torrent file: ', file_name
else:
	print 'I need a torrent file in order to work :('
	sys.exit()

# Connect w/ Transmission and add the torrent file to it.
c = transmissionrpc.Client()
t = c.add_torrent('file://' + file_name)

# Update torrent to ensure that all fields are populated
t.update()

# TODO: Check to see if new torrent is a duplicate

# Perform actions on Torrents based on critera read from Torrent object
# Ex: For torrents from What.cd, move the torrent download location to the appropriate place in the Music directory structure.
def handle_whatcd(torrent):
	# Settings for this action
	DOWNLOAD_DIR = 'F:/Music'

	# Gather data from the torrent
	tmp = torrent.name.split(' - ')

	artist = tmp[0]
	album  = tmp[1].split(' (')[0]
	folder = artist[0].upper()

	# Make alphabet folder if not currently available
	path = DOWNLOAD_DIR + '/' + folder + '/' + artist + '/' + album

	try:
		os.mkdir(path)
	except OSError as exc:
		pass

	# Move torrent data to the new path
	c.move_torrent_data(torrent.id, path)

# List of patterns to search for in tracker URLs and corresponding functions to
# fire if a match is found
actions = {
	'what.cd': handle_whatcd
}

# Process actions on torrent
for action in actions:
	for tracker_url in t.trackers:
		p = re.compile(action)
		url = tracker_url['announce']

		if p.search(tracker_url['announce']):
			actions[action](t)