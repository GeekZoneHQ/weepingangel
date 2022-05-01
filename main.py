from github import Github
import logging
import dotenv
import os
from datetime import datetime, timedelta

dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO)

GH_ACCESS_TOKEN = os.getenv("GH_ACCESS_TOKEN")
GH_REPOSITORY = os.getenv("GH_REPOSITORY")

gh = Github(GH_ACCESS_TOKEN)
repo = gh.get_repo(GH_REPOSITORY)

NOW_DATETIME = datetime.now()


REMINDER_DAYS = 28
WARNING_DAYS = 56
REMOVE_DAYS = 84

if os.getenv("REMINDER_DAYS"):
    REMINDER_DAYS = os.getenv("REMINDER_DAYS")
if os.getenv("WARNING_DAYS"):
    WARNING_DAYS = os.getenv("WARNING_DAYS")
if os.getenv("REMOVE_DAYS"):
    REMOVE_DAYS = os.getenv("REMOVE_DAYS")


def assignee_message(remove_datetime=None, level="reminder"):
    if level == "reminder":
        reminder_message = (
            "Are you still working on this? Please remember to "
            "regularly share your progress with small comments or commits. If "
            "you are stuck, please don't suffer in silence, "
            "ask for help! Thanks!"
        )
        if os.getenv("reminder_message"):
            reminder_message = os.getenv("reminder_message")
        return reminder_message

    if level == "warning":
        deadline = "soon"
        if remove_datetime is not None:
            deadline = f"before {remove_datetime.strftime('%Y-%m-%d')}"
        warning_message = (
            f"Are you still working on this? "
            f"Please remember to regularly share your progress with "
            f"small comments or commits. If I don't hear from you {deadline} "
            f"I will un-assign this issue so that others can have a go. "
            f"Thanks!"
        )
        if os.getenv("warning_message"):
            warning_message = os.getenv("warning_message")
        return warning_message
    if level == "remove":
        remove_message = (
            "It seems that you aren't working on this issue at the "
            "moment, that's ok! I have unassigned for the time "
            "being you so that others can have a go. If you are "
            "still working on it, please share your progress and "
            "challenges in comment. Thanks!"
        )
        if os.getenv("remove_message"):
            remove_message = os.getenv("remove_message")
        return remove_message
    return None


def get_issue_assignee(issue):
    assignee = issue.assignee
    if assignee is not None:
        return assignee.login
    return None


def get_issue_branches(issue_number):
    branches = []
    for branch in repo.get_branches():
        if issue_number in branch.name:
            branches.append(branch)
    return branches


def get_last_commit_date(branch):
    commits = branch.get_commits()
    return commits[0].commit.committer.date


def get_last_comment_date(issue, user):
    comments = issue.get_comments()
    if not comments:
        return None
    created_at = []
    for comment in comments:
        if comment.user.login == user:
            created_at.append(comment.created_at)
    if not created_at:
        return None
    return max(created_at)


def write_comment(issue, message):
    issue.create_comment(message)


def get_last_activity(issue):
    branches = get_issue_branches(issue.number)
    last_commit_date = get_last_commit_date(branches[0])
    last_comment_date = get_last_comment_date(issue, issue.assignee.login)

    if last_comment_date is None and last_commit_date is None:
        return None
    if last_comment_date is None:
        return last_commit_date
    if last_commit_date is None:
        return last_comment_date
    if last_commit_date > last_comment_date:
        return last_commit_date
    return last_comment_date


def get_remove_datetime(issue):
    return get_last_activity(issue) + timedelta(days=REMOVE_DAYS)


def get_issue_assigned_datetime(issue_number):
    issue = repo.get_issue(issue_number)
    assignee = get_issue_assignee(issue)
    if assignee is None:
        return None
    timeline = issue.get_timeline()
    creation_dates = []
    for node in timeline:
        if node.event == "assigned":
            if node.actor.login == assignee:
                creation_dates.append(node.created_at)
    if not creation_dates:
        return None
    return max(creation_dates)


def check_issues(state):
    for issue in repo.get_issues(state=state):
        if issue.assignees is None:
            logging.info(f"Issue {issue.number} has no assignee, skipping")
            continue
        if issue.pull_request is not None:
            logging.info(f"Issue {issue.number} is a pull request, skipping")
            continue

        last_activity = get_last_activity(issue)
        if not last_activity:
            last_activity = get_issue_assigned_datetime(issue)
        delta = NOW_DATETIME - last_activity
        remove_datetime = get_remove_datetime(issue)

        if delta.days > REMOVE_DAYS:
            logging.info(f"Issue {issue.number} "
                         f"assignee {issue.assignee.login} removed")
            issue.edit(assignee=None)
            write_comment(
                issue,
                assignee_message(
                    remove_datetime=remove_datetime, level="remove"
                ),
            )
            continue
        if delta.days > WARNING_DAYS:
            logging.info(f"Issue {issue.number} warning")
            write_comment(issue, assignee_message(level="warning"))
            continue
        if delta.days > REMINDER_DAYS:
            logging.info(f"Issue {issue.number} reminder")
            write_comment(issue, assignee_message())
            continue


def main():
    check_issues("open")


if __name__ == "__main__":
    main()
