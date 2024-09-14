from robocorp.tasks import task
from robocorp import browser

from RPA.Tables import Tables
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Archive import Archive

# Global variables
http = HTTP()
library = Tables()

@task
def order_robots_from_RobotSpareBin():
    global page
    page = browser.page()
    # browser.configure(
    #     slowmo=100
    # )
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """

    
    # Execute the functions in order
    open_order_website()
    click_popup()
    download_csv_file()
    fill_the_form_with_CSV_data()
    archive_receipts()


# Functions declared in execution order

def open_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def click_popup():
    """Fills in the login form and clicks the 'Log in' button"""
    page.click("button:text('OK')")

def download_csv_file():
    """Downloads CSV file from the given URL"""
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def fill_the_form_with_CSV_data():
    """Reads the file and places it into variable"""
    orders = library.read_table_from_csv(
        "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"]
    )
    for row in orders:

        page.select_option("#head", f"{row['Head']}")
        page.check(f"#id-body-{row['Body']}")
        page.fill(".form-control", f"{row['Legs']}")
        page.fill("#address", f"{row['Address']}")
        page.click("button:text('Preview')")
        page.click("button:text('Order')")

        while (True):
            error = page.query_selector(".alert-danger")
            if (error):
                page.wait_for_timeout(1000)
                page.click("button:text('Order')")
            else:
                break

        store_receipt_as_pdf(row["Order number"])
        screenshot_robot(row["Order number"])
        embed_screenshot_to_receipt(f"output/{row['Order number']}.png", f"output/receipts/{row['Order number']}.pdf")

        page.click("button:text('Order another robot')")
        page.click("button:text('OK')")



def store_receipt_as_pdf(order_number):
    print(order_number)
    pdf = PDF()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf.html_to_pdf(order_receipt_html, f"output/receipts/{order_number}.pdf")

def screenshot_robot(order_number):
    locator = page.locator("#robot-preview-image")
    locator.screenshot(path=f"output/{order_number}.png")

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf([screenshot], pdf_file, append=True)

def archive_receipts():
    zip = Archive()
    zip.archive_folder_with_zip("./output", "./output/receipts.zip", compression="bzip2")








# FOR REFERENCE
    #        page.fill("#firstname", sales_rep["First Name"])
    # page.fill("#lastname", sales_rep["Last Name"])
    # page.select_option("#salestarget", str(sales_rep["Sales Target"]))
    # page.fill("#salesresult", str(sales_rep["Sales"]))
    # page.click("text=Submit")            
            
            



