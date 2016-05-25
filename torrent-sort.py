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
try:
	file_name = sys.argv[1]

	# Check to see if file exists
	if not os.path.isfile(file_name):
		print 'File name was given but doesn\'t exist :('
		exit()
	else:
		print 'Attempting to add torrent file: ', file_name
except IndexError as exc:
	print 'I need a torrent file in order to work :('
	sys.exit()

# Connect w/ Transmission and add the torrent file to it.
c = transmissionrpc.Client()
t = c.add_torrent('file://' + file_name, paused=True)

# Update torrent to ensure that all fields are populated
t.update()

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
	c.move_torrent_data(torrent.id, path)

	# Now that we know where the torrent will live, start downloading it!
	c.start_torrent(torrent.id)

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