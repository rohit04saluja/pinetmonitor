#!/usr/bin/python3

import logging
import sys, time, subprocess, re, os
import threading
from telegram.ext import (Updater, CommandHandler)
from config import Config
from datetime import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.debug("Logging initialized")


'''Class for ping functionality'''
class Ping :
    def __init__ (self, dest) :
        logging.debug("Ping initialization")
        out = subprocess.run("ping -c 1 {0}".format(dest).split(" "), capture_output=True)
        self.returncode = out.returncode
        logging.debug("Ping returncode is {0}".format(out.returncode))
        if self.returncode == 0 :
            r = re.search("(\d+) bytes from .*: icmp_seq=\d+ ttl=(\d+) time=(\d+.\d+) ms", out.stdout.decode('UTF-8'))
            self.stdout = r.group(0)
            self.size = int(r.group(1))
            self.ttl = int(r.group(2))
            self.time = float(r.group(3))
        else :
            try:
                self.stdout = out.stdout.decode('UTF-8').split('\n')[1]
            except IndexError :
                self.stdout = out.stdout.decode('UTF-8')
        if self.stdout == "" :
            logging.debug(out.stdout.decode('UTF-8'))

class PiNetMonitor :
    def __init__ (self) :
        self.__config = Config()
        logging.debug("Config initialized")
        self.interval = self.__config.interval
        # Setup Telegram
        self._t_updater = Updater(token=self.__config.telegram.access_token, use_context=True)
        logging.debug("Telegram initialized")
        logging.info("Initialization is complete")

    def __sendMessage (self, msg="") :
        for id in self.__config.telegram.chat_id :
            logging.debug("Sending message for id {}".format(id))
            self._t_updater.dispatcher.bot.send_message(chat_id=id, text=msg)

    def __export (self, ping) :
        if (self.__config.export is not None) :
            f = open (os.path.abspath(self.__config.export), 'a')
            try :
                f.write("{0},{1},{2},{3},{4}\n".format(str(datetime.now()), self.__config.interval, ping.size, ping.ttl, ping.time))
            except AttributeError :
                f.write("{0},{1},{2},{3},{4}\n".format(str(datetime.now()), self.__config.interval, 0, 0, 0))
            f.close()

    def run (self, dest=None) :
        if dest is None : dest = self.__config.dest
        # Setup ctrl-c exit for the script
        try :
            connected = (Ping(dest).returncode == 0)
            succ_retry = fail_retry = 0
            while True :
                # Check the ping connectivity to dest
                p = Ping(dest)
                print(p.stdout)
                if (self.__config.export is not None) : self.__export(p)

                if p.returncode == 0 :
                    if not connected :
                        logging.warning("Change of state detected. It was not connected before")
                        fail_retry = 0
                        succ_retry = succ_retry + 1
                        logging.debug("Success retry count is {}".format(succ_retry))
                        # Send notification that the internet is back up
                        if succ_retry > self.__config.succ_retry :
                            succ_retry = 0
                            logging.warning("Changing interval to {}s".format(self.__config.interval))
                            self.interval = self.__config.interval
                            connected = True
                            self.__sendMessage(self.__config.telegram.messages["up"])
                    elif fail_retry > 0 :
                        # Reset interval time
                        self.interval = self.__config.interval
                        fail_retry = 0

                elif connected :
                    logging.warning("Change of state detected. It was connected before")
                    succ_retry = 0
                    fail_retry = fail_retry + 1
                    logging.debug("Failure retry count is {}".format(fail_retry))
                    logging.warning("Changing interval to 1s")
                    self.interval = 1
                    if fail_retry > self.__config.fail_retry :
                        fail_retry = 0
                        connected = False
                time.sleep(self.interval)
        except KeyboardInterrupt :
            print()
            print("Good bye")
            sys.exit(0)

class SpeedTest :
    def __init__ (self) :
        self.__config = Config()
        logging.debug("Config initialized")

    def __SpeedTest (self) :
        logging.debug('Starting Speedtest now')
        out = subprocess.run(["speedtest"], capture_output=True)
        down = up = ''
        for line in out.stdout.decode('UTF-8').split('\n') :
            if re.search ('Download: .*', line) :
                down = line.split(' ')[1]
            if re.search ('Upload: .*', line) :
                up = line.split(' ')[1]
        return down, up

    def __SpeedTestHandler (self, updater, context) :
        updater.message.reply_text('I am checking now')
        down, up = self.__SpeedTest()
        updater.message.reply_text('Down is {0} and Up is {1}'.format(down, up))

    def run (self) :
        updater = Updater(self.__config.telegram.access_token, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler('speedtest', self.__SpeedTestHandler))
        updater.start_polling()
        updater.idle()

class MyThread (threading.Thread) :
    def __init__ (self, obj, name) :
        threading.Thread.__init__(self)
        self.__obj = obj
        self.__name = name

    def run(self) :
        logging.info('Starting thread {0}'.format(self.__name))
        self.__obj.run()
        logging.info('Exiting thread {0}'.format(self.__name))

if __name__ == "__main__":
    logging.debug('Entering main')
    MyThread(PiNetMonitor(), "PiNetMonitor").start()
    time.speed(60)
    SpeedTest().run()
    logging.debug('Exiting main')