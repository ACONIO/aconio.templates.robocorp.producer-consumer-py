"""This file contains shared functions used by multiple tasks."""

from robocorp import log
from robocorp import vault
from RPA.FileSystem import FileSystem

from config import cfg

# TODO: import shared subtrees before activating related imports & code
# from shared.utils.libraries.VideoRecorder import VideoRecorder
# from shared.utils.libraries.OutlookExtended import OutlookExtended
# from shared.utils.libraries.FinanzOnline import FinanzOnline
# from shared.bmd.libraries.BMDDatabase import BMDDatabase
# from shared.bmd.libraries.BMDHelper import BMDHelper

# rec = VideoRecorder()
# outlook = OutlookExtended()
# finon = FinanzOnline()
# bmd_db = BMDDatabase()
# bmd = BMDHelper()


def setup(start_recording: bool = True,
          login_finonline: bool = True,
          init_bmd_db: bool = True,
          start_bmd: bool = True,
          start_outlook: bool = True):
    """Steps performed before every robot run."""

    cleanup_robot_tmp_folder()

    # if start_recording:
    #     rec.start_recording(filename='output/video.webm', max_length=10800)

    # if login_finonline:
    #     finon_creds = vault.get_secret("finon_credentials")

    #     finon.set_login_credentials(
    #         teilnehmer_id=finon_creds["teilnehmer_id"],
    #         benutzer_id=finon_creds["benutzer_id"],
    #         pin=finon_creds["pin"]
    #     )

    # if init_bmd_db:
    #     bmd_db.load_db_config_from_vault()
    #     bmd_db.connect_BMD_database()
    #     bmd_db.check_connection()

    # if start_bmd:
    #     bmd.start_BMD(cfg.BMD_EXEC_CMD)

    # if start_outlook:
    #     outlook.start_outlook()


def teardown(save_recording: bool = True,
             close_outlook: bool = True,
             close_bmd: bool = True):
    """Steps performed after every robot run."""

    # if close_outlook:
    #     outlook.quit_application()

    # if close_bmd:
    #     bmd.close_bmd()

    # if save_recording:
    #     rec.stop_recorder()
    # else:
    #     try:
    #         rec.cancel_recorder()
    #     except:
    #         log.info('could not cancel recording')


def cleanup_robot_tmp_folder():
    """Removes all documents from the robot temp folder to cleanup previous runs."""
    fs = FileSystem()
    fs.remove_files(fs.list_files_in_directory(cfg.TMP_ROBOT_PATH))
