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
import time

from futurehouse_client import FutureHouseClient, JobNames
from futurehouse_client.models import (
    AuthType,
    RuntimeConfig,
    Stage,
    TaskRequest,
)
from ldp.agent import AgentConfig
```

## Client instantiation

Here we use `auth_type=AuthType.API_KEY` to authenticate with the platform.
Please log in to the platform and go to your user settings to get your API key.

```python
client = FutureHouseClient(
    stage=Stage.PROD,
    auth_type=AuthType.API_KEY,
    api_key="your-api-key",
)
```

## Submit a task to an available futurehouse job


In the futurehouse platform, we refer to the deployed combination of agent and environment as a `job`.
Submitting task to a futurehouse job is done by calling the `create_task` method, which receives a `TaskRequest` object.

```python
task_data = TaskRequest(
    name=JobNames.from_string("crow"),
    query="What is the molecule known to have the smallest solubility in water?",
)
client.create_task(task_data)

while client.get_task().status != "success":
    time.sleep(5)
print(f"Task status: {client.get_task().status}")
print(f"Task answer: \n{client.get_task().formatted_answer}")
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
client.create_task(task_data)

while client.get_task().status != "success":
    time.sleep(5)
print(f"Task status: {client.get_task().status}")
print(f"Task answer: \n{client.get_task().formatted_answer}")
```

# Continue a job

The platform allows to ask follow-up questions to the previous job.
To accomplish that, we can use the `runtime_config` to pass the `task_id` of the previous task.

Notice that `create_task` accepts both a `TaskRequest` object and a dictionary with keywords arguments.

```python
task_data = TaskRequest(
    name=JobNames.CROW, query="How many species of birds are there?"
)

task_id = client.create_task(task_data)
while client.get_task().status != "success":
    time.sleep(5)
print(f"First task status: {client.get_task().status}")
print(f"First task answer: \n{client.get_task().formatted_answer}")
```

```python
continued_task_data = {
    "name": JobNames.CROW,
    "query": (
        "From the previous answer, specifically,how many species of crows are there?"
    ),
    "runtime_config": {"continued_task_id": task_id},
}

continued_task_id = client.create_task(continued_task_data)
while client.get_task().status != "success":
    time.sleep(5)
print(f"Continued task status: {client.get_task().status}")
print(f"Continued task answer: \n{client.get_task().formatted_answer}")
```
