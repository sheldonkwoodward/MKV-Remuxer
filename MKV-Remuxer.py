# Sheldon Woodward
# Remuxer - Script to automatically remux tv shows using MKVMerge
# 5/8/17

import subprocess
import os.path

# paths
MKVMergePath = 'C:/Program Files/MKVToolNix/mkvmerge.exe'
MKVPropeditPath = 'C:/Program Files/MKVToolNix/mkvpropedit.exe'
inputPath = 'E:/My Media/Re-encoding/2 - Encoded'
outputPath = 'E:/My Media/Re-encoding/3 - Remuxed'
subtitlePath = 'E:/My Media/Re-encoding/Subtitles'
trackInfoPath = 'E:/My Media/Re-encoding/3 - Remuxed'

# track names
videoTrackName = ""
stereoTrackName = '2.0 Stereo (AAC)'
surroundTrackName = '5.1 Surround (AC3)'
PGSForcedTrackName = 'Forced (PGS)'
PGSTrackName = 'Full (PGS)'
SRTForcedTrackName = 'Forced (SRT)'
SRTTrackName = 'Full (SRT)'

# input information
showName = input('Show name: ')
season = input('Season number: ')
includePGS = input('Include PGS (y/n): ')
includeSRT = input('Include SRT (y/n): ')

# determine season input type
if season.find('-') != -1:
    season = range(int(season[:season.find('-')]), int(season[season.find('-') + 1:]) + 1)
else:
    season = season.split(',')

# include PGS subtitles
if includePGS == 'y':
    includePGS = True
else:
    includePGS = False

# include SRT subtitles
if includeSRT == 'y':
    includeSRT = True
else:
    includeSRT = False

# rename episodes
if input('Rename Episodes (y/n): ') == 'y':
    for sNum in season:
        seasonInputPath = inputPath + '/' + showName + '/Season ' + str(sNum)
        for eNum in range(1, len(os.listdir(seasonInputPath)) + 1):
            episodeName = showName + ' S' + "{0:0=2d}".format(int(sNum)) + 'E' + "{0:0=2d}".format(int(eNum))
            sourcePath = seasonInputPath + '/' + os.listdir(seasonInputPath)[eNum - 1]
            destinationPath = seasonInputPath + '/' + episodeName + '.mkv'
            os.rename(sourcePath, destinationPath)

# output seasons to be remuxed
print('\n== Season List ==')
for s in season:
    print(' ' + showName + ' Season ' + str(s))

# show and write streams for all episodes
print('\n== Episode List ==')
with open(trackInfoPath + '/' + showName + ' Season ' + str(sNum) + '.txt', 'w') as out:
    for sNum in season:
        try:
            seasonInputPath = inputPath + '/' + showName + '/Season ' + str(sNum)
            for episode in os.listdir(seasonInputPath):
                print(' ' + episode[:-4])
                fileInputPath = seasonInputPath + '/' + episode
                subprocess.run('"' + MKVMergePath + '" --identify "' + fileInputPath + '"', stdout = out)
        except FileNotFoundError:
            print('FILES NOT FOUND')

# remux seasons
for sNum in season:
    # rebuild paths for season
    seasonInputPath = inputPath + '/' + showName + '/Season ' + str(sNum)
    seasonOutputPath = outputPath + '/' + showName + '/Season ' + str(sNum)
    seasonSubtitlePath = subtitlePath + '/' + showName + '/Season ' + str(sNum)

    # check input path
    if os.path.isdir(seasonInputPath) == False:
        print(showName + ' Season ' + str(sNum) + ' does not exist')
        continue

    # modify all episodes
    for episode in os.listdir(seasonInputPath):
        print('\n== Remuxing ' + episode[:-4] + ' ==')

        # set paths for specific episode
        fileInputPath = seasonInputPath + '/' + episode
        fileOutputPath = seasonOutputPath  + '/' + episode
        SRTPath = seasonSubtitlePath + '/' + episode[:-4] + '.srt'
        SRTForcedPath = seasonSubtitlePath + '/' + episode[:-4] + ' FORCED.srt'

        # generate commands
        command = []
        command.append('"' + MKVMergePath + '" --output "' + fileOutputPath + '" --title "' + episode[:-4] + '" --no-chapters --no-global-tags --no-attachments ')
        if includePGS is False:
            command.append('--no-subtitles ')
        command.append('--default-track 0:1 --forced-track 0:0 --language 0:und --track-name 0:"' + videoTrackName + '" ')
        command.append('--default-track 1:1 --forced-track 1:0 --language 1:eng --track-name 1:"' + stereoTrackName + '" ')
        command.append('--default-track 2:0 --forced-track 2:0 --language 2:eng --track-name 2:"' + surroundTrackName + '" ')
        if includePGS is True:
            command.append('--default-track 3:0 --forced-track 3:0 --language 3:eng --track-name 3:"' + PGSTrackName + '" ')
            command.append('--default-track 4:1 --forced-track 4:1 --language 4:eng --track-name 4:"' + PGSForcedTrackName + '" ')
        command.append('"' + fileInputPath + '" ')

        # add command if SRT files exist
        if includeSRT is True:
            if os.path.isfile(SRTPath):
                command.append('--default-track 0:0 --forced-track 0:0 --language 0:eng --track-name 0:"' + SRTTrackName + '" "' + SRTPath + '" ')
            if os.path.isfile(SRTForcedPath):
                command.append('--default-track 0:1 --forced-track 0:1 --language 0:eng --track-name 0:"' + SRTForcedTrackName + '" "' + SRTForcedPath + '" ')

        # build command
        fullCommand = ''
        for subCom in command:
            fullCommand += subCom

        # output and run command
        subprocess.run(fullCommand)

        # fix UIDs
        for UID in range(1, 8):
            subprocess.run('"' + MKVPropeditPath + '" "' + fileOutputPath + '" -e track:' + str(UID) + ' --set track-uid=' + str(UID))

input('Done')
