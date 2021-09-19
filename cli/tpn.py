import sys
import cli.commands
from nubia import Nubia, Options
from cli.plugin import CLIPlugin


def main():
    plugin = CLIPlugin()
    shell = Nubia(
        name="tpn",
        command_pkgs=cli.commands,
        plugin=plugin,
        options=Options(
            persistent_history=False, auto_execute_single_suggestions=True
        ),
    )
    sys.exit(shell.run())


if __name__ == "__main__":
    main()
