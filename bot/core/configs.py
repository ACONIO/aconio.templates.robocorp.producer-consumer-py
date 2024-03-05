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

    # Track the 'Frist' IDs of the cases where the employee gets informed,
    # preventing those 'Fristen' from being processed twice,
    # since they are not automatically set to done
    TRACK_ALERTS_ASSET_NAME = os.environ.get(
        "TRACK_ALERTS_ASSET_NAME", "vz_alert_cases"
    )


class ProducerConfig(Config):
    """Configuration of the producer process."""

    #
    # General Config
    #

    # Maximum amount of work items created by the producer
    MAX_WORK_ITEMS = os.environ.get("MAX_WORK_ITEMS")

    # TODO: Add properties here...

    def __init__(self):
        pass
        # TODO: Add property validation here...


class ConsumerConfig(Config):
    """Configuration of the consumer process."""

    # TODO: Add properties here...

    def __init__(self):
        pass
        # TODO: Add property validation here


class ReporterConfig(Config):
    """ Configuration of the reporter process. """

    # Determines which error code of the BusinessError will result
    # in which message in the reporter e-mail.
    CODES: dict[str, str] = {
        # TODO: Add error codes here...
        # Example:
        # "MISSING_CLIENT_SALUTATION": "Für diesen Klient ist keine Anrede in BMD hinterlegt.",
    }

    # Report Jinja2 HTML template
    REPORT_TEMPLATE_FILE = "report.j2"

    # Report e-mail config
    REPORT_RECIPIENTS = os.environ.get("REPORT_RECIPIENTS")
    REPORT_SALUTATION = os.environ.get("REPORT_SALUTATION", "Sehr geehrte Damen und Herren")

    # Process contact person
    CONTACT_PERSON = os.environ.get("CONTACT_PERSON", "patrick.krukenfellner@aconio.net")

    # If true, the bot will not send the e-mail to the client's e-mail address
    SAVE_AS_DRAFT = os.environ.get("SAVE_AS_DRAFT", "true").lower() == "true"

    def __init__(self):
        super().__init__()

        # Folder, where the mail templates reside
        self.TEMPLATES = os.environ.get(
            "TEMPLATES", os.path.join(self.INPUT_DIR, "templates"))

        if self.TEST_MODE:
            self.SAVE_AS_DRAFT = True
