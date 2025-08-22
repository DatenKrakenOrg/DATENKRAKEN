from typing import Tuple, List, Dict
from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime
from sqlalchemy.sql import select
from database.sql.orm import (
    Temperature as TemperatureORM,
    Humidity as HumidityORM,
    Voc as VocORM,
    Noise as NoiseORM,
)
from database.orm import Temperature, Humidity, Voc, Noise, SensorType
from database.sql.engine import commit_select_scalar, commit_select


class IDataFetcher(ABC):
    @abstractmethod
    def get_unique_arduino_ids(self) -> Dict[SensorType, List[str]]:
        """Gets all existing arduino_ids by each sensor type in the gold layer.

        Returns:
            Dict[SensorType, List[str]]: Returns a dictionary indicating each existing arduino id (values) by each sensor type (key)
        """
        raise NotImplementedError()

    @abstractmethod
    def get_newest_bucket(
        self, arduino_id: str
    ) -> Tuple[Temperature, Humidity, Voc, Noise]:
        """Gets the newest data point (timebucket) for each sensor type. It maps to a custom orm class since sqlalchemy needs a primary key which the gold layer currently doesn't have (bcs. view).

        Args:
            arduino_id (str): Mandatory filtering by a arduino_id

        Returns:
            Tuple[Temperature, Humidity, Voc, Noise]: Tuple containing a orm object for each sensor type representing the newest (continously, see documentation under database) aggregated data point
        """
        raise NotImplementedError()

    @abstractmethod
    def get_bucket_by_t_interval(
        self,
        sensor_type: SensorType,
        arduino_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:
        """Gets all time buckets in a specific time interval by sensor type and arduino id in a form of a pandas.DataFrame.

        Args:
            sensor_type (SensorType): Enum specifying sensor type that should be retrieved.
            arduino_id (str): String specifiying arduino_id that should be retrieved.
            start_date (DateTime): Start date of time buckets (start_date <= data point <= end_date)
            end_date (DateTime): End date of time buckets (start_date <= data point <= end_date)

        Returns:
            pd.DataFrame: pandas.DataFrame containing data specified by function parameters. Columns: bucket_time, avg_value_in_bucket
        """
        raise NotImplementedError()


class DataFetcher(IDataFetcher):
    def get_unique_arduino_ids(self) -> Dict[SensorType, List[str]]:
        """Gets all existing arduino_ids by each sensor type in the gold layer.

        Returns:
            Dict[SensorType, List[str]]: Returns a dictionary indicating each existing arduino id (values) by each sensor type (key)
        """
        stmt_temp = select(TemperatureORM.arduino_id).distinct()
        stmt_hum = select(HumidityORM.arduino_id).distinct()
        stmt_voc = select(VocORM.arduino_id).distinct()
        stmt_noise = select(NoiseORM.arduino_id).distinct()

        return {
            SensorType.TEMPERATURE: commit_select_scalar(stmt_temp),
            SensorType.HUMIDITY: commit_select_scalar(stmt_hum),
            SensorType.VOC: commit_select_scalar(stmt_voc),
            SensorType.NOISE: commit_select_scalar(stmt_noise),
        }

    def get_newest_bucket(
        self, arduino_id: str
    ) -> Tuple[Temperature, Humidity, Voc, Noise]:
        """Gets the newest data point (timebucket) for each sensor type. It maps to a custom orm class since sqlalchemy needs a primary key which the gold layer currently doesn't have (bcs. view).

        Args:
            arduino_id (str): Mandatory filtering by a arduino_id

        Returns:
            Tuple[Temperature, Humidity, Voc, Noise]: Tuple containing a orm object for each sensor type representing the newest (continously, see documentation under database) aggregated data point
        """
        stmt_temp = (
            select(TemperatureORM)
            .where(TemperatureORM.arduino_id == arduino_id)
            .order_by(TemperatureORM.bucket_time.desc())
            .limit(1)
        )
        stmt_hum = (
            select(HumidityORM)
            .where(HumidityORM.arduino_id == arduino_id)
            .order_by(HumidityORM.bucket_time.desc())
            .limit(1)
        )
        stmt_voc = (
            select(VocORM)
            .where(VocORM.arduino_id == arduino_id)
            .order_by(VocORM.bucket_time.desc())
            .limit(1)
        )
        stmt_noise = (
            select(NoiseORM)
            .where(NoiseORM.arduino_id == arduino_id)
            .order_by(NoiseORM.bucket_time.desc())
            .limit(1)
        )

        result_temp_list = commit_select_scalar(stmt_temp)
        result_hum_list = commit_select_scalar(stmt_hum)
        result_voc_list = commit_select_scalar(stmt_voc)
        result_noise_list = commit_select_scalar(stmt_noise)

        result_temp = (
            Temperature(bucket_time=None, arduino_id=None, avg_value_in_bucket=None)
            if len(result_temp_list) == 0
            else result_temp_list[0]
        )
        result_hum = (
            Humidity(bucket_time=None, arduino_id=None, avg_value_in_bucket=None)
            if len(result_hum_list) == 0
            else result_hum_list[0]
        )
        result_voc = (
            Voc(bucket_time=None, arduino_id=None, avg_value_in_bucket=None)
            if len(result_voc_list) == 0
            else result_voc_list[0]
        )
        result_noise = (
            Noise(bucket_time=None, arduino_id=None, avg_value_in_bucket=None)
            if len(result_noise_list) == 0
            else result_noise_list[0]
        )

        return (
            Temperature(
                bucket_time=result_temp.bucket_time,
                arduino_id=result_temp.arduino_id,
                avg_value_in_bucket=result_temp.avg_value_in_bucket,
            ),
            Humidity(
                bucket_time=result_hum.bucket_time,
                arduino_id=result_hum.arduino_id,
                avg_value_in_bucket=result_hum.avg_value_in_bucket,
            ),
            Voc(
                bucket_time=result_voc.bucket_time,
                arduino_id=result_voc.arduino_id,
                avg_value_in_bucket=result_voc.avg_value_in_bucket,
            ),
            Noise(
                bucket_time=result_noise.bucket_time,
                arduino_id=result_noise.arduino_id,
                avg_value_in_bucket=result_noise.avg_value_in_bucket,
            ),
        )

    def get_bucket_by_t_interval(
        self,
        sensor_type: SensorType,
        arduino_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:
        """Gets all time buckets in a specific time interval by sensor type and arduino id in a form of a pandas.DataFrame.

        Args:
            sensor_type (SensorType): Enum specifying sensor type that should be retrieved.
            arduino_id (str): String specifiying arduino_id that should be retrieved.
            start_date (DateTime): Start date of time buckets (start_date <= data point <= end_date)
            end_date (DateTime): End date of time buckets (start_date <= data point <= end_date)

        Returns:
            pd.DataFrame: pandas.DataFrame containing data specified by function parameters. Columns: bucket_time, avg_value_in_bucket
        """
        model_by_type = {
            SensorType.TEMPERATURE: TemperatureORM,
            SensorType.HUMIDITY: HumidityORM,
            SensorType.VOC: VocORM,
            SensorType.NOISE: NoiseORM,
        }
        model = model_by_type[sensor_type]

        if model is None:
            raise ValueError(f"Unsupported sensor_type: {sensor_type}")

        stmt = (
            select(
                model.bucket_time.label("bucket_time"),
                model.avg_value_in_bucket.label("avg_value_in_bucket"),
            )
            .where(
                model.arduino_id == arduino_id,
                model.bucket_time >= start_date,
                model.bucket_time <= end_date,
            )
            .order_by(model.bucket_time.desc())
        )

        rows = commit_select(stmt)
        if not rows:
            return pd.DataFrame(columns=["bucket_time", "avg_value_in_bucket"])

        data = [(r[0], r[1]) for r in rows]
        df = pd.DataFrame(data, columns=["bucket_time", "avg_value_in_bucket"])

        # Convert to datetime IF pandas recognizes bucket_time as object (f.e. string)
        if df["bucket_time"].dtype == "object":
            df["bucket_time"] = pd.to_datetime(
                df["bucket_time"], utc=False, errors="coerce"
            )

        return df
