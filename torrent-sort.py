import sys
import re
import os
import transmissionrpc
import psutil

# TODO: Copy all torrents to a central location

# See if Transmission is running
isRunning = False
# Create a regex to search for the string 'transmission'
proc_rgx = re.compile('transmission')

for proc in psutil.process_iter():
    try:
    	# Get info for this process
        proc_info = proc.as_dict(attrs=['pid', 'name'])

        # Extract the process name
        proc_name = proc_info['name']

        # Sometimes process names are 'None'.  We'll skip those
        if proc_name == None: continue

        proc_name = proc_name.lower()

        # If this process is called 'transmission', we know Transmission is running
        if proc_rgx.search(proc_name):
        	isRunning = True
        	break
    except psutil.NoSuchProcess:
        pass

if not isRunning:
	print 'Transmission isn\'t running.  You should start it.'
	exit()
	# TODO: Attempt to launch Transmission

# Read a torrent file name.
try:
	file_name = sys.argv[1]

	# Check to see if file exists
	if not os.path.isfile(file_name):
		print 'The file you specified doesn\'t exist.'
		exit()
	else:
		print 'Adding torrent: ', file_name
except IndexError as exc:
	print 'You need to specify a torrent file.'
	sys.exit()

# Connect w/ Transmission and add the torrent file to it.
client = transmissionrpc.Client()
torrent = client.add_torrent('file://' + file_name, paused=True)

# Update torrent to ensure that all fields are populated
torrent.update()

# TODO: Check to see if new torrent is a duplicate

# Perform actions on Torrents based on critera read from Torrent object
# Ex: For torrents from What.cd, move the torrent download location to the appropriate place in the Music directory structure.
def handle_whatcd(torrent):
	print 'Torrent from What.cd detected!'

	# Settings for this action
	DOWNLOAD_DIR = 'F:/Music'

	# Gather torrent data from the user so we can figure out where to save the
	# torrent's payload.
	artist = ''
	album  = ''
	while len(artist) == 0:
		artist = raw_input('Artist: ')
		artist = artist.strip()

	while len(album) == 0:
		album = raw_input('Album : ')
		album = album.strip()

	# Determine what letter the artist name starts with, removing "the" from the
	# beginning of all artist names (i.e. The Beatles)
	the_pattern = re.compile('^The\s')
	folder = the_pattern.sub('', artist)[0].upper()

	# Make alphabet folder if not currently available
	path = DOWNLOAD_DIR + '/' + folder + '/' + artist + '/' + album
	
	# Keep the user appraised of our progress
	print 'Saving music to ', path

	try:
		os.mkdir(path)
	except OSError as exc:
		pass

	# Move torrent data to the new path
	client.move_torrent_data(torrent.id, path)

	# Now that we know where the torrent will live, start downloading it!
	client.start_torrent(torrent.id)

# List of patterns to search for in tracker URLs and corresponding functions to
# fire if a match is found
actions = {
	'what.cd': handle_whatcd
}

# Process actions on torrent
found_action = False
for action in actions:
	for tracker_url in torrent.trackers:
		p = re.compile(action)
		url = tracker_url['announce']

		if p.search(tracker_url['announce']):
			actions[action](torrent)
			found_action = True

# If no special actions could be taken, continue as usual.
if not found_action:
	print 'No special actions found. Starting torrent using defaults.'
	client.start_torrent(torrent.id)