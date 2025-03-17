# Crow Client Documentation

Documentation and tutorials for crow-client, a client for interacting with endpoints of the FutureHouse crow service.

## Installation

```bash
uv pip install crow-client
```

<!--TOC-->

- [Installation](#installation)
- [Quickstart](#quickstart)
- [Functionalities](#functionalities)
  - [Stages](#stages)
  - [Authentication](#authentication)
- [Job submission](#job-submission)
- [Job retrieval](#job-retrieval)
- [Crow Deployment](#crow-deployment)
  - [Functional environments](#functional-environments)

<!--TOC-->

## Quickstart

```python
from crow_client import CrowClient
from crow_client.models import CrowDeploymentConfig
from pathlib import Path
from aviary.core import DummyEnv
import ldp

client = CrowClient()

crow = CrowDeploymentConfig(
    name="dummy-env-dev",
    path=Path("../envs/dummy_env"),
    environment="dummy_env.env.DummyEnv",
    environment_variables={"SAMPLE_ENV_VAR": "sample_val"},
    agent="ldp.agent.SimpleAgent",
)

client.create_crow(crow)

job_data = {
    "name": "job-futurehouse-dummy-env-dev",
    "query": "Has anyone tested therapeutic exerkines in humans or NHPs?"
}

job_id = client.create_job(job_data)

job_status = client.get_job(job_id)
```

A quickstart example can be found in the [crow_client_notebook.ipynb](./docs/crow_client_notebook.ipynb) file. In this file, we will see how to submit and retrieve a job, pass runtime configuration to the agent, and deploy a crow.

## Functionalities

Crow-client implements a RestClient (called CrowClient) with the following functionalities:

- [Authentication](#authtype): `auth_client`
- [Job submission](#job-submission): `create_job(JobRequest)`
- [Job status](#job-status): `get_job(job_id)`
- [Crow deployment](#crow-deployment): `create_crow(CrowDeploymentConfig)`

To create a CrowClient, you need to pass the following parameters:
| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| stage | Stage | Stage.DEV | Where to submit the job/deploy the crow? |
| organization | str \| None | None | Which organization to use? |
| auth_type | AuthType | AuthType.PASSWORD | Which authentication method to use? |
| api_key | str \| None | None | The API key to use for authentication, if using auth_type=AuthType.API_KEY. |

Instantiating a CrowClient is as simple as:

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

The stage is where your crow will be deployed. This parameter can be one of the following:
| Name | Description |
| --- | --- |
| Stage.DEV | Development environment at https://dev.api.platform.futurehouse.org |
| Stage.PROD | Production environment at https://api.platform.futurehouse.org |

### Authentication

In order to use the CrowClient, you need to authenticate yourself. Authenticatoin is done by providing an API key, which can be obtained directly from your profile page in the FutureHouse platform.

## Job submission

CrowClient can be used to submit jobs to the FutureHouse platform. Using a CrowClient instance, you can submit jobs to the platform by calling the create_job method, which receives a `JobRequest` (or a dictionary with `kwargs`) and returns the job id.

```python
from crow_client import CrowClient
from crow_client.models import AuthType, Stage

client = CrowClient(
    stage=Stage.DEV,
    auth_type=AuthType.API_KEY,
    api_key="your_api_key",
)

job_data = {
    "name": "job-futurehouse-paperqa2-dev",
    "query": "Has anyone tested therapeutic exerkines in humans or NHPs?"
}

job_id = client.create_job(job_data)
```

`JobRequest` have the following fields:
| Field | Type | Description |
| --- | --- | --- |
| id | UUID | Optional job identifier. A UUID will be generated if not provided |
| name | str | Name of the crow to execute eg. paperqa-crow |
| query | str | Query or task to be executed by the crow |
| runtime_config | RuntimeConfig | Optional runtime parameters for the job |

As we will see in the [Crow Deployment section](#crow-deployment), we need to pass a agent module for deployment. On runtime, we can pass a `runtime_config` to interact with the agent's configuration.
`runtime_config` can receive a `AgentConfig` object with the desired kwargs. Check the available `AgentConfig` fields in the [LDP documentation](https://github.com/Future-House/ldp/blob/main/src/ldp/agent/agent.py#L87). Besides the `AgentConfig` object, we can also pass `timeout` and `max_steps` to limit the execution time and the number of steps the agent can take.
Other especialised configurations are also available but are outside the scope of this documentation.

## Job retrieval

Once a job is submitted, you can retrieve it by calling the get_job method, which receives a job id and returns a `Job` object.

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

`job_status` contains all the information about the job. For instance, its `status`, `task` and trajectory in `environment_frame`.

## Crow Deployment

The CrowClient provides simple functions to deploy and monitor your crow. A crow consists of an [`aviary.environment`](https://github.com/Future-House/aviary?tab=readme-ov-file#environment) and a [`ldp.agent`](https://github.com/Future-House/ldp?tab=readme-ov-file#agent).
With a environment developed as a python module, the deployment looks like this:

```python
from pathlib import Path
from crow_client import CrowClient
from crow_client.models import CrowDeploymentConfig, Stage, AuthType

client = CrowClient(
    stage=Stage.DEV,
    auth_type=AuthType.API_KEY,
    api_key="your_api_key",
)

crow = CrowDeploymentConfig(
    path=Path("../envs/dummy_env"),
    environment="dummy_env.env.DummyEnv",
    environment_variables={"SAMPLE_ENV_VAR": "sample_val"},
    agent="ldp.agent.SimpleAgent",
)

client.create_crow(crow)

client.get_build_status()
```

More information on how to define an `aviary.environment` can be found in the [Aviary documentation](https://github.com/Future-House/aviary?tab=readme-ov-file#environment).

In the `CrowDeploymentConfig` object, `path` is the path to the python module where the encironment is implemented. Inside path, you must have either a `requirements.txt` or a `pyproject.toml` file for `crow-client` to be able to install the dependencies. `environment` is the actual environment name as a module.

### Functional environments

Aviary also supports functional environments. For functional environments we don't need to pass the file path and can pass the environment builder instead:

```python
from aviary.core import fenv
import numpy as np


def function_to_use_here(inpste: str):
    a = np.array(np.asmatrix("1 2; 3 4"))
    return inpste


@fenv.start()
def my_env(topic: str):
    """
    Here is the doc string describing the task.
    """
    a = np.array(np.asmatrix("1 2; 3 4"))
    return f"Write a sad story about {topic}", {"chosen_topic": topic}


@my_env.tool()
def print_story(story: str, state) -> None:
    """Print the story and complete the task"""
    print(story)
    print(function_to_use_here(story))
    state.reward = 1
    state.done = True


from crow_client import CrowClient
from crow_client.models import CrowDeploymentConfig, Stage
from crow_client.clients.rest_client import generate_requirements

client = CrowClient(stage=Stage.DEV)

crow = CrowDeploymentConfig(
    functional_environment=my_env,
    environment="my_env",
    requires_aviary_internal=False,
    environment_variables={"SAMPLE_ENV_VAR": "sample_val"},
    agent="ldp.agent.SimpleAgent",
    requirements=generate_requirements(my_env, globals()),
)

client.create_crow(crow)
```
