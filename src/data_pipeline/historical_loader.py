import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Dict

class DataLeakageError(Exception):
    """Raised when dataset timestamps overlap or violate chronological embargo rules."""
    pass

class HistoricalDataLoader:
    """
    Enforces Strict Chronological Partitioning:
    - 5-Year Training Set (Years 1 to 5)
    - 30-Day Purged Embargo Buffer (clearing all 20-day composite profiles and anchored states)
    - 7-Year Out-of-Sample (OOS) Test Set (Years 6 to 12)
    
    Automated timestamp assertion raises DataLeakageError if any training index overlaps a test index.
    """
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir

    def partition_12year_dataset(
        self, df: pd.DataFrame, timestamp_col: str = "ts"
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Splits a 12-year dataset into 5-year train and 7-year OOS test sets separated by a 30-day embargo.
        """
        if df.empty:
            return df, df

        df = df.sort_values(by=timestamp_col).reset_index(drop=True)
        start_ts = df[timestamp_col].iloc[0]
        train_end_ts = start_ts + pd.DateOffset(years=5)
        embargo_end_ts = train_end_ts + pd.Timedelta(days=30)
        test_start_ts = embargo_end_ts

        train_df = df[df[timestamp_col] < train_end_ts].copy()
        test_df = df[df[timestamp_col] >= test_start_ts].copy()

        # Check for leakage
        if not train_df.empty and not test_df.empty:
            max_train_ts = train_df[timestamp_col].max()
            min_test_ts = test_df[timestamp_col].min()
            
            if max_train_ts >= min_test_ts:
                raise DataLeakageError(
                    f"CRITICAL DATA LEAKAGE: Max train timestamp {max_train_ts} >= Min test timestamp {min_test_ts}"
                )
            
            embargo_gap = (min_test_ts - max_train_ts).days
            if embargo_gap < 30:
                raise DataLeakageError(
                    f"CRITICAL EMBARGO VIOLATION: Embargo gap is {embargo_gap} days, required >= 30 days"
                )

        print(f"Data partitioning successful: Train={len(train_df)} rows, OOS Test={len(test_df)} rows. Embargo gap verified.")
        return train_df, test_df
