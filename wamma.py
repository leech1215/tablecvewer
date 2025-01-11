import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

k = 1

name = input("웹툰의 제목을 입력하세요 : ")

start_url = input("해당 웹툰의 링크를 입력하세요 : ")

if not("https://comic.naver.com/webtoon/detail?titleId=" in start_url):
    k = 0

Id = start_url[45:51]

base_url = f"https://comic.naver.com/webtoon/detail?titleId={Id}&no={{0}}&week=wed"

start_no = int(input("저장 시작 회차: "))
end_no = int(input("저장 종료 회차: "))

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}

base_save_path = os.path.join("saved file", name)

# 폴더 존재 여부 확인
if not os.path.exists(base_save_path):
    os.makedirs(base_save_path)

# 각 페이지 다운로드
for no in range(start_no, end_no + 1):
    folder_name = os.path.join(base_save_path, f"page_{no}")
    if os.path.exists(folder_name):  # 이미 폴더가 존재하면 스킵
        print(f"Page {no}: 이미 저장된 페이지입니다. 다운로드를 건너뜁니다.")
        continue

    os.makedirs(folder_name, exist_ok=True)
    url = base_url.format(no)
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        viewer = soup.find(class_="wt_viewer")

        if viewer:
            img_tags = viewer.find_all("img")
            for idx, img in enumerate(img_tags, start=1):
                img_src = img.get("src")
                if img_src:
                    img_url = urljoin(url, img_src)
                    img_response = requests.get(img_url, headers=headers)

                    if img_response.status_code == 200:
                        img_extension = img_url.split(".")[-1]
                        img_filename = os.path.join(folder_name, f"image_{idx}.{img_extension}")

                        with open(img_filename, "wb") as f:
                            f.write(img_response.content)
                        print(f"Page {no}: {img_filename} 저장 완료.")
        else:
            print(f"Page {no}: 이미지를 찾을 수 없습니다.")
            k = 0
    else:
        print(f"Page {no}: 요청 실패. 상태 코드 {response.status_code}")
        k = 0

# 표지 이미지 다운로드
cover_file = os.path.join(base_save_path, "표지.jpg")
if not os.path.exists(cover_file) and k:  # 표지가 없을 때만 다운로드
    new_name = name.replace(" ", "+")
    search_url = f"https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={new_name}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    detail_info = soup.find(class_="detail_info")
    if detail_info:
        img_tag = detail_info.find("a").find("img")
        if img_tag and "src" in img_tag.attrs:
            image_url = img_tag["src"]
            img_response = requests.get(image_url, stream=True)
            if img_response.status_code == 200:
                with open(cover_file, "wb") as file:
                    for chunk in img_response.iter_content(1024):
                        file.write(chunk)
                print(f"표지 이미지가 {cover_file}에 저장되었습니다.")
else:
    print("표지 이미지를 저장하지 않습니다.")

