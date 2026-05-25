import config
from obd.store  import DataStore
from obd.reader import OBDReader
from obd.mock   import MockReader
from obd.logger import DataLogger
from dashboard.app import App

def main():
    store  = DataStore()
    reader = MockReader(store) if config.MOCK_MODE else OBDReader(store, config.OBD_HOST, config.OBD_PORT)
    reader.start()

    logger = None
    if config.LOG_ENABLED:
        logger = DataLogger(store)
        logger.start()
        print(f"Gravando em: {logger.path}")

    try:
        App(store).run()
    finally:
        reader.stop()
        reader.join(timeout=2)
        if logger:
            logger.stop()
            logger.join(timeout=2)

if __name__ == "__main__":
    main()
