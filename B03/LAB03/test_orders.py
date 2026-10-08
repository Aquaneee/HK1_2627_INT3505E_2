import unittest
from appextended import app

class TestOrdersApi(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_cursor_with_sort_asc(self):
        """Test phân trang kết hợp sort tăng dần theo total"""
        # Lấy trang 1 với limit=2
        res1 = self.client.get('/orders?sort=total&limit=2')
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        self.assertEqual(len(data1["data"]), 2)
        next_cursor = data1["next_cursor"]
        self.assertIsNotNone(next_cursor)

        # Lấy trang 2 dùng next_cursor vừa nhận
        res2 = self.client.get(f'/orders?sort=total&limit=2&cursor={next_cursor}')
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertEqual(len(data2["data"]), 2)

        # Kiểm tra tính liên tục của sort: phần tử đầu trang 2 phải >= phần tử cuối trang 1
        last_total_page1 = data1["data"][-1]["total"]
        first_total_page2 = data2["data"][0]["total"]
        self.assertGreaterEqual(first_total_page2, last_total_page1)

    def test_cursor_with_sort_desc(self):
        """Test phân trang kết hợp sort giảm dần (-total)"""
        res1 = self.client.get('/orders?sort=-total&limit=2')
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        next_cursor = data1["next_cursor"]

        res2 = self.client.get(f'/orders?sort=-total&limit=2&cursor={next_cursor}')
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()

        # Phần tử đầu trang 2 phải <= phần tử cuối trang 1
        self.assertLessEqual(data2["data"][0]["total"], data1["data"][-1]["total"])

    def test_invalid_cursor_returns_400(self):
        """Test cursor sai format trả về mã lỗi 400"""
        res = self.client.get('/orders?cursor=not-a-valid-cursor')
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.get_json())

if __name__ == '__main__':
    unittest.main()