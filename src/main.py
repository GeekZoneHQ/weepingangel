from github import Github
import logging
import dotenv
import os
from datetime import datetime, timedelta

dotenv.load_dotenv()

GH_ACCESS_TOKEN = os.getenv("GH_ACCESS_TOKEN")
GH_REPOSITORY = os.getenv("GH_REPOSITORY")

gh = Github(GH_ACCESS_TOKEN)
repo = gh.get_repo(GH_REPOSITORY)

logging.basicConfig(level=logging.INFO)


def get_action_days():
    actions = ["reminder",
               "warning",
               "remove",
               ]

    base_days = 7 * 4  # 4 weeks

    days = []
    for count, action in enumerate(actions, start=1):
        if not os.getenv(f"{action.upper()}_DAYS"):
            days.append(base_days * count)
            continue
        try:
            days.append(int(os.getenv(f"{action.upper()}_DAYS")))
        except ValueError:
            logging.error(f"get_action_days: {action.upper()}_DAYS "
                          f"must be an integer")
        except Exception as e:
            logging.error(e)

    action_days = {
        "remove": days[2],
        "warning": days[1],
        "reminder": days[0],
    }
    logging.info(f"get_action_days: Action days: {action_days}")
    return action_days


def assignee_message(action_date=None,
                     assignee_login=None,
                     action=None,
                     self_assign_trigger="",
                     ):
    if assignee_login is None:
        return ValueError("assignee_login cannot be None")
    if action is None:
        return ValueError("action cannot be None")
    if action == "reminder":
        reminder_message = (
            "Are you still working on this? Please remember to "
            "regularly share your progress with small comments or commits. If "
            "you are stuck, please don't suffer in silence, "
            "ask for help by logging an issue! Thanks!"
        )
        if os.getenv("reminder_message"):
            reminder_message = os.getenv("reminder_message")
        return f"@{assignee_login} {reminder_message}"

    if action == "warning":
        deadline = "soon"
        if action_date is not None:
            deadline = f"before {action_date.strftime('%Y-%m-%d')}"
        warning_message = (
            f"Are you still working on this? "
            f"Please remember to regularly share your progress with "
            f"small comments or commits. If I don't hear from you {deadline} "
            f"I will un-assign this issue so that others can have a go. "
            f"Thanks!"
        )
        if os.getenv("warning_message"):
            warning_message = os.getenv("warning_message")
        return f"@{assignee_login} {warning_message}"
    if action == "remove":
        self_assign_message = ""
        if self_assign_trigger:
            self_assign_message = (f" and include the `{self_assign_trigger}` "
                                   f"command to re-assign yourself")
        remove_message = (
            f"It seems that you aren't working on this issue at the "
            f"moment, that's ok! I have unassigned it for the time "
            f"being you so that others can have a go. If you are "
            f"still working on it, please share your progress and "
            f"challenges in a comment{self_assign_message}. Thanks!"
        )
        if os.getenv("remove_message"):
            remove_message = os.getenv("remove_message")
        return f"@{assignee_login} {remove_message}"
    logging.error(f"assignee_message: Unknown action: {action}")
    return ValueError(f"Unknown action: {action}")


def get_issue_branches(issue_number):
    branches = []
    for branch in repo.get_branches():
        if str(issue_number) in branch.name:
            branches.append(branch)
    logging.info(f"get_issue_branches: Found branches {branches}")
    return branches


def get_last_commit_date(issue_number):
    branches = get_issue_branches(issue_number)
    commit_dates = []
    for branch in branches:
        commits = repo.get_commits(sha=branch.name)
        commit_date = commits[0].commit.committer.date
        commit_dates.append(commit_date)
        logging.info(f"get_last_commit_date: Last commit date for branch "
                     f"{repo.name}/{branch.name}: {commit_date}")
    if not commit_dates:
        return None
    return max(commit_dates)


def get_last_comment_date(issue, user_login):
    comments = issue.get_comments()
    if not comments:
        return None
    created_at = []
    for comment in comments:
        if comment.user.login == user_login:
            created_at.append(comment.created_at)
    if not created_at:
        return None
    logging.info(f"get_last_comment_date: Issue {issue.number} last comment "
                 f"from {user_login} was at: {max(created_at)}")
    return max(created_at)


def write_comment(issue, message):
    issue.create_comment(message)
    logging.info(f"write_comment: Wrote comment to Issue {issue.number}")
    return 0


def get_last_activity(issue):
    last_commit_date = get_last_commit_date(issue.number)
    last_comment_date = get_last_comment_date(issue, issue.assignee.login)

    if last_comment_date is None and last_commit_date is None:
        return get_issue_assigned_datetime(issue)
    if last_comment_date is None and last_commit_date is not None:
        return last_commit_date
    if last_comment_date is not None and last_commit_date is None:
        return last_comment_date
    if last_comment_date is not None and last_commit_date is not None:
        if last_comment_date < last_commit_date:
            return last_commit_date
    return last_comment_date


def get_issue_assigned_datetime(issue):
    issue = repo.get_issue(number=issue.number)
    assignee = issue.assignee.login
    timeline = issue.get_timeline()
    creation_dates = []
    for page in timeline:
        if page.event == "assigned":
            if assignee == page.raw_data["assignee"]["login"]:
                creation_dates.append(datetime.strptime(page.raw_data["created_at"], "%Y-%m-%dT%H:%M:%SZ"))
    logging.info(f"get_issue_assigned_datetime: Issue {issue.number} "
                 f"assigned to {assignee} at {max(creation_dates)}")
    return max(creation_dates)


def unassign_issue(issue, action):
    if action != "remove":
        return 0
    logging.info(f"unassign_issue: Unassigning issue {issue.number}")
    issue.edit(assignee=None)
    return 0


def check_issues(state):
    action_days = get_action_days()
    now_date = datetime.now().date()
    logging.info(f"check_issues: Checking issues in state {state} "
                 f"on {now_date}")
    for issue in repo.get_issues(state=state):
        if issue.assignee is None or issue.assignees is None:
            logging.info(f"check_issues: Issue {issue.number} "
                         f"has no assignee, skip")
            continue
        if issue.pull_request is not None:
            logging.info(f"check_issues: Issue {issue.number} "
                         f"is a pull request, skip")
            continue

        last_activity_date = get_last_activity(issue).date()
        logging.info(f"check_issues: Issue {issue.number} "
                     f"last activity {last_activity_date}")

        activity_delta = now_date - last_activity_date
        logging.info(
            f"check_issues: Issue {issue.number} "
            f"activity_delta {activity_delta.days} days")

        for key in action_days:
            action_date = (last_activity_date + timedelta(
                days=action_days[key]))
            logging.info(
                f"check_issues: Issue {issue.number} {key} on {action_date}")

            if action_date != now_date:
                continue
            issue.create_comment(assignee_message(action_date=action_date,
                                                  assignee_login=issue.assignee.login,
                                                  action=key))
            unassign_issue(issue=issue,
                           action=key)


def main():
    logging.info("main: Starting. Don't turn your back, don't look away and "
                 "don't blink. Good luck.")
    check_issues("open")
    logging.info("main: Done. It's been good though, hasn't it?")


if __name__ == "__main__":
    main()