# 뷰어 HTML 생성
viewer_file = os.path.join(base_save_path, "image_viewer.html")
if not os.path.exists(viewer_file) and k:  # 뷰어가 없을 때만 생성
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Viewer With Navigation</title>
    <style>
        body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        display: flex;
        height: 100vh;
        overflow: hidden;
        }
        #sidebar {
        width: 250px;
        background-color: #f4f4f4;
        border-right: 1px solid #ddd;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        height: 100vh;
        }
        #sidebar h3 {
        margin: 0;
        padding: 10px;
        text-align: center;
        }
        #sidebar-search {
        padding: 10px;
        background-color: #fff;
        border-bottom: 1px solid #ddd;
        display: flex;
        justify-content: center;
        }
        #page-search {
        padding: 5px;
        width: 80%;
        box-sizing: border-box;
        border: 1px solid #ddd;
        border-radius: 4px;
        outline: none;
        }
        #page-search:focus {
        border-color: #007BFF;
        }
        #page-list {
        flex: 1;
        overflow-y: auto;
        padding: 10px;
        max-height: calc(100vh - 60px);
        }
        .page-item {
        cursor: pointer;
        padding: 8px;
        margin: 5px 0;
        background-color: #fff;
        border: 1px solid #ddd;
        border-radius: 3px;
        text-align: center;
        transition: background-color 0.3s;
        }
        .page-item:hover {
        background-color: #e0e0e0;
        }
        #main-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow-y: auto;
        }
        #input-section {
        padding: 10px;
        background-color: #f4f4f4;
        border-bottom: 1px solid #ddd;
        position: sticky;
        top: 0;
        z-index: 1000;
        text-align: center;
        }
        #navigation-buttons {
        margin-top: 10px;
        }
        #image-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0;
        margin: 0;
        overflow-y: auto;
        }
        .image-item {
        margin: 0;
        padding: 0;
        }
        .image-item img {
        display: block;
        margin: 0;
        border: 0;
        }
        #error-message {
        color: red;
        font-size: 10px;
        margin-top: 14px;
        display: none;
        }
    </style>
    </head>
    <body>
    <div id="sidebar">
        <h3>Page List</h3>
        <div id="sidebar-search">
        <input type="text" id="page-search" placeholder="Search for a page..." oninput="filterPageList()">
        </div>
        <div id="page-list"></div>
    </div>
    <div id="main-content">
        <div id="input-section">
        <label for="page-number">Enter page number:</label>
        <input type="number" id="page-number" min="1" placeholder="Page number">
        <button onclick="loadImages()">Load Images</button>
        <div id="navigation-buttons">
            <button onclick="goToPreviousPage()">Previous Page</button>
            <button onclick="goToNextPage()">Next Page</button>
        </div>
        <div id="error-message"></div>
        </div>
        <div id="image-container"></div>
    </div>

    <script>
        const totalPages = 2000; // Max pages to check
        const maxImages = 200; // Max images per page
        let validPages = []; // To store pages with existing images

        async function generatePageList() {
        const pageList = document.getElementById('page-list');
        pageList.innerHTML = '';
        validPages = []; // Reset valid pages

        for (let i = 1; i <= totalPages; i++) {
            const imagePath = `page_${i}/image_1.jpg`; // Check for the first image in the page
            const isValid = await checkImageExists(imagePath);

            if (isValid) {
            validPages.push(i);
            const pageItem = document.createElement('div');
            pageItem.className = 'page-item';
            pageItem.textContent = `Page ${i}`;
            pageItem.onclick = () => {
                document.getElementById('page-number').value = i;
                loadImages();
            };
            pageList.appendChild(pageItem);
            }
        }

        loadInitialPage();
        }

        function loadInitialPage() {
        const lastVisitedPage = localStorage.getItem('lastVisitedPage');
        const initialPage = lastVisitedPage ? Number(lastVisitedPage) : 1;
        document.getElementById('page-number').value = initialPage;
        loadImages();
        }

        function checkImageExists(url) {
        return new Promise(resolve => {
            const img = new Image();
            img.onload = () => resolve(true);
            img.onerror = () => resolve(false);
            img.src = url;
        });
        }

        function filterPageList() {
        const searchValue = document.getElementById('page-search').value.toLowerCase();
        const pages = document.querySelectorAll('.page-item');
        pages.forEach(page => {
            if (page.textContent.toLowerCase().includes(searchValue)) {
            page.style.display = '';
            } else {
            page.style.display = 'none';
            }
        });
        }

        function loadImages() {
        const pageNumber = parseInt(document.getElementById('page-number').value, 10);
        const imageContainer = document.getElementById('image-container');
        const errorMessage = document.getElementById('error-message');
        imageContainer.innerHTML = '';
        errorMessage.style.display = 'none';

        if (!validPages.includes(pageNumber)) {
            errorMessage.textContent = 'Please enter a valid page number.';
            errorMessage.style.display = 'block';
            return;
        }

        localStorage.setItem('lastVisitedPage', pageNumber);
        const basePath = `page_${pageNumber}`;
        let imageFound = false;

        for (let i = 1; i <= maxImages; i++) {
            const imagePath = `${basePath}/image_${i}.jpg`;
            const imgElement = document.createElement('img');
            imgElement.src = imagePath;
            imgElement.alt = `Image ${i}`;
            imgElement.loading = 'lazy';
            imgElement.onerror = () => {
            if (!imageFound && i === maxImages) {
                errorMessage.textContent = 'No images found for this page.';
                errorMessage.style.display = 'block';
            }
            imgElement.remove();
            };
            imgElement.onload = () => {
            imageFound = true;
            };
            const divElement = document.createElement('div');
            divElement.className = 'image-item';
            divElement.appendChild(imgElement);
            imageContainer.appendChild(divElement);
        }
        }

        function goToPreviousPage() {
        const pageNumberInput = document.getElementById('page-number');
        let currentPage = parseInt(pageNumberInput.value, 10) || 1;
        if (currentPage > 1) {
            pageNumberInput.value = currentPage - 1;
            loadImages();
        }
        }

        function goToNextPage() {
        const pageNumberInput = document.getElementById('page-number');
        let currentPage = parseInt(pageNumberInput.value, 10) || 1;
        if (currentPage < totalPages) {
            pageNumberInput.value = currentPage + 1;
            loadImages();
        }
        }

        document.addEventListener('DOMContentLoaded', generatePageList);
    </script>
    </body>
    </html>
    """
    with open(viewer_file, "w", encoding="utf-8") as file:
        file.write(html_content)
    print(f"뷰어가 {viewer_file}에 생성되었습니다.")
else:
    print("뷰어를 생성하지 않습니다.")

if not k:
    for no in range(start_no, end_no + 1):
        os.rmdir(os.path.join(base_save_path, f"page_{no}"))
    os.rmdir(base_save_path)

print("모든 작업을 완료했습니다. 잠시 후 자동으로 종료됩니다.")
time.sleep(5)