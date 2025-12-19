import logging

logger = logging.getLogger(__name__)


async def get_custom_diamonds(query_params: dict):
    logger.info("Fetching CUSTOM diamonds")
    return {
        "diamonds": [],
        "pagination": {}
    }


async def get_csv_diamonds(query_params: dict, shopify_name: str | None):
    logger.info("Fetching CSV diamonds")
    return {
        "diamonds": [],
        "pagination": {}
    }


async def get_vdb_diamonds(query_params: dict, config: dict):
    logger.info("Fetching VDB diamonds")
    return {
        "diamonds": [],
        "pagination": {}
    }