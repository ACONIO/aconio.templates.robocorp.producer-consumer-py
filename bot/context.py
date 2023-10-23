from abc import ABC
from enum import Enum

from config import *

# from libraries.BoxIt import BoxIt # If BoxIT Process, uncomment this line


class RobotType(str, Enum):
    PRODUCER = "PRODUCER"
    CONSUMER = "CONSUMER"
    DEFAULT = "DEFAULT"  # mainly used for testing


class RunContextFactory:
    def make(
        process_type: RobotType,
        start_recording: bool = False,
        init_bmd_db: bool = False,
        init_bmd_macros: bool = False,
        start_bmd: bool = False,
        start_outlook: bool = False,
    ):
        if process_type == RobotType.PRODUCER:
            return RunContextProducer(
                start_recording=start_recording,
                init_bmd_db=init_bmd_db,
                init_bmd_macros=init_bmd_macros,
                start_bmd=start_bmd,
                start_outlook=start_outlook,
            )
        elif process_type == RobotType.CONSUMER:
            return RunContextConsumer(
                start_recording=start_recording,
                init_bmd_db=init_bmd_db,
                init_bmd_macros=init_bmd_macros,
                start_bmd=start_bmd,
                start_outlook=start_outlook,
            )
        elif process_type == RobotType.DEFAULT:
            return RunContextDefault(
                start_recording=start_recording,
                init_bmd_db=init_bmd_db,
                init_bmd_macros=init_bmd_macros,
                start_bmd=start_bmd,
                start_outlook=start_outlook,
            )


class RunContextBase(ABC):
    """This class manages the run context of the process. It offers setup and teardown functionality
    that initializes resources (mainly library objects) required by the process and manages the
    resources cleanup when the process run is completed.
    """

    def __init__(self, **kwargs) -> None:
        """Configure the process run context. Load the required libraries and init the config."""

        self.start_recording = kwargs.get("start_recording", False)
        self.init_bmd_db = kwargs.get("init_bmd_db", False)
        self.init_bmd_macros = kwargs.get("init_bmd_macros", False)
        self.start_bmd = kwargs.get("start_bmd", False)
        self.start_outlook = kwargs.get("start_outlook", False)

        # If BoxIT Process, create BoxIt object
        # self.boxit = BoxIt()

    def __enter__(self) -> None:
        """Steps performed before every robot run."""
        pass
        # Uncomment after adding the respective libraries.
        # if self.start_recording:
        #     from shared.utils.libraries.VideoRecorder import VideoRecorder
        #     self.rec = VideoRecorder()
        #     self.rec.start_recorder(filename='output/video.webm', max_length=10800)

        # if self.init_bmd_db:
        #     from shared.bmd.libraries.BMDDatabase import BMDDatabase
        #     self.bmd_db = BMDDatabase()
        #     self.bmd_db.load_db_config_from_vault()
        #     self.bmd_db.connect_BMD_database()
        #     self.bmd_db.check_connection()

        # if self.init_bmd_macros:
        #     from shared.bmd.libraries.BMDMacros import BMDMacros
        #     self.bmd_macros = BMDMacros()

        # if self.start_bmd:
        #     from shared.bmd.libraries.BMDHelper import BMDHelper
        #     self.bmd = BMDHelper()
        #     self.bmd.start_BMD(self.cfg.BMD_EXEC_CMD)

        # if self.start_outlook:
        #     from shared.utils.libraries.OutlookExtended import OutlookExtended
        #     self.outlook = OutlookExtended()
        #     self.outlook.start_outlook()

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Steps performed after every robot run."""
        pass
        # Uncomment after adding the respective libraries.
        # if self.start_outlook:
        #     self.outlook.quit_application()

        # if self.start_bmd:
        #     self.bmd.close_bmd()

        # if self.start_recording:
        #     self.rec.stop_recorder()


class RunContextProducer(RunContextBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.cfg = ProducerConfig()


class RunContextConsumer(RunContextBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.cfg = ConsumerConfig()


class RunContextDefault(RunContextBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.cfg = Config()
