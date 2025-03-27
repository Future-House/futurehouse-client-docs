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

# Crow Client usage example

```python
import time

from crow_client import CrowClient
from crow_client.clients import JobNames
from crow_client.models import (
    AuthType,
    JobRequest,
    RuntimeConfig,
    Stage,
)
from ldp.agent import AgentConfig
```

## Client instantiation

```python
client = CrowClient(stage=Stage.DEV, auth_type=AuthType.GOOGLE)
```

## Submit a job


Submitting jobs is done by calling the `create_job` method, which receives a `JobRequest` object.

```python
job_data = JobRequest(
    name=JobNames.from_string("dummy"),
    query="How many moons does earth have?",
)
client.create_job(job_data)

while client.get_job()["status"] != "success":
    time.sleep(5)
print(client.get_job())
```

You can also pass a `runtime_config` to the job, which will be used to configure the agent on runtime.

```python
agent = AgentConfig(
    agent_type="ReActAgent",
    agent_kwargs={
        "model": "gpt-4o-mini",
        "temperature": 0.0,
    },
)
job_data = JobRequest(
    name=JobNames.DUMMY,
    query="How many moons does earth have?",
    runtime_config=RuntimeConfig(agent=agent, max_steps=5),
)
client.create_job(job_data)

while client.get_job()["status"] != "success":
    time.sleep(5)
print(client.get_job())
```
