import json
import requests
import csv

import os

source_extensions = ['.java', '.cpp', '.kt', '.c', '.cmake']

if not os.path.exists("data"):
    os.makedirs("data")

# GitHub Authentication function
def github_auth(url, lsttoken, ct):
    jsonData = None
    try:
        ct = ct % len(lstTokens)
        headers = {'Authorization': 'Bearer {}'.format(lsttoken[ct])}
        request = requests.get(url, headers=headers)
        jsonData = json.loads(request.content)
        ct += 1
    except Exception as e:
        pass
        print(e)
    return jsonData, ct

# @dictFiles, empty dictionary of files
# @lstTokens, GitHub authentication tokens
# @repo, GitHub repo
def countfiles(dictfiles, lsttokens, repo):
    ipage = 1  # url page counter
    ct = 0  # token counter

    try:
        # loop though all the commit pages until the last returned empty page
        while True:
            spage = str(ipage)
            commitsUrl = 'https://api.github.com/repos/' + repo + '/commits?page=' + spage + '&per_page=100'
            jsonCommits, ct = github_auth(commitsUrl, lsttokens, ct)

            # break out of the while loop if there are no more commits in the pages
            if len(jsonCommits) == 0:
                break
            # iterate through the list of commits in  spage
            for shaObject in jsonCommits:
                sha = shaObject['sha']
                # For each commit, use the GitHub commit API to extract the files touched by the commit
                shaUrl = 'https://api.github.com/repos/' + repo + '/commits/' + sha
                shaDetails, ct = github_auth(shaUrl, lsttokens, ct)
                filesjson = shaDetails['files']
                for filenameObj in filesjson:
                    filename = filenameObj['filename']

# Get author/date
####################################################################################
                    # Get extension
                    _, ext = os.path.splitext(filename)

                    # Filter for source files: .java', '.cpp', '.kt', '.c', '.cmake'
                    if ext in source_extensions:

                        # Author and date tuple
                        author_date = (
                            shaDetails['commit']['author']['name'], 
                            shaDetails['commit']['author']['date']
                        )
                        if filename not in dictfiles: 
                            # Add the commits for filename
                            dictfiles[filename] = {
                                'count': 0, 
                                'author_dates': []
                            }
                        # Increment count and append the commit data
                        dictfiles[filename]['count'] += 1
                        dictfiles[filename]['author_dates'].append(author_date)
####################################################################################
                                      
            ipage += 1
    except:
        print("Error receiving data")
        exit(0)


# Format author_date
####################################################################################
def format_author_date(tuples): 
    final_format = []

    # Enumerate through the author_date tuples
    for i, (author, datetime) in enumerate (tuples):
        # Remove time, append, and create newlines every 5
        date = datetime.split('T')[0]
        final_format.append(f"{author} ({date})")
        if(i + 1) % 5 == 0: 
            final_format.append("\n")
    return ', '.join(final_format).rstrip("\n")
####################################################################################


# GitHub repo
repo = 'scottyab/rootbeer'
# repo = 'Skyscanner/backpack' # This repo is commit heavy. It takes long to finish executing
# repo = 'k9mail/k-9' # This repo is commit heavy. It takes long to finish executing
# repo = 'mendhak/gpslogger'


# put your tokens here
# Remember to empty the list when going to commit to GitHub.
# Otherwise they will all be reverted and you will have to re-create them
# I would advise to create more than one token for repos with heavy commits
lstTokens = ["faketoken"]

dictfiles = dict()
countfiles(dictfiles, lstTokens, repo)
print('Total number of files: ' + str(len(dictfiles)))

file = repo.split('/')[1]
fileOutput = 'data/file_' + file + '.csv'

# Updated CSV
####################################################################################
# Format the CSV file
rows = ["Filename", "Touches", "Author & Date Touched List"]
fileCSV = open(fileOutput, 'w')
writer = csv.writer(fileCSV)
writer.writerow(rows)
bigcount = None
bigfilename = None

# write the rows from countfile
for filename, info in dictfiles.items():
    count = info['count']
    author_dates = format_author_date(info['author_dates'])
    rows = [filename, count, author_dates] # add values
    writer.writerow(rows)

    if bigcount is None or count > bigcount:
        bigcount = count
        bigfilename = filename
####################################################################################

fileCSV.close()
print('The file ' + bigfilename + ' has been touched ' + str(bigcount) + ' times.')

