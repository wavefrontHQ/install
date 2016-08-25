import multiprocessing
import socket
import sys
import time

def handle(connection, address, keyword):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("process-%r" % (address,))
    start_time = time.time()
    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            data = connection.recv(1024)
            if data == "":
                logger.debug("Socket closed remotely")
                break
            logger.debug("Received data %r", data)
            if keyword in data:
                sys.exit(0)
                break
            # connection.sendall(data)
            # logger.debug("Sent data")
    except:
        logger.exception("Problem handling request")
    finally:
        logger.debug("Closing socket")
        # connection.shutdown(socket.SHUT_RD)
        connection.close()

class Server(object):
    def __init__(self, hostname, port, keyword):
        import logging
        self.logger = logging.getLogger("server")
        self.hostname = hostname
        self.port = port
        self.keyword = keyword

    def start(self):
        self.logger.debug("listening")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        self.socket.settimeout(60)
        conn, address = self.socket.accept()
        self.logger.debug("Got connection")
        process = multiprocessing.Process(
            target=handle, args=(conn, address, self.keyword))
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
    if arg_len == 2:
        keyword = sys.argv[1]
        server = Server("127.0.0.1", 4242, sys.argv[1])
    else:
        sys.exit(1)

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

