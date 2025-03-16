from pytauri import (
    BuilderArgs,
    builder_factory,
    context_factory,
)


def main() -> None:
    app = builder_factory().build(
        BuilderArgs(
            context=context_factory(),
        )
    )
    app.run()