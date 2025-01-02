from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv
from datetime import datetime

def highlight_element(driver, element):
    """Highlight an element temporarily"""
    original_style = element.get_attribute('style')
    driver.execute_script("""
        arguments[0].style.border = '2px solid red';
        arguments[0].style.backgroundColor = 'yellow';
    """, element)
    return original_style

def restore_element_style(driver, element, original_style):
    """Restore element's original style"""
    driver.execute_script(f"arguments[0].style = '{original_style}';", element)

def get_element_xpath(driver, element):
    """Generate a general XPath for similar elements using JavaScript"""
    script = """
    function getXPath(element) {
        // Try to find common class names that might identify similar elements
        let classes = Array.from(element.classList);
        if (classes.length > 0) {
            // Try each class to find one that matches multiple similar elements
            for (let className of classes) {
                let elements = document.getElementsByClassName(className);
                if (elements.length > 1) {
                    return `//*[contains(@class, '${className}')]`;
                }
            }
        }
        
        // If no suitable class found, try by tag name and similar structure
        let tag = element.tagName.toLowerCase();
        let parent = element.parentElement;
        
        if (parent) {
            // Look for siblings with same tag
            let siblings = parent.getElementsByTagName(tag);
            if (siblings.length > 1) {
                // If there are multiple similar elements, use a more general xpath
                if (parent.id) {
                    return `//*[@id='${parent.id}']//${tag}`;
                } else {
                    return `//${tag}`;
                }
            }
        }
        
        // Fallback to a basic tag-based selector
        return `//${tag}`;
    }
    return getXPath(arguments[0]);
    """
    return driver.execute_script(script, element)

def get_next_page_xpath(driver):
    """Let user select the next page button and return its XPath"""
    print("\nNow, please select the 'Next Page' button:")
    print("1. Hover over the next page button/link")
    print("2. Click it")
    print("3. Press Enter in the terminal")
    
    # Add event listeners for mouseover and click
    driver.execute_script("""
        window.selectedElement = null;
        document.addEventListener('mouseover', function(e) {
            if (e.target.style) {
                e.target.oldStyle = e.target.style.cssText;
                e.target.style.border = '2px solid red';
                e.target.style.backgroundColor = 'yellow';
            }
        });
        document.addEventListener('mouseout', function(e) {
            if (e.target.oldStyle !== undefined) {
                e.target.style.cssText = e.target.oldStyle;
            }
        });
        document.addEventListener('click', function(e) {
            e.preventDefault();
            window.selectedElement = e.target;
        }, true);
    """)
    
    input("Press Enter after clicking the 'Next Page' button...")
    
    # Get the selected element
    next_button = driver.execute_script("return window.selectedElement;")
    if not next_button:
        return None
        
    try:
        return get_element_xpath(driver, next_button)
    except Exception as e:
        print(f"Error getting next button XPath: {str(e)}")
        return None

def collect_page_data(driver, selected_elements):
    """Collect data from current page"""
    data = []
    all_elements = {}
    max_items = 0
    
    # Get all elements for each selected type
    for label, xpath in selected_elements:
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            all_elements[label] = [e.text.strip() for e in elements if e.text.strip()]
            max_items = max(max_items, len(all_elements[label]))
        except Exception as e:
            print(f"Error finding elements for {label}: {str(e)}")
            all_elements[label] = []
    
    # Combine data from all elements
    for i in range(max_items):
        item_data = {}
        for label in all_elements:
            try:
                item_data[label] = all_elements[label][i] if i < len(all_elements[label]) else ""
            except:
                item_data[label] = ""
        if any(item_data.values()):  # Only add if at least one value exists
            data.append(item_data)
    
    return data

def main():
    driver = None
    try:
        # Initialize the webdriver with options
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()

        # Get URL from user
        url = input("Enter the website URL: ")
        driver.get(url)

        # Get maximum number of page that is to be navigated
        max_pages = int(input("Enter Maximum number fo page that needs to be scrapped: "))
        
        # Wait for page to load
        time.sleep(5)  # Increased wait time
        
        # List to store selected elements' XPaths and labels
        selected_elements = []
        
        print("\nFirst, select the elements you want to scrape from each product:")
        while True:
            print("\nSelect an element on the page by clicking it.")
            print("Instructions:")
            print("1. Move your mouse over elements to see them highlighted")
            print("2. Click on the element you want to select")
            print("3. Enter a label for the selected element (e.g., 'product_name', 'price')")
            print("4. Type 'done' when you've selected all elements\n")
            
            # Add event listeners for mouseover and click
            driver.execute_script("""
                window.selectedElement = null;
                document.addEventListener('mouseover', function(e) {
                    if (e.target.style) {
                        e.target.oldStyle = e.target.style.cssText;
                        e.target.style.border = '2px solid red';
                        e.target.style.backgroundColor = 'yellow';
                    }
                });
                document.addEventListener('mouseout', function(e) {
                    if (e.target.oldStyle !== undefined) {
                        e.target.style.cssText = e.target.oldStyle;
                    }
                });
                document.addEventListener('click', function(e) {
                    e.preventDefault();
                    window.selectedElement = e.target;
                }, true);
            """)
            
            # Wait for user to click an element
            input("Press Enter after clicking the desired element...")
            
            # Get the selected element
            selected = driver.execute_script("return window.selectedElement;")
            
            if not selected:
                print("No element was selected. Please try again.")
                continue
            
            # Get label from user
            label = input("Enter a label for this element (or 'done' to finish selection): ")
            
            if label.lower() == 'done':
                break
            
            # Get XPath of selected element
            try:
                xpath = get_element_xpath(driver, selected)
                selected_elements.append((label, xpath))
                print(f"Element '{label}' has been selected!")
            except Exception as e:
                print(f"Error selecting element: {str(e)}")
                continue

        # Get the next page button XPath
        print("\nBefore we start collecting data, we need to identify the next page button.")
        next_page_xpath = get_next_page_xpath(driver)
        if not next_page_xpath:
            print("No next page button was selected. Will only scrape the current page.")
        
        # Now collect data from multiple pages
        all_data = []
        page_count = 0

        while page_count < max_pages:
            print(f"\nCollecting data from page {page_count + 1}...")
            
            # Collect data from current page
            page_data = collect_page_data(driver, selected_elements)
            all_data.extend(page_data)
            
            if next_page_xpath:
                try:
                    # Find and click next page button using saved XPath
                    next_button = driver.find_element(By.XPATH, next_page_xpath)
                    if next_button.is_displayed() and next_button.is_enabled():
                        next_button.click()
                        page_count += 1
                        print(f"Navigating to page {page_count + 1}...")
                        time.sleep(5)  # Wait for new page to load
                    else:
                        print("Next page button is no longer clickable.")
                        break
                except Exception as e:
                    print(f"Error navigating to next page: {str(e)}")
                    break
            else:
                break
        
        # Create CSV filename with datetime stamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"scraped_data_{timestamp}.csv"
        
        # Write data to CSV file
        if all_data:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Get fieldnames from the first item's keys
                fieldnames = list(all_data[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header and data
                writer.writeheader()
                writer.writerows(all_data)
            
            print(f"\nData has been saved to: {csv_filename}")
        
        # Print summary of collected data
        print("\nCollected Data Summary:")
        print("-" * 50)
        print(f"Total items collected: {len(all_data)}")
        print(f"Pages scraped: {page_count + 1}")
        print(f"Data saved to CSV file: {csv_filename}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
