import unittest
import pandas as pd
import numpy as np


# This represents the logic inside your Program 2
def detect_anomalies(df):
    groups = df.groupby("Age Group")["Death Rate"]
    q1 = groups.transform("quantile", q=0.25)
    q3 = groups.transform("quantile", q=0.75)
    iqr = q3 - q1
    df["Lower Threshold"] = q1 - 1.5 * iqr
    df["Upper Threshold"] = q3 + 1.5 * iqr
    df["Anomaly"] = (df["Death Rate"] < df["Lower Threshold"]) | (
        df["Death Rate"] > df["Upper Threshold"]
    )
    return df


class TestMortalityLogic(unittest.TestCase):

    def setUp(self):
        """Create a tiny 'fake' dataset for testing."""
        data = {
            "Age Group": ["1-4 Years", "1-4 Years", "1-4 Years", "1-4 Years"],
            "Year": [2020, 2021, 2022, 2023],
            "Death Rate": [10.0, 10.5, 100.0, 10.2],
        }
        self.test_df = pd.DataFrame(data)

    def test_anomaly_detection(self):
        """Test if the math correctly identifies the outlier."""
        result_df = detect_anomalies(self.test_df)

        # Check if the 3rd row (index 2) is flagged as an anomaly
        self.assertTrue(
            result_df.loc[2, "Anomaly"], "The high death rate should be flagged as True"
        )
        # Check if a normal row is NOT flagged
        self.assertFalse(
            result_df.loc[0, "Anomaly"], "A normal death rate should be False"
        )

    def test_column_types(self):
        """Test that Death Rate remains a float after processing."""
        result_df = detect_anomalies(self.test_df)
        self.assertEqual(result_df["Death Rate"].dtype, np.float64)


if __name__ == "__main__":
    unittest.main()
