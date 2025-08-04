---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.7
  kernelspec:
    display_name: .venv
    language: python
    name: python3
---

# FutureHouse platform client usage example

```python
from futurehouse_client import FutureHouseClient, JobNames
from futurehouse_client.models import (
    RuntimeConfig,
    TaskRequest,
)
from ldp.agent import AgentConfig
```

## Client instantiation

Here we use `auth_type=AuthType.API_KEY` to authenticate with the platform.
Please log in to the platform and go to your user settings to get your API key.

```python
client = FutureHouseClient(
    api_key="your-api-key",
)
```

## Submit a task to an available futurehouse job


In the futurehouse platform, we refer to the deployed combination of agent and environment as a `job`.
Submitting task to a futurehouse job is done by calling the `create_task` method, which receives a `TaskRequest` object.

```python
task_data = TaskRequest(
    name=JobNames.from_string("crow"),
    query="What is the molecule known to have the greatest solubility in water?",
)
responses = client.run_tasks_until_done(task_data)
task_response = responses[0]

print(f"Job status: {task_response.status}")
print(f"Job answer: \n{task_response.formatted_answer}")
```

You can also pass a `runtime_config` to the `create_task` method, which will be used to configure the agent on runtime.
Here, we will define a agent configuration and include it in the `TaskRequest`. This agent is used to decide the next action to take.
We will also use the `max_steps` parameter to limit the number of steps the agent will take.

```python
agent = AgentConfig(
    agent_type="SimpleAgent",
    agent_kwargs={
        "model": "gpt-4o",
        "temperature": 0.0,
    },
)
task_data = TaskRequest(
    name=JobNames.CROW,
    query="How many moons does earth have?",
    runtime_config=RuntimeConfig(agent=agent, max_steps=10),
)
responses = client.run_tasks_until_done(task_data)
task_response = responses[0]

print(f"Job status: {task_response.status}")
print(f"Job answer: \n{task_response.formatted_answer}")
```

# Continue a job

The platform allows to ask follow-up questions to the previous job.
To accomplish that, we can use the `runtime_config` to pass the `task_id` of the previous task.

Notice that `create_task` accepts both a `TaskRequest` object and a dictionary with keywords arguments.

```python
task_data = TaskRequest(
    name=JobNames.CROW, query="How many species of birds are there?"
)

responses = client.run_tasks_until_done(task_data)
task_response = responses[0]

print(f"First job status: {task_response.status}")
print(f"First job answer: \n{task_response.formatted_answer}")
```

```python
continued_job_data = {
    "name": JobNames.CROW,
    "query": (
        "From the previous answer, specifically,how many species of crows are there?"
    ),
    "runtime_config": {"continued_job_id": task_response.task_id},
}

responses = client.run_tasks_until_done(continued_job_data)
continued_task_response = responses[0]


print(f"Continued job status: {continued_task_response.status}")
print(f"Continued job answer: \n{continued_task_response.formatted_answer}")
```
