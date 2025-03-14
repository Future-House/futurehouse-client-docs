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
from pathlib import Path

from crow_client import CrowClient
from crow_client.models import (
    AuthType,
    CrowDeploymentConfig,
    DockerContainerConfiguration,
    FramePath,
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
    name="job-futurehouse-dummy-env-dev",
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
    name="job-futurehouse-dummy-env-dev",
    query="How many moons does earth have?",
    runtime_config=RuntimeConfig(agent=agent, max_steps=5),
)
client.create_job(job_data)

while client.get_job()["status"] != "success":
    time.sleep(5)
print(client.get_job())
```

## Deploy a Crow
A crow is a deployment of an environment, which will be used to run the agent.
Deploying a crow is done by calling the `create_crow` method, which receives a `CrowDeploymentConfig` object.


```python

frame_paths = [
    FramePath(path="state.pdbs", type="pdb", is_iterable=True),
    FramePath(path="state.single_pdb", type="pdb"),
]

crow = CrowDeploymentConfig(
    path=Path("./envs/dummy_env"),
    environment="dummy_env.env.DummyEnv",
    requires_aviary_internal=False,
    environment_variables={"SAMPLE_ENV_VAR": "sample_val"},
    agent="ldp.agent.SimpleAgent",
    container_config=DockerContainerConfiguration(cpu="1", memory="2Gi"),
    force=True,
    frame_paths=frame_paths,
    task_description="This is a dummy task",
)
client.create_crow(crow)
```

```python
while client.get_build_status()["status"] != "SUCCESS":
    time.sleep(5)
print(client.get_build_status())
```
