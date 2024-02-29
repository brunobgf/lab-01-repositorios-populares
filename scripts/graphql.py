import requests
import pandas as pd
from datetime import datetime
import os
import dotenv
import json
import os

def run_query(query, headers):
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, request.text))


def time_since_last_update(last_update_date):
    current_date = datetime.utcnow()

    last_update_date = datetime.strptime(last_update_date, '%Y-%m-%dT%H:%M:%SZ')

    difference = current_date - last_update_date

    days = difference.days
    seconds = difference.seconds

    elapsed_days = days
    elapsed_hours = seconds // 3600
    elapsed_minutes = (seconds % 3600) // 60
    elapsed_seconds = seconds % 60

    return f'{elapsed_days} days {elapsed_hours} hours {elapsed_minutes} minutes {elapsed_seconds} seconds'


def calculate_age(date_of_birth):
    current_date = datetime.utcnow()

    date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%dT%H:%M:%SZ')

    difference = current_date - date_of_birth

    age = difference.days // 365

    return age

index = 1
data = []
end_cursor = "null"
num_repos = 1000
while len(data) < num_repos:
  query = '''{
    search (
          query: "stars:>20000"
          type: REPOSITORY
          first: 25
          after: ''' + end_cursor + '''
        ) {
          pageInfo {
            endCursor
            hasNextPage
          }
          edges {
            node {
              ... on Repository {
                nameWithOwner
                stargazerCount
                url
                createdAt
                updatedAt
                primaryLanguage {
                  name
                }
                pullRequests(states: MERGED) {
                  totalCount
                }
                total_issues:issues {
                  totalCount
                }
                closed_issues:issues(states:CLOSED) {
                  totalCount
                }
                releases {
                  totalCount
                }
              }
            }
          }
        }
  }
  '''
  dotenv.load_dotenv()
  headers = {"Authorization": f"Bearer {os.environ['API_TOKEN']}"}

  # print(json.dumps(run_query(query, headers), indent=6))
  # input()

  result = run_query(query, headers)["data"]["search"]
  end_cursor = "\"" + result["pageInfo"]["endCursor"] + "\""
  repositories = []
  repositories.extend(list(map(lambda x: x['node'], result['edges'])))

  for repo in repositories:
    primary_language_name = None
    if repo['primaryLanguage'] is not None and repo['primaryLanguage']['name'] is not None:
      primary_language_name = repo['primaryLanguage']['name']

    issues_reason = None
    if repo['closed_issues']['totalCount'] > 0 and repo['total_issues']['totalCount'] > 0:
      issues_reason = repo['closed_issues']['totalCount'] / repo['total_issues']['totalCount']

    total_releases = None
    if repo['releases']['totalCount'] > 0:
      total_releases = repo['releases']['totalCount']

    data.append({
      'name': repo['nameWithOwner'].split('/')[1],
      'owner': repo['nameWithOwner'].split('/')[0],
      'url': repo['url'],
      'stars': repo['stargazerCount'],
      'created_at': repo['createdAt'],
      'updated_at': repo['updatedAt'],
      'age': calculate_age(repo['createdAt']),
      'last_update': time_since_last_update(repo['updatedAt']),
      'primary_language': primary_language_name,
      'number_pr_accepted': repo['pullRequests']['totalCount'],
      'issues_reason': issues_reason,
      'total_releases': total_releases,
      'index': index
    })
    index += 1

print(json.dumps(data, indent=1))

df = pd.DataFrame(data=data)
# recs = df.to_records(index=False)

# Save to CSV
if not os.path.exists('./output_csv_repos'):
  os.mkdir('./output_csv_repos')

df.to_csv('./output_csv_repos/repos.csv', index=False)
