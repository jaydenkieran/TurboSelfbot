import logging
import sys
import os
import colorlog
import configparser
import ruamel.yaml as yaml


class Logging:

    """
    Configures and sets up logging modules
    """

    def __init__(self, filename):
        self.lg = logging.getLogger(__name__)
        self.lg.setLevel(logging.DEBUG)
        self.fh = logging.FileHandler(
            filename=filename, encoding='utf-8', mode='w')
        self.fh.setFormatter(logging.Formatter(
            "[{asctime}] {levelname} ({filename} L{lineno}, {funcName}): {message}", style='{'
        ))
        self.lg.addHandler(self.fh)

        self.sh = logging.StreamHandler(stream=sys.stdout)
        self.sh.setFormatter(colorlog.LevelFormatter(
            fmt={
                "DEBUG": "{log_color}{levelname} ({module} L{lineno}, {funcName}): {message}",
                "INFO": "{log_color}{message}",
                "WARNING": "{log_color}{levelname}: {message}",
                "ERROR": "{log_color}{levelname} ({module} L{lineno}, {funcName}): {message}",
                "CRITICAL": "{log_color}{levelname} ({module} L{lineno}, {funcName}): {message}"
            },
            log_colors={
                "DEBUG": "purple",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red"
            },
            style='{'
        ))
        self.sh.setLevel(logging.INFO)
        self.lg.addHandler(self.sh)
        self.lg.debug('Logging has started')


class Config:

    """
    Class for working with the configuration file
    """

    def __init__(self, filename):
        self.log = logging.getLogger(__name__)

        self.filename = filename
        if not os.path.isfile(filename):
            self.log.critical("'{}'' does not exist".format(filename))
            os._exit(1)

        try:
            config = configparser.ConfigParser(interpolation=None)
            config.read(filename, encoding='utf-8')
        except Exception as e:
            self.log.critical(str(e))
            os._exit(1)

        # ---------------------------------------------------- #
        # DO NOT EDIT THIS FILE DIRECTLY. EDIT THE CONFIG FILE #
        # ---------------------------------------------------- #

        # [Auth]
        self.token = config.get('Auth', 'Token', fallback=None)
        self.password = config.get('Auth', 'Password', fallback=None)

        # [General]
        self.selfbot = config.getboolean('General', 'Selfbot', fallback=False)
        self.pm = config.getboolean('General', 'AllowPms', fallback=True)
        self.prefix = config.get('General', 'Prefix', fallback='!')
        self.delete = config.getboolean('General', 'Delete', fallback=True)

        # [Database]
        self.rhost = config.get('Database', 'Host', fallback='localhost')
        self.rport = config.getint('Database', 'Port', fallback=28015)
        self.ruser = config.get('Database', 'User', fallback='admin')
        self.rpass = config.get('Database', 'Password', fallback='')

        self.log.debug("Loaded '{}'".format(filename))
        self.validate()

    def validate(self):
        """
        Checks configuration options for valid values
        """
        critical = False
        if not self.token:
            self.log.critical('You must provide a token in the config')
            critical = True
        if critical:
            os._exit(1)


class Yaml:

    """
    Class for handling YAML
    """

    def __init__(self):
        self.log = logging.getLogger(__name__)

    def parse(self, filename):
        """
        Parse a YAML file
        """
        try:
            with open(filename) as f:
                try:
                    return yaml.load(f)
                except yaml.YAMLError as e:
                    self.log.critical("Problem parsing {} as YAML: {}".format(
                        filename, e))
                    return None
        except FileNotFoundError:
            self.log.critical("Problem opening {}: File was not found".format(
              filename))
            return None
