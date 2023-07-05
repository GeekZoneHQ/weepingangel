# Weeping Angel

The Weeping Angel is an extremely powerful species of quantum-locked humanoid. This particular specimen was inadvertently banished to the Internet by The Doctor, so now gleans energy by removing a victim from their GitHub issue, rather than by removing their head from their body. The only way to thwart their "merciful" nature is to contribute to your GitHub issues frequently.

# Alternative to Stale Bot

The [GitHub stale bot](https://github.com/marketplace/stale) is a bot that automatically closes old issues. It is very popular, however, implies that only new ideas are important. We feel that a triage approach is more appropriate.

For example, say you went to a hospital with a broken arm. You might be told that the Doctor was unable to see you right now and that you would wait for them in the waiting room. Some hours pass and the secretary comes over and tells you that your case has been closed as you have been in the waiting room for too long. Just as you go to head home, you notice someone with a paper cut being seen by the Doctor!

In that situation, you would probably get a little miffed, and understandably so. It is the same for our community ideas. We believe that our stakeholders contributions are all valuable and important. Just because we have not had the capacity to build a particular feature yet, does not mean it is not worth doing at all. [Old wine is good wine](https://youtu.be/YAQ4BD9fHvs).

# Why is this important?
Ensures that
- all ideas are
    - reviewed.
    - considered.
    - implemented as soon as possible.
- the status of each issue is clearly and asynchronously communicated.

If nobody is currently working on an issue, contributors should be given the freedom to crack on with it.

# What the Weeping Angel Does
## Nutshell

Unassigns assignees from an issue if they have not contributed to it for a while.

## What it does

Weeping Angel monitors each assigned issue to discern whether you are looking at it. This is done by calculating the number of days since the issue received a comment or a commit on a branch with a matching issue number.

- IF issue is not assigned
    <br /> THEN return
- IF issue is a PR
    <br /> THEN return
- IF issue has linked PR
    <br /> THEN return
- IF issue assignee has not looked for `reminder_days` days 
  <br />THEN Weeping Angel to post a comment in the issue
  > @[assignee] `reminder_message`
- IF issue assignee has not looked for `warning_days` days 
  <br />THEN Weeping Angel posts a comment in the issue
  > @[assignee] `warning_message`
- if issue assignee has not looked for `remove_days` days 
  <br />THEN Weeping Angel posts a comment in the issue
  > @[assignee] `remove_message`

## Running

Weeping Angel is designed to run *once per day* via cron. It **must** be run every day and **only** once.


## Inputs
The inputs and their default values are:
- `reminder_days` = 28 days (4 weeks)
- `warning_days` = 56 days (8 weeks)
- `remove_days` = 84 days (12 weeks)
- `reminder_message` = <br>
  > Are you still working on this? Please remember to regularly share your progress with a brief comment. If you are stuck, please don't suffer in silence, ask for help by logging an issue! Thanks!
- `warning_message` = <br>
  > Are you still working on this? Please remember to regularly share your progress with a brief comment. If I don't hear from you before `calculated-remove-date` I will un-assign this issue so that others can have a go. Thanks!
- `remove_message` = <br>
  > It seems that you aren't working on this issue at the moment, that's ok! I have unassigned for the time being you so that others can have a go. If you are still working on it, please share your progress and challenges in comment. Thanks!
- `self_assign_trigger` = `None`<br>
  The string that you are using to trigger [self assignment](https://github.com/bdougie/take-action).

## Action YML

### Suggested

If you are happy with the defaults, you can use the suggested `.github/workflows/weepingangel.yml` file.

```yaml
name: Weeping Angel
on:
  schedule:
    - cron:  '0 10 * * *'
jobs:
  build:
    runs-on: ubuntu-latest
     
    steps:
    - name: Run Weeping Angel action
      uses: GeekZoneHQ/weepingangel@latest
      env:
        GH_ACCESS_TOKEN: ${{ secrets.GH_ACCESS_TOKEN }}
        GH_REPOSITORY: ${{ github.repository }}
```

### Custom

If you want to provide your own values, you can use the custom yml file.

```yaml
name: Weeping Angel
on:
  schedule:
    - cron:  '0 10 * * *'
jobs:
  build:
    runs-on: ubuntu-latest
 
    steps:
    - name: Run Weeping Angel action
      uses: GeekZoneHQ/weepingangel@main
      env:
        GH_ACCESS_TOKEN: ${{ secrets.GH_ACCESS_TOKEN }}
        GH_REPOSITORY: ${{ github.repository }}
      with:
        reminder_days: 1000
        warning_days: 2000
        remove_days: 3000
        reminder_message: Your amazing custom reminder message
        warning_message: Your amazing custom warning message
        remove_message: Your amazing custom remove message
        self_assign: /mine
```



# Recommended accompaniment

To ensure that issues are triaged correctly, we recommend using the Weeping Angel in conjunction with these other GitHub actions.
- [Eisenhower](https://github.com/GeekZoneHQ/eisenhower)
 <br />Priority Labeler which ensures all your tickets are prioritized, preventing decision fatigue.
- [Take Action](https://github.com/bdougie/take-action)
 <br />Allow anyone to assign themselves to an issue using a comment.