import requests
import csv
from bs4 import BeautifulSoup

base_url = "https://www.ketabrah.ir"

def redirect(url):
    result = requests.get(url)
    return BeautifulSoup(result._content, "html.parser")


def processing(hottest_key, hottest_value):
    main_soup = redirect(hottest_value)
    tag_a_title = main_soup.find_all("a", {"class":"title"})
    books = {}

    for a in tag_a_title:
        title = a.find_next("h3")
        books[title.text] = base_url + a.get("href")

    data = []
    for key, value in books.items():
        soup = redirect(value)    
        tag_div = soup.find("div",{"class":"book-details section"})
        trs = tag_div.find_all("tr")
        index = 0
        title = trs[index].find_next("td",{"itemprop":"name"}).text
        author = trs[index + 1].find_next("td").find_next("span").text
        translator = ""
        publisher = ""
        if trs[index + 2].find_next("td").text == "مترجم":
            translator = trs[index + 2].find_next("td").find_next("span").text
            index += 1

        publisher = trs[index + 2].find_next("td").find_next("span").text
        publish_year = trs[index + 3].find_all("td")[1].text
        subject = trs[len(trs) - 1].find_next("a").text

        price = soup.find("span",{"class":"discounted-price"}).text
        rate = soup.find("div",{"class":"rating-options"}).find_next("span").text
        comment_count = soup.find("span", {"class":"comment-count"})
        if comment_count is None:
            comment_count = "0"
        else:
            comment_count = comment_count.text    

        data.append([subject, title, author, translator, publisher, price, publish_year, rate, comment_count])

    # open CSV file in write mode with 9 columns
    with open('output.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['موضوع', 'عنوان', 'نویسنده', 'مترجم', 'ناشر', 'قیمت', 'سال چاپ', 'امتیاز کاربران', 'تعداد نظرات'])
        # write data rows
        for row in data:
            writer.writerow(row)   

    print("End of processing ", hottest_key)         


def iterate(dictionary):
    for key, value in dictionary.items():
        soup = redirect(value)
        tag_a= soup.find_all("a", {"class":"header white"})
        hrefs = {}
        for a in tag_a:
            title = a.find_next("h2")
            hrefs[title.text] = base_url + a.get("href")

        # Get access to the first item of each category 
        hottest_key = list(hrefs.keys())[0]
        hottest_value = list(hrefs.values())[0]

        last_page = find_last_page(hottest_value, 100, 100)
        for page in range(last_page):
            processing(f"{hottest_key} page: {page + 1}", within_url(hottest_value, page))  



def find_last_page(url, x, rate):
    # The url also contains number of the pages
    # so it has to redirect each page with specific url(page-2|page-3|...)
    # thus we have to find the last page of each section
    my_str = within_url(url, x)
    soup = redirect(my_str)
    error = soup.find("div",{"class":"error-box"})

    if rate == 1 and (error is None):
        print(x)
        return x
    else:
        rate //= 2
        if error is not None:
            return find_last_page(url, x - rate, rate)
        else:
            return find_last_page(url, x + rate , rate)     


def within_url(core_str, x):
    my_str = core_str
    substr = "?bt=books"
    inserttxt = f"/page-{x}"

    idx = my_str.index(substr)
    my_str = my_str[:idx] + inserttxt + my_str[idx:]
    return my_str


def main():
    soup = redirect(base_url)
    tag_ul = soup.find("ul", {"class": "categories-menu"})
    options = tag_ul.find_all("li")
    categories = {}
    # sub_options = tag_ul.find_all("div",{"class":"sub-category"})
    # sub_categories = {}

    for li in options[7:]:
        link_element = li.find_next("a")
        categories[link_element.text] = base_url + link_element.get("href")

    
    iterate(categories)


if __name__ == "__main__":
    main()    