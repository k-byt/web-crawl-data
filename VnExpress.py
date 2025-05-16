import csv
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_driver():
    """Thiết lập trình duyệt Chrome với các tùy chọn phù hợp"""
    chrome_options = Options()
    # Bỏ chế độ headless để hiện trình duyệt
    chrome_options.add_argument('--start-maximized')  # Mở rộng cửa sổ
    chrome_options.add_argument('--disable-notifications')  # Tắt thông báo
    chrome_options.add_argument('--disable-popup-blocking')  # Tắt popup
    chrome_options.add_argument('--lang=vi')  # Đặt ngôn ngữ tiếng Việt
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scroll_page(driver, scroll_times=3):
    """Cuộn trang để tải thêm nội dung"""
    for i in range(scroll_times):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Đợi tải nội dung
            print(f"Đã cuộn trang lần {i+1}/{scroll_times}")
        except Exception as e:
            print(f"Lỗi khi cuộn trang: {str(e)}")
            continue

def get_article_data(article):
    """Trích xuất thông tin từ một bài báo"""
    try:
        # Tìm tiêu đề và link
        title_element = article.find_element(By.CSS_SELECTOR, 'h3.title-news a, h2.title-news a, p.title-news a')
        title = title_element.text.strip()
        link = title_element.get_attribute('href')
        
        # Tìm thời gian đăng
        try:
            time_element = article.find_element(By.CSS_SELECTOR, '.time-public, .time, .date')
            publish_time = time_element.text.strip()
        except NoSuchElementException:
            publish_time = "Không có thời gian"
        
        # Kiểm tra dữ liệu hợp lệ
        if not title or not link:
            return None
            
        return {
            'Tiêu đề': title,
            'Thời gian': publish_time,
            'Link': link
        }
    except Exception:
        return None

def save_to_csv(data, filename='vnexpress_articles.csv'):
    """Lưu dữ liệu vào file CSV"""
    try:
        header = ['Tiêu đề', 'Thời gian', 'Link']
        
        # Xóa file cũ nếu tồn tại
        if os.path.exists(filename):
            os.remove(filename)
            
        # Ghi dữ liệu mới
        with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            writer.writerows(data)
            
        print(f'\nĐã lưu thành công {len(data)} bài viết vào file {filename}')
    except Exception as e:
        print(f'\nLỗi khi lưu file CSV: {str(e)}')

def main():
    articles_data = []
    seen_links = set()
    successful_count = 0
    failed_count = 0
    
    try:
        # Khởi tạo trình duyệt
        print("Đang khởi tạo trình duyệt Chrome...")
        driver = setup_driver()
        
        # Truy cập trang web
        url = "https://vnexpress.net/thoi-su"
        print(f"\nĐang truy cập {url}...")
        driver.get(url)
        
        # Đợi trang tải xong
        print("\nĐang đợi trang tải...")
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "width_common"))
            )
        except TimeoutException:
            print("Trang tải quá lâu! Đang thử tiếp tục...")
        
        # Cuộn trang để tải thêm bài viết
        print("\nĐang tải thêm bài viết...")
        scroll_page(driver)
        
        # Lấy danh sách bài viết
        articles = driver.find_elements(By.CSS_SELECTOR, '.item-news, .width_common article')
        total_articles = len(articles)
        print(f"\nĐã tìm thấy {total_articles} bài viết")
        
        # Thu thập dữ liệu
        print("\nBắt đầu thu thập dữ liệu...")
        for index, article in enumerate(articles, 1):
            print(f"\nĐang xử lý bài {index}/{total_articles}...", end=" ")
            
            data = get_article_data(article)
            if data and data['Link'] not in seen_links:
                seen_links.add(data['Link'])
                articles_data.append(data)
                successful_count += 1
                print("✓ Thành công")
                print(f"Tiêu đề: {data['Tiêu đề']}")
                print(f"Thời gian: {data['Thời gian']}")
                print(f"Link: {data['Link']}")
                print("-" * 60)
            else:
                failed_count += 1
                print("✗ Bỏ qua")
        
        # Hiển thị thống kê
        print("\n=== Thống kê ===")
        print(f"Tổng số bài viết đã quét: {total_articles}")
        print(f"Thành công: {successful_count}")
        print(f"Bỏ qua/Lỗi: {failed_count}")
        
        # Lưu dữ liệu
        if articles_data:
            save_to_csv(articles_data)
        else:
            print("\nKhông có dữ liệu để lưu")
            
    except Exception as e:
        print(f"\nLỗi: {str(e)}")
        
    finally:
        input("\nNhấn Enter để đóng trình duyệt...")
        driver.quit()

if __name__ == "__main__":
    main()
    