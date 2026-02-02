from app.core.config import settings, logger

def test_config():
    try:
        logger.info(f"Project Name: {settings.PROJECT_NAME}")
        logger.info(f"Version: {settings.VERSION}")
        # Only check existence, don't log keys
        keys_status = {
            "GROQ_API_KEY": bool(settings.GROQ_API_KEY),
            "PINECONE_API_KEY": bool(settings.PINECONE_API_KEY),
            "PINECONE_INDEX_NAME": bool(settings.PINECONE_INDEX_NAME),
        }
        logger.info(f"Keys Configured: {keys_status}")
        print("CONFIG_TEST_SUCCESS")
    except Exception as e:
        logger.error(f"Config Test Failed: {str(e)}")
        print(f"CONFIG_TEST_ERROR: {str(e)}")

if __name__ == "__main__":
    test_config()
