# Weeping Angel

The Weeping Angel is an extremely powerful species of quantum-locked humanoid. This particular form of the species gains energy by removing a victim from their GitHub issue, rather than by removing their head from their body. The only way to thwart their "merciful" nature is to contribute to the issue frequently.

# Alternative to Stale Bot

The [GitHub stale bot](https://github.com/marketplace/stale) is a bot that automatically closes old issues. It is very popular, however, implies that only new ideas are important. We feel that a triage approach is more appropriate.

For example, say you went to a hospital with a broken arm. You might be told that the Doctor was unable to see you right now and that you would wait for them in the waiting room. Some hours pass and the secretary comes over and tells you that your case has been closed as you have been in the waiting room for too long. Just as you go to head home, you notice someone with a paper cut being seen by the Doctor!

In that situation, you would probably get a little miffed, and understandably so. It is the same for our community ideas. We believe that our stakeholders contributions are all valuable and important. Just because we have not been able to get around to building a particular feature yet, does not mean it is not worth doing at all.

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

## Details

Weeping Angel monitors each assigned issue to discern whether you are looking at it. This is done by calculating the number of days since the issue received a comment or a commit on a branch with a matching issue number.

- IF issue is not assigned
    <br /> THEN return
- IF issue has linked PR
    <br /> THEN return
- IF issue assignee has not looked for 4 weeks 
  <br />THEN Weeping Angel to post a comment in the issue
  > @[assignee] Are you still working on this? Please remember to regularly share your progress with a brief comment. If you are stuck, please don't suffer in silence, ask for help! Thanks!
- IF issue assignee has not looked for 6 weeks
  <br />THEN Weeping Angel posts a comment in the issue
  > @[assignee] Are you still working on this? Please remember to regularly share your progress with a brief comment. If I don't hear from you before `date` I will un-assign this issue so that others can have a go. Thanks!
- if issue assignee has not looked for 8 weeks
  <br />THEN Weeping Angel posts a comment in the issue
  > @[assignee] It seems that you aren't working on this issue at the moment, that's ok! I have unassigned you so that others can have a go. If you are still working on it, please share your progress and challenges in comment and include the command `!mine` to reassign yourself. Thanks!
 


# Recommended accompaniment

To ensure that issues are triaged correctly, we recommend using the Weeping Angel in conjunction with our
- [Eisenhower Priority Labeler](https://github.com/GeekZoneHQ/eisenhower)
- [This One Is Mine](https://github.com/GeekZoneHQ/thisoneismine)