# crow-client-docs

Documentation and tutorials for crow-client, a client for interacting with endpoints of the FutureHouse crow service.

## Installation

```bash
uv pip install crow-client
```

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
| Stage.LOCAL | Local development at http://localhost:8080 |
| Stage.LOCAL_DOCKER | Docker local development at http://host.docker.internal:8080 |

### AuthType

The auth_type parameter can be one of the following:
| Name | Description |
| --- | --- |
| AuthType.GOOGLE | Authentication using Google OAuth |
| AuthType.PASSWORD | Authentication using email and password |
| AuthType.API_KEY | Authentication using an FutureHouse platform API key |

## Job submission

CrowClient can be used to submit jobs to the FutureHouse platform. Using a CrowClient instance, you can submit jobs to the platform by calling the create_job method, which receives a `JobRequest` (or a dictionary) and returns the job id.

```python
from crow_client import CrowClient
from crow_client.models import AuthType, Stage

client = CrowClient(
    stage=Stage.DEV,
    organization="your_organization",
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

> NOTE: Add some docs on `runtime_config` here. How to use it to make runtime changes to your crow.
>
> Considering PaperQA, can we use it to change the `llm`, for instance?
>
> How to use the `upload_id` for the gcp?
>
> Can we use it to deserialize the `state`?
>
> Can we use it to maintain files after the job is finished? Maybe giving the option to download the files from the platform?

## Job retrieval

Once a job is submitted, you can retrieve it by calling the get_job method, which receives a job id and returns a `Job` object.

```python
from crow_client import CrowClient
from crow_client.models import AuthType

client = CrowClient(
    auth_type=AuthType.API_KEY,
    api_key="your_api_key",
)

job_id = "e809b6ba-bc0f-4e5a-9a91-f9a76ab92a30"

job_status = client.get_job(job_id)
```

`job_status` contains all the information about the job. For instance, its `status`, `task` and the entire trajectory as `environment_frame`

> NOTE: Do we want to provide an illustration of this schema?
>
> NOTE: Are `CrowJob` and `CrowJobClient` useful?? What else can they do?
>
> `CrowJob` was in previous README, but it seems it's gone now.
>
> `CrowJobClient` seems to have only a few methods: `finalize_environment`, `store_agent_state`, and `store_environment_frame`. It seems to work more in behind the scenes. Should we document it?

## Crow Deployment

The CrowClient provides simple functions to deploy and monitor your crow. A crow consists of an [`aviary.environment`](https://github.com/Future-House/aviary?tab=readme-ov-file#environment) and a [`ldp.agent`](https://github.com/Future-House/ldp?tab=readme-ov-file#agent).
With a environment developed as a python module, the deployment looks like this:

```python
from pathlib import Path
from crow_client import CrowClient
from crow_client.models import CrowDeploymentConfig, Stage, AuthType

client = CrowClient(
    stage=Stage.DEV,
    organization="your_organization",
    auth_type=AuthType.API_KEY,
    api_key="your_api_key",
)

> NOTE: What are `path` and `environment` here?

crow = CrowDeploymentConfig(
    path=Path("../envs/dummy_env"),
    environment="dummy_env.env.DummyEnv",
    requires_aviary_internal=False,
    environment_variables={"SAMPLE_ENV_VAR": "sample_val"},
    agent="ldp.agent.SimpleAgent",
)

client.create_crow(crow)

client.get_build_status()
```

More information on how to define an `aviary.environment` can be found in the [Aviary documentation](https://github.com/Future-House/aviary?tab=readme-ov-file#environment).

> NOTE: Want to talk about local crow deployment here.

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

client = CrowClient(stage=Stage.LOCAL)

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
