import arcade_github
from arcade_github.tools.activity import set_starred

from arcade.core.catalog import ToolCatalog
from arcade.sdk.eval import (
    BinaryCritic,
    EvalRubric,
    EvalSuite,
    tool_eval,
)

# Evaluation rubric
rubric = EvalRubric(
    fail_threshold=0.9,
    warn_threshold=0.95,
)

catalog = ToolCatalog()
# Register the GitHub tools
catalog.add_module(arcade_github)


@tool_eval()
def github_activity_eval_suite() -> EvalSuite:
    """Evaluation suite for GitHub Activity tools."""
    suite = EvalSuite(
        name="GitHub Activity Tools Evaluation Suite",
        system_message="You are an AI assistant that helps users interact with GitHub repositories using the provided tools.",
        catalog=catalog,
        rubric=rubric,
    )

    # Set Starred
    suite.add_case(
        name="Star a repository",
        user_message="Star the test repository that is owned by ArcadeAI.",
        expected_tool_calls=[
            (
                set_starred,
                {
                    "owner": "ArcadeAI",
                    "name": "test",
                    "starred": True,
                },
            )
        ],
        critics=[
            BinaryCritic(critic_field="owner", weight=0.3),
            BinaryCritic(critic_field="name", weight=0.3),
            BinaryCritic(critic_field="starred", weight=0.4),
        ],
    )

    suite.add_case(
        name="Unstar a repository",
        user_message="Unstar the ArcadeAI/test repository.",
        expected_tool_calls=[
            (
                set_starred,
                {
                    "owner": "ArcadeAI",
                    "name": "test",
                    "starred": False,
                },
            )
        ],
        critics=[
            BinaryCritic(critic_field="owner", weight=0.3),
            BinaryCritic(critic_field="name", weight=0.3),
            BinaryCritic(critic_field="starred", weight=0.4),
        ],
    )

    return suite