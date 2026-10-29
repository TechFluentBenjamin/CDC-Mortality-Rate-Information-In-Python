import unittest
#imported unittest.mock for mocking input and output in tests
from unittest.mock import patch
import pandas as pd
import numpy as np
#imported io and sys for capturing printed output during tests
import io
import sys
#imported main to test the menu functionality
import main


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

#Added a test for main.py
class TestMainMenu(unittest.TestCase):
    @patch('builtins.input', side_effect=['1', '4'])
    @patch('program_dashboard.run_dashboard')
    def test_menu_exit_flow(self, mock_dashboard, mock_input):
        """Test that selecting option 1 then 4 exits the program correctly."""
        # We use side_effect to simulate user typing '1' then '4'
        # This tests if the loop runs and eventually hits sys.exit()
        with self.assertRaises(SystemExit) as cm:
            main.main()
        
        # Verify that the exit code was 0 (sys.exit(0))
        self.assertEqual(cm.exception.code, 0)
        # Verify that the dashboard function was actually called
        mock_dashboard.assert_called_once()
    @patch('builtins.input', side_effect=['5', '4'])
    def test_invalid_choice(self, mock_input):
        """Test how the program handles an invalid input."""
        # We capture stdout to see if the error message prints
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        with self.assertRaises(SystemExit):
            main.main()
            
        sys.stdout = sys.__stdout__  # Reset redirect
        self.assertIn("Invalid choice", captured_output.getvalue())



if __name__ == "__main__":
    unittest.main()
