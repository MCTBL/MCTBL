import requests as req
import json
from github import Github, Auth
import re
import os
import logging as logger
import time

waka_key = os.environ.get("WAKA_KEY")
gh_token = os.environ.get("GH_TOKEN")
repo_name = os.environ.get("REPO_NAME")
branch_name = os.environ.get("BRANCH_NAME", "main").strip()
start_mark = os.environ.get("START_MARK", "<!--START_SECTION:waka-->").strip()
end_mark = os.environ.get("END_MARK", "<!--END_SECTION:waka-->").strip()


def check_env() -> bool:
    if len(waka_key) == 0 or len(gh_token) == 0 or len(repo_name) == 0:
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
    tempStr = "Update Time:       " + \
        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + \
        "\nTotal Code Time: " + \
        data["data"]["human_readable_total_including_other_language"] + "\n"

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
            waka_url = "https://wakatime.com/api/v1/users/current/stats/last_7_days"
            headers = {
                'Authorization': "Basic %s" % waka_key.strip(),
                'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
            }
            connect = Github(auth=Auth.Token(gh_token.strip()))
            repo = connect.get_user().get_repo(repo_name.strip())
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
