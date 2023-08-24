import os
file_to_upload = 'benchmark/24-08-23_13-39-20/'

folder_path = "results/"
csv_file = 'miner_benchmark.csv'

file_to_upload += csv_file

folder_in_repo = '/home/kunj/benchmark_files'

access_token = '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'

from github import Github
g = Github("Kunj-2206", "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")

repo = g.get_user().get_repo('NIValidatorEndpoint')
all_files = []
contents = repo.get_contents("")
while contents:
    file_content = contents.pop(0)
    if file_content.type == "dir":
        contents.extend(repo.get_contents(file_content.path))
    else:
        file = file_content
        all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))

with open(os.path.join(file_to_upload, csv_file), 'r') as file:
    content = file.read()

# Upload to github
git_prefix = 'benchmark_files/'
git_file = git_prefix + 'Miner_Benchmark.csv'
if git_file in all_files:
    contents = repo.get_contents(git_file)
    repo.update_file(contents.path, "committing files", content, contents.sha, branch="master")
    print(git_file + ' UPDATED')
else:
    repo.create_file(git_file, "committing files", content, branch="master")
    print(git_file + ' CREATED')