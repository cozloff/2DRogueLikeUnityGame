import json
import requests
import os

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np 

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
def scatter_data(dictfiles, lsttokens, repo):
    ipage = 1  # url page counter
    ct = 0  # token counter
    earliest = datetime.max # earliest week
    dates = [] # List of weeks 
    files = {} # List of files

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

# Generate scatterdata
####################################################################################
                    # Get extension
                    _, ext = os.path.splitext(filename)

                    # Filter for source files: .java', '.cpp', '.kt', '.c', '.cmake'
                    if ext in source_extensions:
                        # Append the formatted dates and get the author
                        date_str = shaDetails['commit']['author']['date']
                        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                        dates.append(date)
                        author = shaDetails['commit']['author']['name']

                        if filename not in files:
                            files[filename] = []
                        
                        # Append the date and author per file
                        files[filename].append({'week': date, 'author': author})

            ipage += 1

        # Find the earliest date
        earliest = min(dates)

        # Convert dates into week numbers relative to the earliest date
        for filename, commits in files.items():
            for commit in commits:
                commit['week'] = (commit['week'] - earliest).days // 7
                if filename not in dictfiles:
                    dictfiles[filename] = {
                        'weeks': [],
                        'authors': []
                    }
                
                # Add week number and authors for the scatterplot
                dictfiles[filename]['weeks'].append(commit['week'])
                dictfiles[filename]['authors'].append(commit['author'])
####################################################################################
        
    except:
        print("Error receiving data")
        exit(0)

# Generate scatterplot
####################################################################################
def generate_scatter_plot(dictfiles):
    # Get all unique authors
    authors = set(author for data in dictfiles.values() for author in data['authors'])

    # Generate a color assignment for each author
    color_ast = plt.cm.rainbow(np.linspace(0, 1, len(authors)))
    author_color_ast = {author: color for author, color in zip(authors, color_ast)}

    plt.figure(figsize=(10, 6))

    # Plot commits into scatter plot
    for i, data in enumerate(dictfiles.values()):
        for week, author in zip(data['weeks'], data['authors']):
            plt.scatter(i, week, color=author_color_ast[author])

    plt.xlabel('files')
    plt.ylabel('weeks')

    # Save the scatterplot to data folder and then show it
    scatter_filename = os.path.join('data', 'scatter_plot.png')
    plt.savefig(scatter_filename)
    plt.show()
    plt.close()

    # Create a separate figure for the legend
    plt.figure(figsize=(8, 6))
    for author, color in author_color_ast.items():
        plt.plot([], [], color=color, label=author)

    # Save the legend to data 
    plt.legend(loc='center')
    legend_filename = os.path.join('data', 'legend.png')
    plt.savefig(legend_filename)
    plt.close()
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
scatter_data(dictfiles, lstTokens, repo)
generate_scatter_plot(dictfiles)



