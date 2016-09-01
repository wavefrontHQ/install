import multiprocessing
import socket
import sys
import time

def handle(connection, address, keywords):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("process-%r" % (address,))
    start_time = time.time()

    # using dict to keep track of what has been seen
    # initialization
    found = False
    key_map = {}
    for key in keywords:
        key_map[key] = False

    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            data = connection.recv(1024)
            if data == "":
                logger.debug("Socket closed remotely")
                break
            logger.debug("Received data %r", data)
            # if key that has not been found is found in the data,
            # change the mapping of that key to true
            for key in key_map:
                if not key_map[key]:
                    if key in data:
                        logger.debug("Found key {}".format(key))
                        key_map[key] = True

            # filtered the map
            key_map = {key:key_map[key]
                for key in key_map if not key_map[key]}
            if not key_map:
                found = True
                sys.exit(0)

            # connection.sendall(data)
            # logger.debug("Sent data")
    except:
        if not found:
            logger.exception("Problem handling request")
    finally:
        logger.debug("Closing socket")
        # connection.shutdown(socket.SHUT_RD)
        connection.close()
        for key in key_map:
            logger.debug("Failed to find {}".format(key))

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
        process = multiprocessing.Process(
            target=handle, args=(conn, address, self.keywords))
        process.daemon = True
        process.start()
        start_time = time.time()
        self.logger.debug("Started process %r", process)
        while process.is_alive():
            end_time = time.time()
            if end_time - start_time > 35:
                process.terminate()
                sys.exit(1)
                break

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

