from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from fake_headers import Headers

LINK_PATTERN = r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*'

# Create your views here.
def scrape(request):

    context = {}

    if request.method == 'POST':
        website = request.POST.get("websiteAddress").strip()
        context["website"] = website

        if not website.startswith('https://'):
            website = f'https://{website}'

        if not re.match(LINK_PATTERN, website):
            context["error"] = "Invalid url"
        else:

            try:
                header = Headers(headers=True).generate()
                r = requests.get(website, headers=header)

                if r.status_code == 200:
                    data = {}

                    soup = BeautifulSoup(r.text, 'html.parser')
                    links = soup.find_all(name='a')

                    for link in links:
                        href = link.get('href')
                        if not href:
                            continue
                        if href[0] == '/':
                            href = urljoin(website, href)

                        title = link.get_text().strip()
                        if title == '':
                            title = 'None'

                        data[href] = title

                    if data:
                        context["results"] = data
                    else:
                        context["error"] = "No links found."
                else:
                    context["error"] = f"{r.status_code}"
            except Exception as e:
                context["error"] = "Url unreachable"
    return render(request, 'link_collector/main.html', context=context)