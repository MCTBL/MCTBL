import requests as req
import json
from github import Github, Auth
import re
import os
import logging as logger

waka_key = os.getenv("WAKA_KEY").strip()
gh_token = os.getenv("GH_TOKEN").strip()
repo_name = os.getenv("REPO_NAME").strip()
branch_name = os.getenv("BRANCH_NAME").strip()
start_mark = os.getenv("START_MARK").strip()
end_mark = os.getenv("END_MARK").strip()

waka_url = "https://wakatime.com/api/v1/users/current/stats/last_7_days"
headers = {
    'Authorization': "Basic %s" % waka_key,
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
}


def check_env() -> bool:
    if len(start_mark) == 0:
        start_mark = "<!--START_SECTION:waka-->"
    if len(end_mark) == 0:
        end_mark = "<!--END_SECTION:waka-->"
    if len(branch_name) == 0:
        branch_name = "main"
    if len(waka_key) or len(gh_token) or len(repo_name) == 0:
        return False
    else:
        return True


def waka_str():
    response = req.request("GET", waka_url, headers=headers)
    data = json.loads(response.text)
    temp_list = []
    for i in data["data"]["languages"]:
        temp_list.append([i["name"], i["percent"], i["text"]])
    num = 20
    tempStr = "Total Code Time: " + \
        data["data"]["human_readable_total_including_other_language"] + "\n\n"

    for l in temp_list:
        strBar = ""
        for i in range(num):
            if i <= int(l[1] / (100 / num)):
                strBar += ">"
            else:
                strBar += "="
        tempStr += (f"{l[0]: <17}" + f"{l[2]: <16}" +
                    f"{strBar}  " + f"{l[1]:.2f}".zfill(5) + " %" + "\n")

    return tempStr


def get_gh(repo):
    content = repo.get_contents("/README.md")
    return content


if __name__ == "__main__":

    if not check_env():
        logger.warning("some env is necessary")
    else:
        try:
            connect = Github(auth=Auth.Token(gh_token))
            repo = connect.get_user().get_repo(repo_name)
            readme_content = get_gh(repo)

            waka = waka_str()

            old_readme = str(readme_content.decoded_content, "utf8")
            readme_splits = re.split(
                "(<!--START_SECTION:waka-->|<!--END_SECTION:waka-->)+", old_readme)
            readme_splits[2] = "\n``` rust\n" + waka + "```\n"
            new_readme = "".join(readme_splits)

            repo.update_file(readme_content.path, message="weekly update README.md",
                             content=new_readme, sha=readme_content.sha, branch=branch_name)
        except Exception as e:
            logger.warning(e)
