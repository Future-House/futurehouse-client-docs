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

from crow_client import CrowClient, JobNames
from crow_client.models import (
    AuthType,
    JobRequest,
    RuntimeConfig,
    Stage,
)
from ldp.agent import AgentConfig
```

## Client instantiation

Here we use `auth_type=AuthType.API_KEY` to authenticate with the platform.
Please log in to the platform and go to your user settings to get your API key.

```python
client = CrowClient(
    stage=Stage.PROD,
    auth_type=AuthType.API_KEY,
    api_key="your-api-key",
)
```

## Submit a job


Submitting jobs is done by calling the `create_job` method, which receives a `JobRequest` object.

```python
job_data = JobRequest(
    name=JobNames.from_string("crow"),
    query="What is the molecule known to have the smallest solubility in water?",
)
client.create_job(job_data)

while client.get_job().status != "success":
    time.sleep(5)
print(f"Job status: {client.get_job().status}")
print(f"Job answer: \n{client.get_job().formatted_answer}")
```

You can also pass a `runtime_config` to the job, which will be used to configure the agent on runtime.
Here, we will define a agent configuration and pass it to the job. This agent is used to decide the next action to take.
We will also use the `max_steps` parameter to limit the number of steps the agent will take.

```python
agent = AgentConfig(
    agent_type="SimpleAgent",
    agent_kwargs={
        "model": "gpt-4o",
        "temperature": 0.0,
    },
)
job_data = JobRequest(
    name=JobNames.CROW,
    query="How many moons does earth have?",
    runtime_config=RuntimeConfig(agent=agent, max_steps=10),
)
client.create_job(job_data)

while client.get_job().status != "success":
    time.sleep(5)
print(f"Job status: {client.get_job().status}")
print(f"Job answer: \n{client.get_job().formatted_answer}")
```

# Continue a job

The platform allows to keep asking follow-up questions to the previous job.
To accomplish that, we can use the `runtime_config` to pass the `job_id` of the previous job.

Notice that `create_job` accepts both a `JobRequest` object and a dictionary with keywords arguments.

```python
job_data = JobRequest(name=JobNames.CROW, query="How many species of birds are there?")

job_id = client.create_job(job_data)
while client.get_job().status != "success":
    time.sleep(5)
print(f"First job status: {client.get_job().status}")
print(f"First job answer: \n{client.get_job().formatted_answer}")
```

```python
continued_job_data = {
    "name": JobNames.CROW,
    "query": (
        "From the previous answer, specifically,how many species of crows are there?"
    ),
    "runtime_config": {"continued_job_id": job_id},
}

continued_job_id = client.create_job(continued_job_data)
while client.get_job().status != "success":
    time.sleep(5)
print(f"Continued job status: {client.get_job().status}")
print(f"Continued job answer: \n{client.get_job().formatted_answer}")
```
