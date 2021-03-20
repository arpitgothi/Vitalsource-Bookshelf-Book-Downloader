import os
import sys
import requests
import lxml.html
from fpdf import FPDF
from PIL import Image


def get_session(email, password, book):
    s = requests.session()

    login_url = 'https://jigsaw.vitalsource.com/login?return=/books/{}/content/image/1.jpg'.format(book)
    login = s.get(login_url)
    login_html = lxml.html.fromstring(login.text)

    hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')
    form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}

    form['user[email]'] = email
    form['user[password]'] = password

    response = s.post(login_url, data=form)

    return s


def convert_images_to_pdf(book):

    
    directory = "{}\\".format(book)

    first_page = Image.open("{}\\0001.jpg".format(book))
    width, height = first_page.size

    pdf = FPDF(unit="pt", format=[width, height])

    d = os.fsencode(directory)

    for file in os.listdir(d):
        filename = os.fsdecode(file)
        pdf.add_page()
        pdf.image("{}{}".format(directory, filename), 0, 0)

    print("Processing PDF. This may take several minutes. Please be calm to get result!!")
    pdf.output("{}.pdf".format(book), "F")


def download_book(email, password, book):

    session = get_session(email, password, book)

    IsValid = True
    page = 1

    if not os.path.exists("{}".format(book)):
        os.makedirs("{}".format(book))
        print("New Directory created!!")

    # download all pages of book. It Will stop once the next page doesn't exist
    while IsValid:

        if page % 10 == 0:
            print("Downloading page {}".format(page))

        url = "https://jigsaw.vitalsource.com/books/{}/content/image/{}.jpg".format(book, page)

        image = session.get(url)

        if image.status_code == requests.codes.ok:
            image_file = open(os.path.join('{}'.format(
                book), "{}.jpg".format(str(page).zfill(4))), 'wb')
            for chunk in image.iter_content(100000):
                image_file.write(chunk)
            image_file.close()
            page += 1
        else:
            print("End of book. Book is {} pages long".format(page))
            IsValid = False

    convert_images_to_pdf(book)


if __name__ == "__main__":
    if len(sys.argv) == 4:
        email = sys.argv[1]
        password = sys.argv[2]
        book = sys.argv[3]
        download_book(email, password, book)
    else:
        print("Usage: python book.py mail_id password book_id")
