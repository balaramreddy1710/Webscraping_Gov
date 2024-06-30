import requests
from bs4 import BeautifulSoup
import pdfkit

# Function to generate HTML content for PDF
def generate_html_content(state_items, col_divs):
    html_content = """
    <html>
    <head><title>Election Results</title></head>
    <body>
    """
    
    # Extract information from state_items
    for item in state_items:
        if 'pc-wrap' in item.get('class', []):
            # Extract parliamentary constituency information
            num_constituencies = item.find('h1').text
            link = item.find('a').get('href') if item.find('a') else None
        
            html_content += f"<h2>Parliamentary Constituencies: {num_constituencies}</h2>"
            
            if link:
                # Send a GET request to the parliamentary constituency link
                response_link = requests.get(link)
                
                if response_link.status_code == 200:
                    # Parse the HTML content of the linked page
                    soup_link = BeautifulSoup(response_link.content, 'html.parser')

                    # Find the table within the content div
                    table = soup_link.find('table')

                    if table:
                        # Extract the table headers
                        headers = [header.text.strip() for header in table.find_all('th')]

                        # Extract the table rows
                        rows = []
                        for row in table.find_all('tr')[1:]:
                            cells = row.find_all('td')
                            row_data = [cell.text.strip() for cell in cells[:2]]  # Extracting first two cells
                            rows.append(row_data)

                        # Add table headers and rows to HTML content
                        headers_str = ' | '.join(headers[:2])
                        html_content += f"<p>{headers_str}</p>"
                        for row in rows:
                            html_content += f"<p>{' | '.join(row[:2])}</p>"

                else:
                    html_content += f"<p>Failed to retrieve parliamentary constituency link: {link}</p>"

        else:
            # Extract state-level constituency information
            state_name = item.find('h2').text.strip()
            num_constituencies = item.find('h1').text
            link = item.find('a').get('href') if item.find('a') else None

            html_content += f"<h2>{state_name}, State Constituencies: {num_constituencies}</h2>"
            
            if link:
                # Send a GET request to the state-level constituency link
                response_link = requests.get(link)
                
                if response_link.status_code == 200:
                    # Parse the HTML content of the linked page
                    soup_link = BeautifulSoup(response_link.content, 'html.parser')
                    
                    # Extract and add state-specific information to HTML content
                    page_title = soup_link.find('div', class_='page-title')
                    if page_title:
                        h1 = page_title.find('h1').text.strip() if page_title.find('h1') else ""
                        html_content += f"<h3>{h1}</h3>"

                    # Extract and add assembly constituency details to HTML content
                    state_items_link = soup_link.find_all('div', class_='item')
                    for item_link in state_items_link:
                        state_title = item_link.find('h2', class_='state-title').text.strip()
                        assembly_constituencies = item_link.find_all('span')[1].text.strip()
                        party_wrap = item_link.find('div', class_='partyWrap')
                        h6 = party_wrap.find('h6').text.strip() if party_wrap.find('h6') else ""
                        party_list_divs = party_wrap.find_all('div', class_='pr-row')

                        html_content += f"<h4>State: {state_title}</h4>"
                        html_content += f"<p>Assembly Constituencies: {assembly_constituencies}</p>"
                        html_content += f"<p>Status Title: {h6}</p>"
                        for div in party_list_divs:
                            party = div.find_all('div')[0].text.strip()
                            leading_won = div.find_all('div')[1].text.strip()
                            html_content += f"<p>Party: {party}, Leading/Won: {leading_won}</p>"

                    # Extract and add bye-election details to HTML content
                    bye_items_link = soup_link.find_all('div', class_='const-box')
                    for box in bye_items_link:
                        h3 = box.find('h3').text.strip()
                        h4 = box.find('h4').text.strip()
                        h2 = box.find('h2').text.strip()
                        h5 = box.find('h5').text.strip()
                        h6 = box.find('h6').text.strip()
                        
                        html_content += f"<h4>Constituency: {h3}</h4>"
                        html_content += f"<p>State: {h4}</p>"
                        html_content += f"<p>Status: {h2}</p>"
                        html_content += f"<p>Candidate: {h5}</p>"
                        html_content += f"<p>Party: {h6}</p>"
                        html_content += f"<br>"

                else:
                    html_content += f"<p>Failed to retrieve state-level constituency link: {link}</p>"

    # Extract information from col_divs for Arunachal Pradesh and Sikkim
    for div in col_divs[:2]:
        # Extract the link URL from the 'a' tag within the div
        link = div.find('a')['href'] if div.find('a') else None
        # Extract the text content within the 'a' tag
        text = div.find('a').text.strip() if div.find('a') else ""

        if link and text:
            html_content += f"<h2>State: {text}</h2>"

            # Send a GET request to the link
            response_link = requests.get(link)
            
            if response_link.status_code == 200:
                # Parse the HTML content of the linked page
                soup_link = BeautifulSoup(response_link.content, 'html.parser')

                # Extract and add h1 content to HTML content
                h1_content = soup_link.find('h1').text.strip()
                html_content += f"<h3>{h1_content}</h3>"

                party_wraps = soup_link.find_all('div', class_='partyWrap')

                for wrap in party_wraps:
                    # Extract and add the h6 content to HTML content
                    h6_content = wrap.find('h6').text.strip()
                    html_content += f"<h4>{h6_content}</h4>"

                    # Extract contents of pr-head and add to HTML content
                    pr_head = wrap.find('div', class_='pr-head')
                    if pr_head:
                        pr_head_divs = pr_head.find_all('div')
                        if len(pr_head_divs) == 2:
                            parties_heading = pr_head_divs[0].text.strip()
                            leading_won_heading = pr_head_divs[1].text.strip()
                            html_content += f"<p>{parties_heading} | {leading_won_heading}</p>"
                    else:
                        html_content += "<p>No pr-head found.</p>"

                    # Extract contents of pr-row and add to HTML content
                    pr_rows = wrap.find_all('div', class_='pr-row')
                    for row in pr_rows:
                        row_divs = row.find_all('div')
                        if len(row_divs) == 2:
                            party = row_divs[0].text.strip()
                            leading_won = row_divs[1].text.strip()
                            html_content += f"<p>Party: {party}, Leading/Won: {leading_won}</p>"
                    html_content += "<br>"
            else:
                html_content += f"<p>Failed to retrieve link: {link}</p>"
        
        else:
            html_content += "<p>No link found in the div.</p>"

    html_content += """
    </body>
    </html>
    """
    
    return html_content

# Send a GET request to the website
url = "https://results.eci.gov.in/"
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all div elements with the class "state-item"
    state_items = soup.find_all('div', class_='state-item') 

    # Find all div elements with the class "col-md-6 col-12" for Arunachal Pradesh and Sikkim
    col_divs = soup.find_all('div', class_='col-md-6 col-12')
    
    # Generate HTML content for PDF
    html_content = generate_html_content(state_items, col_divs)
    
    # Save HTML to a file
    with open('election_results.html', 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    # Convert HTML to PDF
    pdfkit.from_file('election_results.html', 'election_results.pdf')
    
    print("PDF generation completed.")
else:
    print(f"Failed to retrieve the website. Status code: {response.status_code}")
