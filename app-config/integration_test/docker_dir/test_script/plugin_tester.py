import multiprocessing
import socket
import sys
import time

def handle(connection, address, key_list):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("process-%r" % (address,))

    found = False
    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            data = connection.recv(1024)
            if data == "":
                logger.debug("Socket closed remotely")
                break
            logger.debug("Received data %r", data)
            # if key in list is found, then remove that key
            for key in key_list:
                if key in data:
                    logger.debug("Found key {}".format(key))
                    key_list.remove(key)

            # an empty list denotes all keywords are found
            if len(key_list) == 0:
                found = True
                sys.exit(0)

            # connection.sendall(data)
            # logger.debug("Sent data")
    except:
        # sys.exit is an exception.  Successful exit
        # should not have exception message.
        if not found:
            logger.exception("Problem handling request")
    finally:
        logger.debug("Closing socket")
        connection.shutdown(socket.SHUT_RD)
        connection.close()


class Server(object):
    def __init__(self, hostname, port, keywords):
        import logging
        self.logger = logging.getLogger("server")
        self.hostname = hostname
        self.port = port
        self.keywords = keywords

    def start(self):
        self.logger.debug("listening")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        self.socket.settimeout(60)
        conn, address = self.socket.accept()
        self.logger.debug("Got connection")

        # initialize a list for keeping track of keyword not found
        # using Manager, which allow an object to be shared
        # between processes.  It is slower than using shared memory.
        manager = multiprocessing.Manager()
        key_list = manager.list(self.keywords)

        process = multiprocessing.Process(
            target=handle, args=(conn, address, key_list))
        process.daemon = True
        process.start()
        start_time = time.time()  # keep track of time passed
        self.logger.debug("Started process %r", process)

        while process.is_alive():
            end_time = time.time()
            # exceed two cycles of collectd agent report
            if end_time - start_time > 65:
                self.logger.debug("Closing socket by server object")
                conn.shutdown(socket.SHUT_RD)
                conn.close()
                process.terminate()
                process.join()

                for key in key_list:
                    self.logger.debug("Failed to find {}".format(key))
                sys.exit(1)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    arg_len = len(sys.argv)
    if arg_len != 2:
        logging.debug("Usage: plugin_tester.py [keymetrics].")
        sys.exit(1)

    keywords = sys.argv[1].split(' ')
    server = Server("127.0.0.1", 4242, keywords)

    try:
        logging.info("Listening")
        server.start()
    except:
        logging.exception("Unexpected exception")
        sys.exit(1)
    finally:
        logging.info("Shutting down")
        for process in multiprocessing.active_children():
            logging.info("Shutting down process %r", process)
            process.terminate()
            process.join()
    logging.info("All done")

