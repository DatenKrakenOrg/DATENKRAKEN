from typing import Tuple, List, Dict
import pandas as pd
from datetime.datetime import DateTime
from database.orm import Temperature, Humidty, Voc, Noise, SensorType

class IDataFetcher:
    def get_unique_arduino_ids() -> Dict[SensorType, List[int]]:
        """Gets all existing arduino_ids by each sensor type in the gold layer.

        Returns:
            Dict[SensorType, List[int]]: Returns a dictionary indicating each existing arduino id (values) by each sensor type (key)
        """
        raise NotImplementedError()

    def get_newest_bucket(arduino_id: int) -> Tuple[Temperature, Humidty, Voc, Noise]:
        """Gets the newest data point (timebucket) for each sensor type. It maps to a custom orm class since sqlalchemy needs a primary key which the gold layer currently doesn't have (bcs. view).

        Args:
            arduino_id (int): Mandatory filtering by a arduino_id

        Returns:
            Tuple[Temperature, Humidty, Voc, Noise]: Tuple containing a orm object for each sensor type representing the newest (continously, see documentation under database) aggregated data point
        """
        raise NotImplementedError()

    def get_bucket_by_t_interval(sensor_type: SensorType, arduino_id: int, start_date: DateTime, end_date: DateTime) -> pd.DataFrame:
        """Gets all time buckets in a specific time interval by sensor type and arduino id in a form of a pandas.DataFrame.

        Args:
            sensor_type (SensorType): Enum specifying sensor type that should be retrieved.
            arduino_id (int): Integer specifiying arduino_id that should be retrieved.
            start_date (DateTime): Start date of time buckets (start_date <= data point <= end_date)
            end_date (DateTime): End date of time buckets (start_date <= data point <= end_date)

        Returns:
            pd.DataFrame: pandas.DataFrame containing data specified by function parameters. Columns: bucket_time, avg_value_in_bucket
        """
        raise NotImplementedError()
    
