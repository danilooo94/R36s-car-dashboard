import config
import app_log
from obd.store            import DataStore
from obd.esp32_reader     import Esp32SerialReader
from obd.logger           import DataLogger
from dashboard.app_extras import AppExtras


def main():
    app_log.install_excepthook()
    app_log.info(f"=== sessão iniciada — log de erros: {app_log.path} ===")

    store  = DataStore()
    reader = Esp32SerialReader(store)
    reader.start()

    logger = None
    if config.LOG_ENABLED:
        logger = DataLogger(store)
        logger.start()
        app_log.info(f"Gravando dados em: {logger.path}")

    try:
        AppExtras(store).run()
    except Exception:
        app_log.exception("Erro não tratado no loop principal")
        raise
    finally:
        reader.stop()
        reader.join(timeout=2)
        if logger:
            logger.stop()
            logger.join(timeout=2)
        app_log.info("=== sessão encerrada ===")


if __name__ == "__main__":
    main()
