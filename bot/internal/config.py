"""This file holds all configuration options of the process."""
import os


class Config:
    # If this mode is enabled, the robot will take no "critical" action
    # (e.g. e-mails won't be sent but only stored in drafts)
    TEST_MODE = os.environ.get("TEST_MODE").lower() == 'true'

    # This directory holds the data of the robot (input files & temporary files)
    ROBOT_DATA_DIR = os.environ.get("ROBOT_DATA_DIR")

    # Path to a directory from which the robot obtains input data
    INPUT_DIR = os.environ.get(
        "INPUT_DIR",
        os.path.join(ROBOT_DATA_DIR, "input"),
    )

    # Path to a directory where the robot can save temporary files
    TEMP_DIR = os.environ.get(
        "TEMP_DIR",
        os.path.join(ROBOT_DATA_DIR, "temp"),
    )

    #
    # BMD Executable Command
    #

    # Can be used to define CLI parameters passed to the BMD application upon startup
    BMD_EXEC_PARAMS = os.environ.get("BMD_EXEC_PARAMS", "")

    # The BMD executable file
    BMD_EXECUTABLE = os.environ.get(
        "BMD_EXECUTABLE",
        os.path.join(os.environ.get("BMDNTCSDIR"), "BMDNTCS.exe"),
    )

    # Command to start BMD
    BMD_EXEC_CMD = " ".join([BMD_EXECUTABLE, BMD_EXEC_PARAMS])


class ProducerConfig(Config):
    """Configuration of the producer process."""

    # TODO: Add properties here...

    def __init__(self):
        super().__init__()
        # TODO: Add property validation here...


class ConsumerConfig(Config):
    """Configuration of the consumer process."""

    # TODO: Add properties here...

    def __init__(self):
        super().__init__()
        # TODO: Add property validation here
