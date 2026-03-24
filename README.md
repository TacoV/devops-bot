This library creates an Azure DevOps assistant bot that helps teams maintain the work items board. Design: A **local DevOps assistant bot**: a Python service + API clients + optional LLM layer. In Docker.

There's additional 

It does (or will do):

* Perform maintenance and janitorial tasks
* Adhere to specific team agreements on the desired structure of the bot
* Add comments or update tickets where needed
* Concern itself with hierarchy, including states that do or do not make sense
* Take into accounts sprints (iterations)
* Give advice about how to improve it's own work
* Connect to some LLM API to get summaries, advice, etc
* Work on cron or manually (for now)

It doesn't:

* Connect to Teams, mail, or Slack.
* Concern itself with builds
* Concern itself with multiple projects
* Concern itself with the repository

Things that sound good:

* Health checks
* Work item hygiene
* Auto-fixes
* Add `typer` for beautiful CLI
* Markdown reports
* Auto-discover tasks from the tasks folder

It should be able at some point to work slightly agentic - form an idea, retrieve work items in WIQL as desired, draw conclusions, give the feedback.