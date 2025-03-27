# FutureHouse Platform API Documentation

Documentation and tutorials for `crow-client`, a client for interacting with endpoints of the FutureHouse platform.

> FutureHouse's mascot is the crow. Therefore, some objects are named after the crow as a homage.

<!--TOC-->

- [Installation](#installation)
- [Quickstart](#quickstart)
- [Functionalities](#functionalities)
  - [Stages](#stages)
- [Authentication](#authentication)
- [Job submission](#job-submission)
- [Job retrieval](#job-retrieval)

<!--TOC-->

## Installation

```bash
uv pip install crow-client
```

## Quickstart

```python
from crow_client import CrowClient, JobNames
from crow_client.models import CrowDeploymentConfig
from pathlib import Path
from aviary.core import DummyEnv
import ldp

client = CrowClient(
    stage=Stage.DEV,
    auth_type=AuthType.API_KEY,
    api_key="your_api_key",
)

job_data = {
    "name": JobNames.CROW,
    "query": "Has anyone tested therapeutic exerkines in humans or NHPs?"
}

job_run_id = client.create_job(job_data)

job_status = client.get_job(job_run_id)
```

A quickstart example can be found in the [crow_client_notebook.ipynb](./docs/crow_client_notebook.ipynb) file, where we show how to submit and retrieve a job_run, pass runtime configuration to the agent, and deploy a new job.

## Functionalities

Crow-client implements a RestClient (called `CrowClient`) with the following functionalities:

- [Authentication](#authtype): `auth_client`
- [Job submission](#job-submission): `create_job(JobRequest)`
- [Job status](#job-status): `get_job(job_id)`

To create a `CrowClient`, you need to pass the following parameters:
| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| stage | Stage | Stage.DEV | Where to submit the job will be deployed/ran? |
| organization | str \| None | None | Which organization to use? |
| auth_type | AuthType | AuthType.API_KEY | Which authentication method to use? |
| api_key | str \| None | None | The API key to use for authentication, if using auth_type=AuthType.API_KEY. |

To instantiate a Client, we can use the following code:

```python
from crow_client import CrowClient
from crow_client.models import Stage, AuthType

client = CrowClient(
    stage=Stage.DEV,
    organization="your_organization",
    auth_type=AuthType.API_KEY,
    api_key="your_api_key",
)
```

### Stages

The stage is where your job will be deployed or submitted. This parameter can be one of the following:
| Name | Description |
| --- | --- |
| Stage.DEV | Development environment at https://dev.api.platform.futurehouse.org |
| Stage.PROD | Production environment at https://api.platform.futurehouse.org |

## Authentication

In order to use the `CrowClient`, you need to authenticate yourself. Authentication is done by providing an API key, which can be obtained directly from your [profile page in the FutureHouse platform](https://platform.futurehouse.org/profile).

## Job submission

`CrowClient` can be used to submit jobs to the FutureHouse platform. Using a `CrowClient` instance, you can submit jobs to the platform by calling the `create_job` method, which receives a `JobRequest` (or a dictionary with `kwargs`) and returns the job id.
Aiming to make the submission of jobs as simple as possible, we have created a `JobNames` enum that contains the available job types.

The available supported jobs are:
| Alias | Job Name | Task type | Description |
| --- | --- | --- | --- |
| `JobNames.CROW` | `job-futurehouse-paperqa2` | Fast Search | Ask a question of scientific data sources, and receive a high-accuracy, cited response. Built with [PaperQA2](https://github.com/Future-House/paper-qa). |
| `JobNames.FALCON` | `job-futurehouse-paperqa2-deep` | Deep Search | Use a plethora of sources to deeply research. Receive a detailed, structured report as a response. |
| `JobNames.OWL` | `job-futurehouse-hasanyone` | Precedent Search | Formerly known as HasAnyone, query if anyone has ever done something in science. |
| `JobNames.DUMMY` | `job-futurehouse-dummy` | Dummy Task | This is a dummy task. Mainly for testing purposes. |

Using `JobNames`, the client automatically adapts the job name to the current stage.
The job submission looks like this:

```python
from crow_client import CrowClient, JobNames
from crow_client.models import AuthType, Stage

client = CrowClient(
    stage=Stage.DEV,
    auth_type=AuthType.API_KEY,
    api_key="your_api_key",
)

job_data = {
    "name": JobNames.CROW,
    "query": "Has anyone tested therapeutic exerkines in humans or NHPs?"
}

job_id = client.create_job(job_data)
```

`JobRequest` has the following fields:

| Field          | Type          | Description                                                                                                         |
| -------------- | ------------- | ------------------------------------------------------------------------------------------------------------------- |
| id             | UUID          | Optional job identifier. A UUID will be generated if not provided                                                   |
| name           | str           | Name of the job to execute eg. `job-futurehouse-paperqa2`, or using the `JobNames` for convenience: `JobNames.CROW` |
| query          | str           | Query or task to be executed by the job                                                                             |
| runtime_config | RuntimeConfig | Optional runtime parameters for the job                                                                             |

As we will see in the [Job Deployment section](#job-deployment), we need to pass an agent module for deployment. On runtime, we can pass a `runtime_config` to interact with the agent's configuration.
`runtime_config` can receive a `AgentConfig` object with the desired kwargs. Check the available `AgentConfig` fields in the [LDP documentation](https://github.com/Future-House/ldp/blob/main/src/ldp/agent/agent.py#L87). Besides the `AgentConfig` object, we can also pass `timeout` and `max_steps` to limit the execution time and the number of steps the agent can take.
Other especialised configurations are also available but are outside the scope of this documentation.

## Job retrieval

Once a job is submitted, you can retrieve it by calling the `get_job` method, which receives a job id and returns a `JobResponse` object.

```python
from crow_client import CrowClient
from crow_client.models import AuthType

client = CrowClient(
    auth_type=AuthType.API_KEY,
    api_key="your_api_key",
)

job_id = "job_id"

job_status = client.get_job(job_id)
```

`job_status` contains information about the job. For instance, its `status`, `task`, `environment_name` and `agent_name`, and other fields specific to the job.
