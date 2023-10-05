import os

from singleton_decorator import singleton


@singleton
class __Config:

    # If this mode is enabled, the robot will take no "critical" action
    # (e.g. e-mails won't be sent but only stored in drafts)
    TEST_MODE = os.environ.get("TEST_MODE")

    # This directory holds the data of the robot (input data & temporary files)
    # Per default, this directory should reside in C:\Users\<production_username>\Documents\robot_data
    ROBOT_DATA_DIR = os.environ.get(
        "ROBOT_DATA_DIR",
        os.path.join(
            "c:",
            os.sep,
            "Users",
            os.environ.get("USERNAME"),
            "Documents",
            "robot_data"
        ),
    )

    # Path to a directory from which the robot obtains input data
    INPUT_DATA_DIR = os.environ.get(
        "TMP_ROBOT_PATH",
        # TODO: insert repository name
        os.path.join(ROBOT_DATA_DIR, "input_data", "<process_name>"),
    )

    # Path to a directory where the robot can save temporary files
    TMP_ROBOT_PATH = os.environ.get(
        "TMP_ROBOT_PATH",
        # TODO: insert repository name
        os.path.join(ROBOT_DATA_DIR, "temp_files", "<process_name>"),
    )

    #
    # BMD Executable Command
    #

    # Can be used to define CLI parameters passed to the BMD application upon startup
    BMD_EXEC_PARAMS = os.environ.get("BMD_EXEC_PARAMS", "")

    # The BMD executable file
    BMD_EXECUTABLE = os.environ.get(
        "BMD_EXECUTABLE",
        os.path.join(
            os.environ.get("BMDNTCSDIR"),
            "BMDNTCS.exe"
        ),
    )

    # Command to start BMD
    BMD_EXEC_CMD = " ".join([BMD_EXECUTABLE, BMD_EXEC_PARAMS])


cfg = __Config()
