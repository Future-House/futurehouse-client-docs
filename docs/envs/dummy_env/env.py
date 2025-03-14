# mypy: disable-error-code="valid-type,mutable-override,has-type,misc"
import json
import logging
import os

from aviary.core import DummyEnv as AviaryDummyEnv
from aviary.core import Frame
from aviary.message import Message
from aviary.tools import Tool

logger = logging.getLogger(__name__)


class DummyEnvState(AviaryDummyEnv.State):
    count: int = 0
    end_immediately: bool = False


class DummyEnv(AviaryDummyEnv):
    State = DummyEnvState

    def __init__(
        self,
        count: int = 0,
        task: str = "",
        end_immediately: bool = False,
        concurrent_tool_calls: bool = True,
    ):
        super().__init__(
            task=task,
            end_immediately=end_immediately,
            concurrent_tool_calls=concurrent_tool_calls,
        )
        self.count = count

    @classmethod
    def from_task(cls, task: str) -> "DummyEnv":
        """
        Create 5 different stories by invoking the "print_story" function 5 times given the task.

        Args:
            task: The user query.
        """
        instance = cls(task=task)
        instance.task = task
        return instance

    async def reset(self) -> any:
        def print_story(story: str, state: DummyEnvState) -> str:
            """Print a story.

            Args:
                story: Story to print.
                state: Environment state.
            """
            state.reward = 1.0
            state.count += 1
            state.done = state.count >= 5  # noqa: PLR2004
            state.end_immediately = state.done
            return story

        def cast_float(x: str) -> float:
            """Cast the input argument x to a float."""
            return float(x)

        def cast_int(x: float) -> int:
            """Cast the input argument x to an integer."""
            return int(x)

        self.tools = [
            Tool.from_function(print_story),
            Tool.from_function(cast_float, allow_empty_param_descriptions=True),
            Tool.from_function(cast_int, allow_empty_param_descriptions=True),
        ]
        self.state = type(self).State(
            messages=[
                Message(
                    content="Write a 5 word story via print_story"
                    + (f" about {self.task}" if self.task else "")
                )
            ],
        )
        return self.state.messages, self.tools

    def export_frame(self) -> Frame:
        frame = Frame(
            state={
                "messages": [m.content for m in self.state.messages],
                # Testing that we can render arrays of pdbs through the FramePath
                # and second, different proteins to ensure they can all co-exist in the UI at the same time
                "pdbs": [
                    "https://storage.googleapis.com/fh-public/wikicrow2_pdbs/A1BG.pdb",
                    "https://storage.googleapis.com/fh-public/wikicrow2_pdbs/ABHD16B.pdb",
                    "https://storage.googleapis.com/fh-public/wikicrow2_pdbs/AADACL4.pdb",
                ],
                # Similar test here, but making sure we can render a single pdb without is_iterable on the FramePath
                "single_pdb": (
                    "https://storage.googleapis.com/fh-public/wikicrow2_pdbs/ABCD4.pdb"
                ),
            },
            info={
                "tool_names": [t.info.name for t in self.tools],
                "done": self.state.done,
                "reward": self.state.reward,
            },
        )

        # This is simply an example of how to save some output to crow_service
        # /storage will always be an available volume
        # volume path can be overwritten by passing a different
        #   storage_location via CrowClient
        safe_task = self.task.lower().replace(" ", "-")[:30]  # type: ignore[union-attr]
        safe_task = "".join(c for c in safe_task if c.isalnum() or c in "-_")

        filename = f"frame-{safe_task}.json"

        filepath = os.path.join("/storage", filename)
        logger.info(f"Attempting to write frame to {filepath}")

        try:
            with open(filepath, "w") as f:
                json.dump({"state": frame.state, "info": frame.info}, f, indent=2)
            logger.info(f"Successfully wrote frame to {filepath}")
        except Exception:
            logger.exception(f"Failed to write frame to {filepath}")
            raise
        return frame
