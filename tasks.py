from robocorp.tasks import task
from robocorp import browser
from RPA.Tables import Tables
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries inc.
    Saves the order HTML receipt as a PDF file
    Saves the Screenshot of the ordered Robot
    Embeds the screenshot of the robot to the pdf receipt
    creates ZIP archive of the receipt and the image
    """
    browser.configure(
        slowmo=100,
    )
    orders = get_orders()
    get_to_intranet()
    process_orders(orders)
    archive_receipts()
    


def get_orders():
    """ Downloads the orders file """
    http = HTTP()
    order_list = http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True, target_file="orders.csv")
    table = Tables()
    orders = table.read_table_from_csv("orders.csv")
    return orders

def process_orders(orders):
    i=1
    for order in orders:
        fill_the_form(order)
        page = browser.page()
        page.click("button:text('Preview')")
        page.click("button:text('Order')")
        while(page.locator(".alert-danger").is_visible()):
            page.click("button:text('Order')")
        store_receipt_as_pdf(i)
        i += 1
        page.click("button:text('Order another robot')")
        click_modal_away()


def fill_the_form(order):
    """fills the form on the website for the given order"""
    page = browser.page()
    #choose head
    page.select_option("#head", value=order['Head'])
    #choose body
    selector = "input[id=id-body-"+order['Body']+"]"
    page.set_checked(selector, True)
    #choose number of legs
    page.fill("input[placeholder='Enter the part number for the legs']", order['Legs'])
    #insert address
    page.fill("#address", order['Address'])

def get_to_intranet():
    """Opens a browser and directs to robotsparebinindustries website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    click_modal_away()

def click_modal_away():
    """gets rid of the annoying modal that pops up"""
    page = browser.page()
    page.click("button:text('I guess so...')")


def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(receipt, "output/receipts/receipt"+str(order_number)+".pdf")
    screenshot_robot(order_number)
    embed_screenshot_to_pdf("output/receipts/receipt"+str(order_number)+".png", "output/receipts/receipt"+str(order_number)+".pdf")
    

def screenshot_robot(order_number):
    page = browser.page()
    page.locator("#robot-preview-image").screenshot(path="output/receipts/receipt"+str(order_number)+".png")
    

def embed_screenshot_to_pdf(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)
    

def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip("output/receipts", "output/robot-Archive.zip", exclude="*.png")
