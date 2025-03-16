import sys

from pydantic import BaseModel, RootModel
from pytauri import (
    BuilderArgs,
    builder_factory,
    context_factory, Commands,
)

commands: Commands = Commands()

class Person(BaseModel):
    name: str


@commands.command()
async def greet(body: Person) -> RootModel[str]:
    return RootModel[str](
        message=f"Hello, {body.name}! You've been greeted from Python {sys.winver}!"
    )


def main() -> None:
    app = builder_factory().build(
        BuilderArgs(
            context=context_factory(),
        )
    )
    app.run()
