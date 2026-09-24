import unittest
import datetime as dt

from history_extension import audit_month, cached_or_fetch
from data_pipeline import UTC


class ExtensionTests(unittest.TestCase):
    def row(self):
        return {'utc_epoch':int(dt.datetime(2018,1,2,tzinfo=UTC).timestamp())}

    def test_holdout_rejected_before_network(self):
        with self.assertRaises(ValueError):
            cached_or_fetch(2025,1,'BID')

    def test_good_basic_month(self):
        self.assertEqual(audit_month(2018,1,[self.row()],[]),[])

    def test_bad_geometry_quarantined(self):
        self.assertIn('ohlc_geometry',audit_month(2018,1,[self.row()],[{}]))

    def test_wrong_range_and_duplicate(self):
        row=self.row()
        result=audit_month(2018,2,[row,row],[])
        self.assertIn('timestamp_range_or_alignment',result)
        self.assertIn('timestamp_order_or_duplicate',result)


if __name__ == '__main__':
    unittest.main()
