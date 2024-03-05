from abc import ABC

from bot.core import config


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

    def __enter__(self) -> None:
        """Steps performed before every robot run."""
        if self.start_recording:
            pass
            # TODO: UNCOMMENT ON DEMAND.
            # from shared.utils.libraries.VideoRecorder import VideoRecorder

            # self.rec = VideoRecorder()
            # self.rec.start_recorder(filename="output/video.webm", max_length=10800)

        try:
            if self.init_bmd_db:
                pass
                # TODO: UNCOMMENT ON DEMAND.
                # from shared.bmd.libraries.BMDDatabase import BMDDatabase

                # self.bmd_db = BMDDatabase()
                # self.bmd_db.load_db_config_from_vault()
                # self.bmd_db.connect_BMD_database()
                # self.bmd_db.check_connection()

            if self.init_bmd_macros:
                pass
                # TODO: UNCOMMENT ON DEMAND.
                # from shared.bmd.libraries.BMDMacros import BMDMacros

                # self.bmd_macros = BMDMacros()

            if self.start_bmd:
                pass
                # TODO: UNCOMMENT ON DEMAND.
                # from shared.bmd.libraries.BMDHelper import BMDHelper

                # self.bmd = BMDHelper()
                # self.bmd.start_BMD(self.cfg.BMD_EXEC_CMD)

            if self.start_outlook:
                pass
                # TODO: UNCOMMENT ON DEMAND.
                # from shared.utils.libraries.OutlookExtended import OutlookExtended

                # self.outlook = OutlookExtended()
                # self.outlook.start_outlook()

        except Exception as e:
            # Ensure to stop recorder threads and re-raise exception
            self.rec.stop_recorder()
            raise e

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Steps performed after every robot run."""
        if self.start_outlook:
            pass
            # self.outlook.quit_application()

        if self.start_bmd:
            pass
            # self.bmd.close_bmd()

        if self.start_recording:
            pass
            # self.rec.stop_recorder()


class RunContextProducer(RunContextBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.cfg = config.ProducerConfig()


class RunContextConsumer(RunContextBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.cfg = config.ConsumerConfig()

        # init jinja2 environment holding all template files
        from jinja2 import Environment, FileSystemLoader, StrictUndefined

        self.jinja_env = Environment(
            loader=FileSystemLoader(self.cfg.TEMPLATES),
            # throw is some variable is present in the template but not passed
            undefined=StrictUndefined,
        )

        if self.cfg.TRACK_ITEMS_ASSET_NAME:
            pass
            # TODO: UNCOMMENT ON DEMAND.
            # from shared.utils.libraries.ItemCounter import ItemCounter
            # self.item_counter = ItemCounter(self.cfg.TRACK_ITEMS_ASSET_NAME)


class RunContextReporter(RunContextBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.cfg = config.ReporterConfig()

        # init jinja2 environment holding all template files
        from jinja2 import Environment, FileSystemLoader, StrictUndefined

        self.jinja_env = Environment(
            loader=FileSystemLoader(self.cfg.TEMPLATES),
            # throw is some variable is present in the template but not passed
            undefined=StrictUndefined,
        )


class RunContextDefault(RunContextBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.cfg = config.Config()
