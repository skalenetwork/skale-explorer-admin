import json
import logging
from datetime import time, datetime
from decimal import Decimal
from collections import Counter

import psycopg2
from psycopg2.extras import RealDictCursor

from admin.configs.meta import get_schain_meta
from admin.statistics.models import StatsDatabase

logger = logging.getLogger(__name__)


def collect_schain_stats(schain_name):
    schain_meta = get_schain_meta(schain_name)
    conn = psycopg2.connect(
        host="localhost",
        database="explorer",
        user="postgres",
        port=schain_meta['db_port'])

    queries = ['''
    SELECT
        count(case when (NOW()::date-blocks.timestamp::date) < 7 THEN 1 else null end) tx_count_7_days,
        count(DISTINCT case when (NOW()::date-blocks.timestamp::date) < 7 THEN transactions.hash else null end) unique_tx_count_7_days,
        count(DISTINCT case when (NOW()::date-blocks.timestamp::date) < 7 THEN from_address_hash else null end) user_count_7_days,
        sum(DISTINCT case when (NOW()::date-blocks.timestamp::date) < 7 THEN transactions.gas_used else 0 end) gas_total_used_7_days_gwei,
        sum(DISTINCT case when (NOW()::date-blocks.timestamp::date) < 7 THEN transactions.gas_used else 0 end) / 1000000000 gas_total_used_7_days_eth ,
        count(case when (NOW()::date-blocks.timestamp::date) < 30 THEN 1 else null end) tx_count_30_days,
        count(DISTINCT case when (NOW()::date-blocks.timestamp::date) < 30 THEN transactions.hash else null end) unique_tx_count_30_days,
        count(DISTINCT case when (NOW()::date-blocks.timestamp::date) < 30 THEN from_address_hash else null end) user_count_30_days,
        sum(DISTINCT case when (NOW()::date-blocks.timestamp::date) < 30 THEN transactions.gas_used else 0 end) gas_total_used_30_days_gwei,
        sum(DISTINCT case when (NOW()::date-blocks.timestamp::date) < 30 THEN transactions.gas_used else 0 end) / 1000000000 gas_total_used_30_days_eth
    FROM transactions
    inner join blocks on blocks.number = transactions.block_number
    ''', '''
    SELECT 
        count(1) tx_count_24_hours,
        count(DISTINCT transactions.hash) unique_tx_24_hours,
        count(DISTINCT from_address_hash) user_count_24_hours, 
        sum(DISTINCT transactions.gas_used) gas_total_used_24_hours_gwei, 
        sum(DISTINCT transactions.gas_used) / 1000000000 gas_total_used_24_hours_eth,
        TO_CHAR(blocks.timestamp :: DATE, 'yyyymmdd') as TX_DATE
    FROM transactions
    inner join blocks on blocks.number = transactions.block_number
    where NOW()::date-blocks.timestamp::date < 7
    GROUP by TO_CHAR(blocks.timestamp :: DATE, 'yyyymmdd')
    ''', '''
    SELECT
        count(case when (NOW()::date-timestamp::date) <= 0 THEN 1 else null end) block_count_24_hours,
        count(case when (NOW()::date-timestamp::date) < 7 THEN 1 else null end) block_count_7_days,
        count(case when (NOW()::date-timestamp::date) < 30 THEN 1 else null end) block_count_30_days
    FROM blocks
    ''', '''
        SELECT MAX(cnt_per_second) max_tps_last_24_hours
        from (
          SELECT count(1) cnt_per_second,
            TO_CHAR(blocks.timestamp :: DATE,  'YYYY-MM-DD HH:MM:SS')
          from transactions
          inner join blocks on blocks.number = transactions.block_number
          WHERE
            NOW()::date-blocks.timestamp::date < 7
          group by 
            TO_CHAR(blocks.timestamp :: DATE,  'YYYY-MM-DD HH:MM:SS')
        ) as foo
    ''', '''
        SELECT MAX(cnt_per_second) max_tps_last_7_days
        from (
          SELECT count(1) cnt_per_second,
            TO_CHAR(blocks.timestamp :: DATE,  'YYYY-MM-DD HH:MM:SS')
          from transactions
          inner join blocks on blocks.number = transactions.block_number
          WHERE
            NOW()::date-blocks.timestamp::date < 7
          group by 
            TO_CHAR(blocks.timestamp :: DATE,  'YYYY-MM-DD HH:MM:SS')
        ) as foo
    ''', '''
        SELECT MAX(cnt_per_second) max_tps_last_30_days
        from (
          SELECT count(1) cnt_per_second,
            TO_CHAR(blocks.timestamp :: DATE,  'YYYY-MM-DD HH:MM:SS')
          from transactions
          inner join blocks on blocks.number = transactions.block_number
          WHERE
            NOW()::date-blocks.timestamp::date < 30
          group by 
            TO_CHAR(blocks.timestamp :: DATE,  'YYYY-MM-DD HH:MM:SS')
        ) as foo
    ''', '''
        SELECT 
            count(distinct hash) tx_count_total, 
            count(distinct from_address_hash) user_count_total
        from transactions
    ''']

    raw_result = {}
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    for query in queries:
        cursor.execute(query)
        raw_result.update(dict(cursor.fetchall()[0]))
    raw_result.pop('tx_date')
    result = {
        key: float(raw_result[key]) if type(raw_result[key]) == Decimal else raw_result[key]
        for key in raw_result
    }
    return result


def update_schains_stats(schain_names):
    db = StatsDatabase()
    total_stats = {}
    for schain in schain_names:
        schain_stats = collect_schain_stats(schain)
        logger.info(f'Stats for {schain}: {schain_stats}')
        total_stats = dict(Counter(total_stats) + Counter(schain_stats))
    logger.info(f'Schains: {len(schain_names)}; total stats: {total_stats}')
    timestamp = time()
    db.add(
        schains_number=len(schain_names),
        timestamp = datetime.fromtimestamp(timestamp),
        **total_stats
    )
    return timestamp
