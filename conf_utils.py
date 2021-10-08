import yaml


def read_conf_from_path(pth):
    """ Read configuration from file
    :param pth: path to configuration file
    """

    with open(pth, 'r') as stream:
        try:
            return yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)


conf = read_conf_from_path('conf.yml')

DATABASE_NAME = conf['database_name']
DATABASE_ADDRESS = conf['database_address']
DATABASE_USER = conf['database_user']
DATABASE_PASSWORD = conf['database_password']
DATABASE_PORT = conf['database_port']

IP = conf['server_ip']
PORT = conf['server_port']

DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(DATABASE_USER, DATABASE_PASSWORD, DATABASE_ADDRESS,
                                                         DATABASE_PORT, DATABASE_NAME)

TIME_UPDATE = conf['time_update']
SENDER_ADDRESS = conf['sender_address']
SENDER_PASSWORD = conf['sender_password']