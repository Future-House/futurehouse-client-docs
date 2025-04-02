# FutureHouse Platform API Documentation

Documentation and tutorials for futurehouse-client, a client for interacting with endpoints of the FutureHouse platform.

> FutureHouse's mascot is the crow. Therefore, some objects are named after the crow as a homage.

<!--TOC-->

- [Installation](#installation)
- [Quickstart](#quickstart)
- [Functionalities](#functionalities)
  - [Stages](#stages)
- [Authentication](#authentication)
- [Task submission](#task-submission)
- [Task Continuation](#task-continuation)
- [Task retrieval](#task-retrieval)

<!--TOC-->

## Installation

```bash
uv pip install futurehouse-client
```

## Quickstart

```python
from futurehouse_client import FutureHouseClient, JobNames
from pathlib import Path
from aviary.core import DummyEnv
import ldp

client = FutureHouseClient(
    stage=Stage.PROD,
    auth_type=AuthType.API_KEY,
    api_key="your_api_key",
)

task_data = {
    "name": JobNames.CROW,
    "query": "Has anyone tested therapeutic exerkines in humans or NHPs?"
}

task_run_id = client.create_task(task_data)

task_status = client.get_task(task_run_id)
```

A quickstart example can be found in the [client_notebook.ipynb](./docs/client_notebook.ipynb) file, where we show how to submit and retrieve a job task, pass runtime configuration to the agent, and ask follow-up questions to the previous job.

## Functionalities

FutureHouse client implements a RestClient (called `FutureHouseClient`) with the following functionalities:

- [Authentication](#authtype): `auth_client`
- [Task submission](#task-submission): `create_task(TaskRequest)`
- [Task status](#task-status): `get_task(task_id)`

To create a `FutureHouseClient`, you need to pass the following parameters:
| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| stage | Stage | Stage.DEV | Where the job will be submitted? |
| organization | str \| None | None | Which organization to use? |
| auth_type | AuthType | AuthType.API_KEY | Which authentication method to use? |
| api_key | str \| None | None | The API key to use for authentication, if using auth_type=AuthType.API_KEY. |

To instantiate a Client, we can use the following code:

```python
from futurehouse_client import FutureHouseClient
from futurehouse_client.models import Stage, AuthType

client = FutureHouseClient(
    stage=Stage.PROD,
    organization="your_organization",
    auth_type=AuthType.API_KEY,
    api_key="your_api_key",
)
```

### Stages

The stage is where your job will be submitted. This parameter can be one of the following:
| Name | Description |
| --- | --- |
| Stage.DEV | Development environment at https://dev.api.platform.futurehouse.org |
| Stage.PROD | Production environment at https://api.platform.futurehouse.org |

## Authentication

In order to use the `FutureHouseClient`, you need to authenticate yourself. Authentication is done by providing an API key, which can be obtained directly from your [profile page in the FutureHouse platform](https://platform.futurehouse.org/profile).

## Task submission

In the futurehouse platform, we define the deployed combination of an agent and an environment as a `job`. To invoke a job, we need to submit a `task` (also called a `query`) to it.
`FutureHouseClient` can be used to submit tasks/queries to available jobs in the FutureHouse platform. Using a `FutureHouseClient` instance, you can submit tasks to the platform by calling the `create_task` method, which receives a `TaskRequest` (or a dictionary with `kwargs`) and returns the task id.
Aiming to make the submission of tasks as simple as possible, we have created a `JobNames` `enum` that contains the available task types.

The available supported jobs are:
| Alias | Job Name | Task type | Description |
| --- | --- | --- | --- |
| `JobNames.CROW` | `job-futurehouse-paperqa2` | Fast Search | Ask a question of scientific data sources, and receive a high-accuracy, cited response. Built with [PaperQA2](https://github.com/Future-House/paper-qa). |
| `JobNames.FALCON` | `job-futurehouse-paperqa2-deep` | Deep Search | Use a plethora of sources to deeply research. Receive a detailed, structured report as a response. |
| `JobNames.OWL` | `job-futurehouse-hasanyone` | Precedent Search | Formerly known as HasAnyone, query if anyone has ever done something in science. |
| `JobNames.DUMMY` | `job-futurehouse-dummy` | Dummy Task | This is a dummy task. Mainly for testing purposes. |

Using `JobNames`, the client automatically adapts the job name to the current stage.
The task submission looks like this:

```python
from futurehouse_client import FutureHouseClient, JobNames
from futurehouse_client.models import AuthType, Stage

client = FutureHouseClient(
    stage=Stage.PROD,
    auth_type=AuthType.API_KEY,
    api_key="your_api_key",
)

task_data = {
    "name": JobNames.CROW,
    "query": "Has anyone tested therapeutic exerkines in humans or NHPs?"
}

task_id = client.create_task(task_data)
```

`TaskRequest` has the following fields:

| Field          | Type          | Description                                                                                                         |
| -------------- | ------------- | ------------------------------------------------------------------------------------------------------------------- |
| id             | UUID          | Optional job identifier. A UUID will be generated if not provided                                                   |
| name           | str           | Name of the job to execute eg. `job-futurehouse-paperqa2`, or using the `JobNames` for convenience: `JobNames.CROW` |
| query          | str           | Query or task to be executed by the job                                                                             |
| runtime_config | RuntimeConfig | Optional runtime parameters for the job                                                                             |

`runtime_config` can receive a `AgentConfig` object with the desired kwargs. Check the available `AgentConfig` fields in the [LDP documentation](https://github.com/Future-House/ldp/blob/main/src/ldp/agent/agent.py#L87). Besides the `AgentConfig` object, we can also pass `timeout` and `max_steps` to limit the execution time and the number of steps the agent can take.
Other especialised configurations are also available but are outside the scope of this documentation.

## Task Continuation

Once a task is submitted and the answer is returned, FutureHouse platform allow you to ask follow-up questions to the previous task.
It is also possible through the platform API.
To accomplish that, we can use the `runtime_config` we discussed in the [Task submission](#task-submission) section.

```python
from futurehouse_client import FutureHouseClient, JobNames
from futurehouse_client.models import AuthType, Stage

client = FutureHouseClient(
    stage=Stage.PROD,
    auth_type=AuthType.API_KEY,
    api_key="your_api_key",
)

task_data = {
    "name": JobNames.CROW,
    "query": "How many species of birds are there?"
}

task_id = client.create_task(task_data)

continued_task_data = {
    "name": JobNames.CROW,
    "query": "From the previous answer, specifically,how many species of crows are there?",
    "runtime_config": {
        "continued_task_id": task_id
    }
}

continued_task_id = client.create_task(continued_task_data)
```

## Task retrieval

Once a task is submitted, you can retrieve it by calling the `get_task` method, which receives a task id and returns a `TaskResponse` object.

```python
from futurehouse_client import FutureHouseClient
from futurehouse_client.models import AuthType

client = FutureHouseClient(
    stage=Stage.PROD,
    auth_type=AuthType.API_KEY,
    api_key="your_api_key",
)

task_id = "task_id"

task_status = client.get_task(task_id)
```

`task_status` contains information about the task. For instance, its `status`, `task`, `environment_name` and `agent_name`, and other fields specific to the job.
