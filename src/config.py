import os, json, sys, logging

class Telegram :
    def __init__ (self, config) :
        self.access_token = config['access_token']
        self.chat_id = config['chat_id']
        self.messages = config['messages']

class Config :
    def __init__ (self, configPath=os.path.expanduser("~")+"/.pinetmonitorconfig.json") :
        try :
            config = json.loads(open(configPath).read())
            try : self.telegram = Telegram(config["telegram"])
            except KeyError :
                pass # TODO: Add else case to raise an exception for missing access_token

            try : self.dest = config["dest"]
            except KeyError : self.dest = '8.8.8.8'
            logging.info("Destination is {}".format(self.dest))
            try : self.interval = config["interval"]
            except KeyError : self.interval = 5
            logging.info("Interval is {}".format(self.interval))

            try : self.export = config["export"].replace("~", os.path.expanduser("~"))
            except KeyError : self.export = None
            if self.export is not None : logging.info("Export is enabled at {}".format(self.export))

            try : self.succ_retry = config["succ_retry"]
            except KeyError : self.succ_retry = 5
            logging.info("Success retry count is {}".format(self.succ_retry))

            try : self.fail_retry = config["fail_retry"]
            except KeyError : self.fail_retry = 5
            logging.info("Failure retry count is {}".format(self.fail_retry))

        except FileNotFoundError :
            print("Please create config file at {} from config_template.json".format(configPath))
            sys.exit(1)